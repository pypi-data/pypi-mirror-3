import sys
import pickle
from redis import Redis
from paxd.app.http import Request
from paxd.process import print_exc
from multiprocessing import Pipe, Process
from threading import Thread
from Queue import Empty
import uuid
from signal import signal, SIGINT
from paxd.app.msg import PRequest #, BaseResponse

def start_webui(name):
    WebUI(name).start()
    
class WebUI(object):
    def __init__(self, name):
        self.name = name
    
    def start(self):
        http_server = Thread(target=start_server, args=(self.name,))
        http_server.daemon = True
        http_server.start()
        # signal(SIGINT, sigint_handler)
        while True:
            try:
                http_server.join(0.5)
            except KeyboardInterrupt:
                print 'WebUI listener process exiting\n'
                sys.exit(-1)

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

shut_down = None

def start_server(name):
    redis = Redis('localhost')
    print 'SENDING REQUESTS TO', name
    class WebUIHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.bad_path():
                return self.do_404()
            
            request = Request(self.client_address, 
                                self.command, 
                                self.path, 
                                self.request_version, 
                                [])
            
            paxd_req = PRequest(redis, name, args=[request], timeout=30)
            try:
                response = paxd_req.send().get()
            except Exception, e:
                print e
                print e.traceback
                raise
            if not response:
                self.send_response(500)
                self.end_headers()
                self.wfile.write('TIMED OUT')
                return
            self.send_response(response.code)
            if response.content_type:
                self.send_header('Content-Type', response.content_type)
            if response.location:
                self.send_header('Location', response.location)
            self.end_headers()
            self.wfile.write(response.body)
        
        def bad_path(self):
            return 'favicon' in self.path
        
        def do_404(self):
            self.send_response(404)
            self.end_headers()
    
    server_class = HTTPServer
    handler_class = WebUIHandler
    server_address = ('', 22100)
    print 'listening on', server_address
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

def sigint_handler(num, frame):
    import sys
    print >>sys.stderr, 'EXITING'
    sys.exit(0)