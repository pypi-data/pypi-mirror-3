import os
import json
from redis import Redis
from functools import wraps
from paxd.app.msg import PRequest

def queue_name(queue, version):
    return '%s~%s' % (queue, version)

def make_task_file(path, broker_host=None, broker_port=None):
    with open(path) as f:
        data = json.loads(f.read())
    return make_task_conf(data, broker_host=broker_host, broker_port=broker_port)

def make_task_conf(conf, broker_host=None, broker_port=None):
    if broker_host is None:
        broker_host = os.environ['BROKER_HOST']
    if broker_port is None:
        broker_port = int(os.environ.get('BROKER_PORT', 6379))
    redis = Redis(broker_host, port=broker_port)
    class task(object):
        def __init__(self, queue):
            self._queue = queue
            self.queue = queue_name(queue, conf.get('version',''))
            self.conf = conf
        
        def __call__(self, fun):
            @wraps(fun)
            def delay(*args, **kwargs):
                if 'paxd_timeout' in kwargs:
                    paxd_timeout = kwargs['paxd_timeout']
                    del kwargs['paxd_timeout']
                else:
                    paxd_timeout = None
                return PRequest(redis, self.queue, args=args, kwds=kwargs, timeout=paxd_timeout).send()
            @wraps(fun)
            def run_offline(*args, **kwargs):
                if 'paxd_timeout' in kwargs:
                    paxd_timeout = kwargs['paxd_timeout']
                    del kwargs['paxd_timeout']
                else:
                    paxd_timeout = None
                return PRequest(redis, self.queue, args=args, kwds=kwargs, timeout=paxd_timeout, offline=True).send()
            fun.delay = delay
            fun.run_offline = run_offline
            fun.paxd_task = True
            fun.paxd_queue = self.queue
            return fun
    return task