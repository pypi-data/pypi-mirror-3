import traceback
import sys
import time
from threading import RLock, Thread
import uuid
from redis import Redis
from multiprocessing import Process, Pipe, cpu_count
from paxd.process import print_exc
from paxd.app.msg import BaseRequest, BaseResponse
from paxd.server import fsys

from smartpool.pool import Pool
from paxd.app.command import Command, init_process

class Application(object):
    DEFAULT_WORKERS = 2
    
    def __init__(self, name, data_root, env, packages, 
                    commands, num_workers, version, 
                    python_paths, group, system, state='stopped'):
        self.lock = RLock()
        self.data_root = data_root
        self.env = env
        self.group = group
        self.id = self.make_id(name=name, group=group, version=version)
        self.name = name
        self.num_workers = num_workers
        self.packages = packages
        self.python_paths = python_paths
        self.state = state
        self.system = system
        self.version = version
        self.exit = False
        
        # Commands
        self.commands = commands
        self.old_commands = []
        
        # Shared Pool
        self.pool = Pool(processes=self.num_workers, initializer=init_process, initargs=[self.abs_python_paths(), self.env])
        self.old_pools = []
        self.shared_pool = SharedPool(self, self.pool, self.old_pools)
        self.shared_pool.daemon = True
        for q, c in self.commands.items():
            c.set_shared_size(self.num_workers)
        
        # Cleanup thread
        self.cleaner = CleanUp(self)
        self.cleaner.daemon = True
        self.cleaner.start()
        
        # start if "started" state passed in
        if self.state == 'started':
            self.unpause()
    
    def quit(self):
        self.pause()
        self.resize(0)
        self.exit = True
        for q, c in self.commands.iteritems():
            c.quit()
    
    def pause(self):
        for queue, command in self.commands.iteritems():
            command.pause()
        self.state = 'stopped'
    
    def unpause(self):
        self.start()
        for queue, command in self.commands.iteritems():
            command.unpause()
        self.state = 'started'
    
    def resize(self, size):
        self.pool.resize(size)
        self.num_workers = size
        for q, c in self.commands.items():
            c.set_shared_size(self.num_workers)
    
    @property
    def trace(self):
        return self.pool.introspect()
    
    def __getitem__(self, queue):
        return self.commands[queue]
    
    def __contains__(self, queue):
        return queue in self.commands
    
    def abs_python_paths(self):
        return [fsys.join(self.data_root, p) for p in self.python_paths]
    
    def start(self):
        for queue, command in self.commands.iteritems():
            command.start()
        if not self.shared_pool.is_alive():
            self.shared_pool.start()
        if not self.cleaner.is_alive():
            self.cleaner.start()
    
    def stop(self):
        if self.system:
            return
    
    @staticmethod
    def make_id(**kwargs):
        return (kwargs['name'], kwargs['group'], kwargs['version'])
    
    @classmethod
    def from_conf(cls, path, conf, instance_id, system=False, group=None):
        app_args = {
            'name' : conf['name'],
            'group' : conf.get('group', 'default'),
            'data_root' : path,
            'env' : conf.get('environment', {}),
            'packages' : conf.get('required_packages',[]),
            'python_paths' : conf.get('python_paths',[]),
            'num_workers' : 2, # TODO, configurable
            'version' : conf.get('version',''),
            'system' : system,
        }
        
        if group != None:
            app_args['group'] = group
        
        if 'state' in conf:
            app_args['state'] = conf['state']
        
        app_args['commands'] = {}
        for queue, c in conf.get('commands', {}).iteritems():
            com = Command.from_conf(queue, c, path, app_args['python_paths'], app_args['env'], instance_id, 
                    shared_size=app_args['num_workers'], version=app_args['version'])
            app_args['commands'][queue] = com
        
        return Application(**app_args)
    
    def update(self, path, conf, instance_id):
        '''
            create new pool with new parameters
        '''
        assert self.version == conf.get('version',''), (self.version, conf.get('version',''))
        assert self.name == conf.get('name'), (self.name, conf.get('name'))
        
        final_state = self.json_info
        
        self.data_root = path
        self.env = conf.get('environment', {})
        self.packages = conf.get('required_packages',[])
        self.python_paths = conf.get('python_paths', [])
        
        # commands
        old_commands = self.commands
        
        self.commands = {}
        for queue, c in conf.get('commands', {}).iteritems():
            com = Command.from_conf(queue, c, self.data_root, self.python_paths, self.env, instance_id, 
                    shared_size=self.DEFAULT_WORKERS, version=self.version)
            self.commands[queue] = com
        for q, c in old_commands.iteritems():
            if q not in self.commands:
                continue
            if not c.stopped:
                self.commands[q].unpause()
        self.cleaner.add_commands(old_commands)
        
        if self.state == 'started':
            self.unpause()
        
        # Shared Pool
        with self.lock:
            self.cleaner.add_pool(self.pool)
            self.pool = Pool(processes=self.num_workers, initializer=init_process, initargs=[self.abs_python_paths(), self.env])
        
        for q, c in self.commands.items():
            c.set_shared_size(self.num_workers)
        
        # start if "started" state passed in
        if self.state == 'started':
            self.unpause()

        
    
    def json_info(self, detailed=False):
        data = {
            'data_root' : self.data_root,
            'environment' : self.env,
            'group' : self.group,
            # 'id' : self.id,
            'name' : self.name,
            'num_workers' : self.num_workers,
            'packages' : self.packages,
            'python_paths' : self.python_paths,
            'state' : self.state,
            'system' : self.system,
            'version' : self.version,
            'commands' : {},
        }
        for q, c in self.commands.iteritems():
            data['commands'][q] = c.json_info(detailed=detailed)
        return data
    
    def __repr__(self):
        return 'Application(name="%s", group="%s", version="%s")' % (self.name, self.group, self.version)

class CleanUp(Thread):
    def __init__(self, app):
        Thread.__init__(self)
        self.app = app
        self.lock = RLock()
        self.old_pools = []
        self.old_commands = []
    
    def add_pool(self, pool):
        pool.close()
        with self.lock:
            self.old_pools.append(pool)
    
    def add_commands(self, commands):
        for q, c in commands.iteritems():
            c.quit()
        with self.lock:
            self.old_commands.append(commands)
    
    def run(self):
        while True:
            with print_exc:
                if self.app.exit:
                    break
                self.event_loop()
    
    def event_loop(self):
        with self.lock:
            sleep = len(self.old_pools) == 0 and len(self.old_commands) == 0
        if sleep:
            time.sleep(2)
            return
        
        with self.lock:
            new_pools = []
            for p in self.old_pools:
                for i in p.introspect():
                    if i['state'] != 'EXITED':
                        new_pools.append(p)
                        break
            self.old_pools = new_pools
            new_commands = []
            # all old sets of commands
            for c_map in self.old_commands:
                finished = []
                # a single set of commands
                for q, c in c_map.iteritems():
                    for i in c.trace:
                        if i['state'] != 'EXITED':
                            break
                    else:
                        finished.append(q)
                for q in finished:
                    del c_map[q]
                if len(c_map) > 0:
                    new_commands.append(c_map)
            self.old_commands = new_commands

class SharedPool(Thread):
    def __init__(self, app, pool, old_pools, *args, **kwargs):
        Thread.__init__(self, *args, **kwargs)
        self.app = app
        self.pool = app.pool
        self.old_pools = old_pools
        self.pending = []
        self.lock = RLock()
    
    def full(self):
        with self.lock:
            self.pending = [x for x in self.pending if not x['async'].ready()]
            return len(self.pending) > self.app.num_workers
    
    def run(self):
        while True:
            with print_exc:
                if self.app.exit:
                    break
                self.event_loop()
    
    def event_loop(self):
        if self.full():
            time.sleep(0.1)
            return
        for queue, command in self.app.commands.items():
            if command.stopped:
                continue
            if command.runner.shared_ready():
                with self.lock:
                    res = command.runner.run_fun(pool=self.pool, pool_type='shared')
                    self.pending.append(res)
                return
        else:
            time.sleep(0.1)