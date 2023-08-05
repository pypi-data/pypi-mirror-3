import uuid
import traceback
import json
import pickle
from paxd.app.http import Response
from paxd.app.msg import PRequest
from redis import Redis
from paxd.webuiapp import html

################################
#  Web UI App/Routing
################################

def webui_app(request):
    try:
        response = handle_request(request)
    except:
        response = Response(500, 'Server Error %s' % traceback.format_exc())
    return response


def route_mapping():
    return (
        ('/jquery.js', jquery),
        ('/load', load_app),
        ('/update', update_app),
        ('/unload', unload_app),
        ('/failed/remove', remove_failed),
        ('/failed/remove-all', remove_all_failed),
        ('/failed/requeue', requeue_failed),
        ('/failed/requeue-all', requeue_all_failed),
        ('/failed', get_failed),
        ('/pause', pause_app),
        ('/unpause', unpause_app),
        ('/trace_command', trace_command),
        ('/trace_app', trace_app),
        ('/', get_apps),
    )

def route(request):
    for path, fun in route_mapping():
        if request.path.partition('?')[0] == path:
            return fun
    return None

def handle_request(request):
    fun = route(request)
    if fun is None:
        return Response(404, 'Not Found')
    try:
        return Response(200, fun(request), content_type='text/html')
    except Forward, f:
        return Response(301, '', location=f.location)
    except NoResponse:
        return Response(500, 'No Response from controller')

################################
#  Web UI Actions
################################

controller_queue = '_paxd.controller'
def get_apps(request):
    redis = Redis('localhost')
    req = PRequest(redis, controller_queue, {
            'command' : 'APPLIST'
        }, timeout=2)
    promise = req.send()
    resp = promise.get()
    if not resp:
        return 'NO RESPONSE'
    
    return html.render('applications.html', resp)
    # return html.header() + html.applications(resp) + html.footer()

def jquery(request):
    import os
    from paxd import PROJECT_PATH
    from mako.lookup import TemplateLookup
    
    path = os.path.join(PROJECT_PATH, 'paxd/webuiapp/templates/jquery-1.5.min.js')
    with open(path) as f:
        return f.read()

def load_app(request):
    redis = Redis('localhost')
    
    group = request.GET.get('group')
    
    conf = request.GET.get('config_file')
    if not conf:
        conf = '/paxd.conf'
    
    promise = PRequest(redis, controller_queue, {
        'command':'LOAD_APP',
        'url' : request.GET['url'],
        'group' : group, 
        'config_file' : conf, 
    }, timeout=60)

    resp = promise.send().get()
    if not resp:
        return 'NO RESPONSE'
    raise Forward('/')

def update_app(request):
    redis = Redis('localhost')
    
    group = request.GET.get('group')
    
    conf = request.GET.get('config_file')
    if not conf:
        conf = '/paxd.conf'
    
    promise = PRequest(redis, controller_queue, {
        'command':'UPDATE_APP',
        'name' : request.GET['name'], 
        'version' : request.GET['version'], 
        'url' : request.GET['url'],
        'group' : group, 
        'config_file' : conf, 
    }, timeout=60)
    resp = promise.send().get()
    if not resp:
        return 'NO RESPONSE'
    raise Forward('/')


def requeue_failed(request):
    redis = Redis('localhost')
    promise = PRequest(redis, controller_queue, {
        'name' : request.GET['name'], 
        'group' : request.GET['group'], 
        'version' : request.GET['version'],
        'queue' : request.GET['queue'], 
        'command' : 'REQUEUE_FAILED',
        'fail_id' : request.GET['fail_id'], 
    }, timeout=4)
    res = promise.send().get()
    if res is None:
        raise NoResponse()
    return json.dumps(res)

def remove_failed(request):
    redis = Redis('localhost')
    promise = PRequest(redis, controller_queue, {
        'name' : request.GET['name'], 
        'group' : request.GET['group'], 
        'version' : request.GET['version'], 
        'queue' : request.GET['queue'], 
        'command' : 'REMOVE_FAILED',
        'fail_id' : request.GET['fail_id'], 
    }, timeout=4)
    res = promise.send().get()
    if res is None:
        raise NoResponse()
    return json.dumps(res)

def get_failed(request):
    resp = command_action(request, 'GET_FAILED')
    res = html.render('failed.html', resp)
    return res

def unload_app(request):
    resp = app_action(request, 'UNLOAD_APP')
    return json.dumps(resp)

def pause_app(request):
    resp = command_action(request, 'PAUSE')
    return json.dumps(resp)

def unpause_app(request):
    resp = command_action(request, 'UNPAUSE')
    return json.dumps(resp)

def remove_all_failed(request):
    resp = command_action(request, 'REMOVE_ALL_FAILED')
    return json.dumps(resp)

def requeue_all_failed(request):
    resp = command_action(request, 'REQUEUE_ALL_FAILED')
    return json.dumps(resp)


def trace_app(request):
    resp = app_action(request, 'TRACE_APP')
    return html.render('traces.html', resp)

def trace_command(request):
    resp = command_action(request, 'TRACE_COMMAND')
    return html.render('traces.html', resp)

def app_action(request, command_name):
    redis = Redis('localhost')
    promise = PRequest(redis, controller_queue, {
        'command' : command_name,
        'name' : request.GET['name'], 
        'group' : request.GET['group'], 
        'version' : request.GET['version'], 
        # 'queue' : request.GET['queue'], 
    }, timeout=4)
    res = promise.send().get()
    if res is None:
        raise NoResponse()
    return res

def command_action(request, command_name):
    redis = Redis('localhost')
    promise = PRequest(redis, controller_queue, {
        'command' : command_name,
        'name' : request.GET['name'], 
        'group' : request.GET['group'], 
        'version' : request.GET['version'], 
        'queue' : request.GET['queue'], 
    }, timeout=4)
    res = promise.send().get()
    if res is None:
        raise NoResponse()
    return res
    

def id_app(request, command_name):
    redis = Redis('localhost')
    promise = PRequest(redis, controller_queue, {
        'command' : command_name,
        'id' : request.GET['id'], 
    }, timeout=4)
    res = promise.send().get()
    if res is None:
        raise NoResponse()
    return res

class NoResponse(Exception):
    pass

class Forward(Exception):
    def __init__(self, location):
        self.location = location