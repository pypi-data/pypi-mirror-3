import traceback
import importlib
from paxd.app.msg import BaseRequest, BaseResponse
from paxd.process import print_exc
from paxd.server import fsys
import time
from smartpool.pool import Pool
from Queue import Queue, Empty
from threading import RLock, Thread
from redis import Redis
from multiprocessing import Process, Pipe, cpu_count

WORKER_FUNCTIONS = {}
def worker_fun(entry, args, kwds, format):
    import json
    import cPickle as pickle
    if format == 'pickle':
        deserialize = pickle.loads
    else:
        deserialize = json.loads
    try:
        if entry not in WORKER_FUNCTIONS:
            module, _, fun = entry.rpartition(':')
            module = importlib.import_module(module)
            wfun = module
            for name in fun.split('.'):
                wfun = getattr(wfun, name)
            WORKER_FUNCTIONS[entry] = wfun
        args = deserialize(args)
        kwds = deserialize(kwds)
        return WORKER_FUNCTIONS[entry](*args, **kwds)
    except KeyboardInterrupt:
        time.sleep(0.3)
        raise
    except Exception, e:
        e.traceback = traceback.format_exc()
        raise e

def init_process(paths, env):
    import sys
    import os
    for p in reversed(paths):
        sys.path.insert(0, p)
    for k, v in env.iteritems():
        os.environ[k] = v

class Command(object):
    def __init__(self, queue, entry, base_path, python_paths, environment, instance_id, shared_size, state='stopped', num_processes=max(cpu_count(), 2), version=''):
        self.entry = entry
        self.queue = queue
        self.base_path = base_path
        self.python_paths = python_paths
        self.environment = environment
        self.instance_id = instance_id
        self.redis = Redis('localhost')
        self.lock = RLock()
        
        # computed fields
        self.abs_python_paths = [fsys.join(base_path, p) for p in python_paths]
        
        self.queue_name = '%s~%s' % (queue, version)
        self.active_queue = '%s:active' % self.queue_name
        self.failed_queue = '%s:failed' % self.queue_name
        self.success_count = '%s:success' % self.queue_name
        self.pending_queue = '%s:pending' % self.queue_name
        
        # state
        self.exit = False
        self.state = state
        self.num_processes = num_processes
        self.pool = Pool(processes=self.num_processes, initializer=init_process, initargs=[self.abs_python_paths, environment])
        self.initialized = False
        self.shared_size = shared_size
        
        # Input
        self.in_queue = TaskQueue(self)
        self.in_queue.daemon = True
        
        # Output
        self.out_writer = ResultWriter(self)
        self.out_writer.daemon = True
        
        # Run
        self.runner = TaskRunner(self)
        self.runner.daemon = True
        if self.state == 'started':
            self.unpause()
    
    def quit(self):
        self.pause()
        self.exit = True
        self.resize(0)
        self.pool.close()
    
    def kill(self):
        self.pause()
        self.exit = True
        self.resize(0)
        self.pool.terminate()
    
    def set_shared_size(self, size):
        self.shared_size = size
    
    def pause(self):
        self.state = 'stopped'
    
    def unpause(self):
        self.start()
        self.state = 'started'
    
    @property
    def stopped(self):
        return self.state == 'stopped'
    
    @property
    def trace(self):
        return self.pool.introspect()
    
    def resize(self, size):
        self.pool.resize(size)
        self.num_processes = size
    
    def start(self):
        if self.initialized:
            return
        with print_exc:
            self.out_writer.clear_old()
        if not self.in_queue.is_alive():
            self.in_queue.start()
        if not self.runner.is_alive():
            self.runner.start()
        if not self.out_writer.is_alive():
            self.out_writer.start()
        self.initialized = True

    def json_info(self, detailed=False):
        info = {
            'entry' : self.entry,
            'queue' : self.queue,
            'queue_full' : self.queue_name,
            'state' : self.state,
            'processes' : self.num_processes,
        }
        
        success = self.redis.get(self.success_count)
        if success is None:
            success = 0
        info.update(** {
            'queued' : self.redis.llen(self.queue_name),
            'active' : self.redis.hlen(self.active_queue)+self.redis.llen(self.pending_queue),
            'failed' : self.redis.llen(self.failed_queue),
            'success' : success,
        })
        return info

    
    @classmethod
    def from_conf(self, queue, data, base_path, paths, environment, instance_id, shared_size, version):
        c_args = {
            'entry' : data.get('entry', queue),
            'queue' : queue,
            'python_paths' : paths,
            'base_path' : base_path,
            'environment' : environment,
            'instance_id' : instance_id,
            'shared_size' : shared_size,
            'version' : version,
        }
        if 'state' in data:
            c_args['state'] = data['state']
        
        if 'processes' in data:
            c_args['num_processes'] = data['processes']
        return Command(**c_args)
    
    @property
    def trace(self):
        return self.pool.introspect()
    
    def poll(self):
        with self.lock:
            return len(self.pending) == 0 and self.exit
    
    @property
    def failed_items(self):
        import json
        items = []
        for x in self.redis.lrange(self.failed_queue, 0, -1):
            items.append(json.loads(x[5:]))
        return items
    
    @property
    def failed_with_raw(self):
        import json
        for x in self.redis.lrange(self.failed_queue, 0, -1):
            yield (json.loads(x[5:]), x)
    
    def requeue_all(self):
        pipe = self.redis.pipeline(transaction=True)
        for item, raw in self.failed_with_raw:
            BaseRequest.send_raw(self.redis, self.queue_name, item['request'])
            pipe.lrem(self.failed_queue, raw)
        pipe.execute()
        
    
    def requeue_failed(self, id):
        for item, raw in self.failed_with_raw:
            if item['id'] != id:
                continue
            pipe = self.redis.pipeline(transaction=True)
            BaseRequest.send_raw(self.redis, self.queue_name, item['request'])
            pipe.lrem(self.failed_queue, raw)
            pipe.execute()
    
    def remove_all_failed(self):
        self.redis.delete(self.failed_queue)
    
    def remove_failed(self, id):
        for item, raw in self.failed_with_raw:
            if item['id'] != id:
                continue
            self.redis.lrem(self.failed_queue, raw)

class TaskQueue(Thread):
    def __init__(self, command):
        Thread.__init__(self)
        self.command = command
        self.redis = Redis('localhost')
        self.queue = Queue()
    
    def get(self, timeout=None):
        try:
            return self.queue.get(block=True, timeout=timeout)
        except Empty:
            return None
    
    def qsize(self):
        return self.queue.qsize()
    
    def run(self):
        while True:
            if self.command.exit and self.queue.qsize() == 0:
                break
            if self.command.stopped:
                time.sleep(0.5)
                continue
            if self.queue.qsize() >= self.command.num_processes + self.command.shared_size:
                time.sleep(0.05)
                continue
            self.enqueue()
    
    def enqueue(self):
        item = self.redis.brpoplpush(self.command.queue_name, self.command.pending_queue, 1)
        if item is None:
            return
        pipe = self.redis.pipeline(transaction=True)
        pipe.hset(self.command.active_queue, item, self.command.instance_id)
        pipe.lrem(self.command.pending_queue, item, 1)
        pipe.execute()
        self.queue.put(item)
    


class ResultWriter(Thread):
    daemon = True
    def __init__(self, command):
        Thread.__init__(self)
        self.command = command
        self.lock = RLock()
        self.pending = []
        self.redis = Redis('localhost')
    
    def add_pending(self, result):
        with self.lock:
            self.pending.append(result)
        return result
    
    def full(self, pool='private', max=None):
        if max is None:
            max = self.command.num_processes
        with self.lock:
            count = len([x for x in self.pending if x['pool'] == pool])
        return count > max
    
    def shared_full(self):
        return self.full(pool='shared', max=self.command.shared_size)
    
    def run(self):
        while True:
            with print_exc:
                try:
                    if not self.check_pending():
                        time.sleep(0.1)
                except Exit:
                    break
        # clear out anything remaining before exiting
        self.clear_old()
    
    def check_pending(self):
        with self.lock:
            if self.command.exit and len(self.pending) == 0:
                raise Exit()
            for p in self.pending:
                if not p['async'].ready():
                    continue
                break
            else:
                return False
            self.pending = [x for x in self.pending if x['request'].response_queue != p['request'].response_queue]
        
        try:
            request = p['request']
            ret = p['async'].get()
            response = request.response_class(request.response_queue, 'SUCCESS', ret)
            error = False
        except Exception, e:
            response = request.response_class(request.response_queue, 'ERROR', None)
            response.set_exception(e)
            error = True
        self.respond(request, response, error=error)
        return True
    
    def respond(self, request, response, error=False, retry=True):
        if not request.response_queue:
            return
        try:
            pipe = self.redis.pipeline(transaction=True)
            if not request.offline:
                pipe.lpush(request.response_queue, response.serialize_resp())
                pipe.expire(request.response_queue, request.timeout)
            if error:
                pipe.lpush(self.command.failed_queue, response.serialize_failed_resp(request))
            else:
                pipe.incr(self.command.success_count)
            pipe.hdel(self.command.active_queue, request.raw)
            pipe.execute()
        except KeyboardInterrupt:
            if retry:
                self.respond(request, response, error=error, retry=False)
    
    def clear_old(self):
        def handle_old(request, del_cmd):
            request_parsed = BaseRequest.from_serialized(request)
            response = request_parsed.response_class(request_parsed.response_queue, 'INCOMPLETE', None)
            pipe = self.redis.pipeline(transaction=True)
            pipe.lpush(self.command.failed_queue, response.serialize_failed_resp(request_parsed))
            del_cmd(pipe, request)
            pipe.execute()
        with self.lock:
            for request, v in self.redis.hgetall(self.command.active_queue).iteritems():
                if v != self.command.instance_id:
                    continue
                handle_old(request, lambda pipe, k : pipe.hdel(self.command.active_queue, k))
            # this could /technically/ delete something pending, but the pending 
            # queue is used for a very short period of time and if the system is 
            # up long enough to delete the pending item it should be OK
            for request in self.redis.lrange(self.command.pending_queue, 0, -1):
                handle_old(request, lambda pipe, k : pipe.lrem(self.command.pending_queue, k, 1))


class TaskRunner(Thread):
    def __init__(self, command):
        Thread.__init__(self)
        self.command = command
        self.input = self.command.in_queue
        self.output = self.command.out_writer
    
    def run(self):
        while True:
            if self.command.exit:
                break
            if self.command.stopped or self.command.num_processes == 0:
                time.sleep(0.5)
                continue
            with print_exc:
                if self.ready():
                    self.run_fun()
                else:
                    time.sleep(0.05)
    
    def ready(self):
        stopped = self.command.stopped
        full = self.output.full()
        queue_empty = self.input.qsize() == 0
        return not stopped and not full and not queue_empty
    
    def shared_ready(self):
        stopped = self.command.stopped
        full = self.output.shared_full()
        queue_empty = self.input.qsize() == 0
        return not stopped and not full and not queue_empty
    
    def run_fun(self, pool=None, pool_type='private'):
        if pool is None:
            pool = self.command.pool
        
        # Get item
        request = self.input.get()
        if request is None:
            return
        request = BaseRequest.from_serialized(request)
        
        # run fun
        kwds = {
            'entry' : self.command.entry,
            'args' : request.args,
            'kwds' : request.kwds,
            'format' : request.format,
        }
        # args = [self.application.entry]
        # args.extend([a for a in request.args])
        return self.output.add_pending({
            'async' : pool.apply_async(worker_fun, kwds=kwds),
            'request' : request,
            'pool' : pool_type,
        })

class Exit(Exception):
    pass



