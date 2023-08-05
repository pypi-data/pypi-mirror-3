import time
from datetime import datetime
from multiprocessing import Process, Pipe, Queue
from Queue import Empty
from signal import signal, SIGINT, SIGKILL, SIGTERM
from threading import RLock, Thread
import os
import sys
import pickle
import json
from redis import Redis

import threading
from paxd.app.application import Application
from paxd.process import print_exc
from paxd.server.webserver import start_webui
from paxd.server import fsys
from paxd.app.msg import BaseRequest, BaseResponse
from paxd import PROJECT_PATH, VERSION

class Controller(object):
    command_queue = '_paxd.controller'
    webui_queue = '_paxd.web_ui'
    def __init__(self, instance_id):
        self.instance_id = instance_id
        self.lock = RLock()
        self.processes = []
        self.threads = []
        self.applications = {}
        self.initialized = False
        self.application_history = []
    
    def run(self):
        try:
            print 'STARTING UP CONTROLLER.  pid: ', os.getpid()
            # Internal Applications
            self.start_process(start_webui, '%s~%s' % (self.webui_queue, VERSION))
            
            # Start "apps"
            self.configure()
            
            # useful for debugigng, prints out stack traces every 4 seconds
            # for things which aren't sleeping or blocking on locks/network
            # self.introspector = Introspector()
            # self.introspector.daemon = True
            # self.introspector.start()
            
            # Wait For Commands
            self.handle_commands()
        except Exception, e:
            print 'TERMINATING', e
            import sys
            for process in self.processes:
                process.terminate()
            raise
    
    def configure(self):
        if self.initialized:
            return
        redis = Redis('localhost')
        config = redis.hget('_paxd.controllers.config', self.instance_id)
        self.load_web_ui().start()
        if not config:
            return
        
        config = json.loads(config)
        for app in config['applications']:
            if app['name'] == 'Pax Daemonica':
                continue
            print 'LOADING', app['name']
            
            app = Application.from_conf(app['data_root'], app, self.instance_id)
            assert app.id not in self.applications
            self.applications[app.id] = app
        
        for time, app in config.get('application_history',[]):
            print 'CREATING HISTORIC ENTRY FOR', app['name']
            app = Application.from_conf(app['data_root'], app, self.instance_id)
            self.application_history.append((time, app))

        
        self.initialized = True
    
    def handle_commands(self):
        thread = Thread(target=command_thread, args=(self,))
        thread.daemon = True
        thread.start()
        self.threads.append(thread)
        while True:
            try:
                thread.join(60)
            except KeyboardInterrupt:
                print 'CONTROLLER EXITING'
                sys.exit(0)
    
    def load_web_ui(self):
        app = Application.from_conf(PROJECT_PATH, WEBUI_CONF, self.instance_id, system=True)
        if app.id not in self.applications:
            self.applications[app.id] = app
        self.applications[app.id].unpause()
        return self.applications[app.id]
        
    def load_app(self, url, config_file='/paxd.conf', group=None):
        path = self.setup_workspace(url)
        data = self.load_config(path, config_file)
        app = Application.from_conf(path, data, self.instance_id, group=group)
        if app.id in self.applications:
            raise Exception('App ID already exists')
        self.applications[app.id] = app
        return app
    
    def update_app(self, name, group, version, url, config_file):
        id = Application.make_id(name=name, group=group, version=version)
        assert id in self.applications
        path = self.setup_workspace(url)
        data = self.load_config(path, config_file)
        app = self.applications[id]
        app.update(path, data, self.instance_id)
        return app
    
    def start_app(self, name, group='default', version=''):
        id = Application.make_id(name=name, group=group, version=version)
        assert id in self.applications
        self.applications[id].start()
    
    def start_process(self, fun, name):
        process = Process(target=fun, args=(name,))
        process.start()
        print 'STARTING INTERNAL PROCESS', name, process.pid
        self.processes.append(process)
    
    def setup_workspace(self, url):
        return fsys.download_temp(url)
    
    def load_config(self, path, config_file):
        conf = fsys.join(path, config_file)
        with open(conf) as f:
            data = f.read()
            return json.loads(data)


def command_thread(controller):
    redis = Redis('localhost')
    while True:
        with print_exc:
            _, value = redis.blpop(controller.command_queue)
            request = BaseRequest.from_serialized(value)
            
            resp_data = handle_command(controller, redis, request.deserialize(request.args))
            
            response = request.response_class(request.response_queue, 'SUCCESS', resp_data)
            pipe = redis.pipeline(transaction=True)
            q = request.response_queue
            ser = response.serialize_resp()
            pipe.lpush(q, ser)
            pipe.expire(request.response_queue, request.timeout)
            # pipe.lrem(self.active_queue, 1, request.raw)
            pipe.execute()
            save_settings(redis, controller)

def save_settings(redis, controller):
    pipe = redis.pipeline(transaction=True)
    apps = []
    with controller.lock:
        for id, app in controller.applications.iteritems():
            apps.append(app.json_info())
    data = {
        'applications' : apps,
        'application_history' : [(t, a.json_info()) for t, a in controller.application_history]
    }
    # import pprint
    # pprint.pprint(data)
    redis.hset('_paxd.controllers.config', controller.instance_id, json.dumps(data))

def handle_command(controller, redis, rdata):
    try:
        command = rdata['command']
        if command == 'APPLIST':
            return handle_list(controller, redis, rdata)
        elif command == 'LOAD_APP':
            return handle_load_app(controller, redis, rdata)
        elif command == 'UPDATE_APP':
            return handle_update_app(controller, redis, rdata)
        elif command == 'LOAD_AUTO':
            return handle_load_auto(controller, redis, rdata)
        elif command == 'UNLOAD_APP':
            return handle_unload(controller, redis, rdata)
        elif command == 'PAUSE' or command == 'UNPAUSE':
            return handle_pause_unpause(controller, redis, rdata)
        elif command == 'REQUEUE_ALL_FAILED':
            return handle_requeue_all_failed(controller, redis, rdata)
        elif command == 'REMOVE_ALL_FAILED':
            return handle_remove_all_failed(controller, redis, rdata)
        elif command == 'TRACE_COMMAND':
            return handle_trace_command(controller, redis, rdata)
        elif command == 'TRACE_APP':
            return handle_trace_app(controller, redis, rdata)
        elif command == 'GET_FAILED':
            return handle_get_failed(controller, redis, rdata)
        elif command == 'REQUEUE_FAILED':
            return handle_requeue_failed(controller, redis, rdata)
        elif command == 'REMOVE_FAILED':
            return handle_remove_failed(controller, redis, rdata)
        return 'BAD COMMAND'
    except Exception, e:
        import traceback
        print e
        traceback.print_exc()
        return { 'status' : 'ERROR', 'exception' : e }

def handle_list(controller, redis, rdata):
    ret = []
    with controller.lock:
        for id, app in controller.applications.iteritems():
            json_info = app.json_info(detailed=True)
            ret.append(json_info)
        
        historic = []
        for time, app in controller.application_history:
            info = app.json_info()
            info['terminated'] = time
            historic.append(info)
    
    return {'applications' : ret, 'history' : historic }

def handle_trace_app(controller, redis, rdata):
    app = get_app(controller, rdata)
    if app is None:
        return NO_APP_MSG
    return { 'status' : 'SUCCESS', 'traces' : app.trace, 'app' : app.json_info() }

def handle_trace_command(controller, redis, rdata):
    app = get_app(controller, rdata)
    command = get_command(controller, app, rdata)
    if app is None or command is None:
        return NO_APP_MSG
    return { 'status' : 'SUCCESS', 'traces' : command.trace, 'app' : app.json_info() }

def handle_requeue_failed(controller, redis, rdata):
    app = get_app(controller, rdata)
    command = get_command(controller, app, rdata)
    if app is None or command is None:
        return NO_APP_MSG
    res = command.requeue_failed(rdata['fail_id'])
    return { 'status' : 'SUCCESS' }

def handle_remove_failed(controller, redis, rdata):
    app = get_app(controller, rdata)
    command = get_command(controller, app, rdata)
    if app is None or command is None:
        return NO_APP_MSG
    res = command.remove_failed(rdata['fail_id'])
    return { 'status' : 'SUCCESS' }

def handle_get_failed(controller, redis, rdata):
    app = get_app(controller, rdata)
    command = get_command(controller, app, rdata)
    if app is None or command is None:
        return NO_APP_MSG
    return { 'status' : 'SUCCESS', 'failed' : command.failed_items, 'app' : app.json_info(), 'command' : command.json_info() }

def handle_load_app(controller, redis, rdata):
    app = controller.load_app(rdata['url'], config_file=rdata['config_file'], group=rdata.get('group'))
    return { 'status' : 'SUCCESS', 'apps' : [app.json_info()] }

def handle_update_app(controller, redis, rdata):
    app = controller.update_app(name=rdata['name'],
                                group=rdata['group'],
                                version=rdata['version'],
                                url=rdata['url'],
                                config_file=rdata['config_file'])
    return { 'status' : 'SUCCESS', 'apps' : [app.json_info()] }

def handle_unload(controller, redis, rdata):
    with controller.lock:
        app = get_app(controller, rdata)
        if app is None:
            return { 'status' : 'FAILURE', 'reason' : 'NO SUCH APP ID' }
        app.quit()
        controller.application_history.append((datetime.utcnow().ctime(), app))
        del controller.applications[app.id]
        return { 'status' : 'SUCCESS', 'app' : app.json_info() }

def handle_requeue_all_failed(controller, redis, rdata):
    app = get_app(controller, rdata)
    command = get_command(controller, app, rdata)
    if app is None or command is None:
        return NO_APP_MSG
    command.requeue_all()
    return { 'status' : 'SUCCESS', 'app' : app.json_info() }
    
def handle_remove_all_failed(controller, redis, rdata):
    app = get_app(controller, rdata)
    command = get_command(controller, app, rdata)
    if app is None or command is None:
        return NO_APP_MSG
    command.remove_all_failed()
    return { 'status' : 'SUCCESS', 'app' : app.json_info() }

def handle_pause_unpause(controller, redis, rdata):
    app = get_app(controller, rdata)
    command = get_command(controller, app, rdata)
    if app is None or command is None:
        return NO_APP_MSG
    if rdata['command'] == 'UNPAUSE':
        command.unpause()
    else:
        command.pause()
    return { 'status' : 'SUCCESS', 'app' : app.json_info() }

NO_APP_MSG = { 'status' : 'FAILURE', 'reason' : 'NO SUCH APP ID' }

def get_command(controller, app, rdata):
    if rdata['queue'] in app:
        return app[rdata['queue']]
    return None

def get_app(controller, rdata):
    id = Application.make_id(name=rdata['name'], group=rdata['group'], version=rdata['version'])
    with controller.lock:
        if id in controller.applications:
            return controller.applications[id]
    return None
    

WEBUI_CONF = {
    "name" : "Pax Daemonica", 
    "group" : "default", 
    "python_paths" : ["/"], 
    "required_packages" : [] ,
    "commands" : {
        "_paxd.web_ui" : {
            "entry" : "paxd.webuiapp.webui:webui_app"
        },
    },
    "environment" : {},
    "version" : VERSION
}


class Introspector(threading.Thread):
    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        
    def run(self):
        print 'start'
        while True:
            time.sleep(3)
            self.introspect()
            # break
    
    def introspect(self):
        print 'introspect'
        import traceback
        current_thread = threading.current_thread().ident
        try:
            import os
            stack = None
            res = []
            print '*' * 160 * 2
            for id, stack in sys._current_frames().items():
                data = ''.join(traceback.format_stack(stack))
                if 'task = get()' in data:
                    continue
                if 'waiter.acquire()' in data:
                    continue
                if 'time.sleep(' in data:
                    continue
                if 'data = self._sock.recv(self._rbufsize)' in data:
                    continue
                if 'traceback.format_stack(stack)' in data:
                    continue
                if '_sleep(delay' in data:
                    continue
                
                print '-' * 80
                print id
                print data
        finally:
            del stack
