from datetime import datetime
import sys
import traceback
import uuid
import cPickle as pickle
import json

class Promise(object):
    def __init__(self, redis, req_queue, queue, loader, timeout):
        self.queue = queue
        self.req_queue = req_queue
        self.loader = loader
        self.redis = redis
        self.timeout = timeout
        
    def poll(self):
        return self.redis.llen(self.queue) == 0
    
    def get(self, timeout=0):
        ''' Get the response.  Automatically raise an exception if there was
            an error, return the data otherwise.  Waits for the timeout length
            of the original request unless the timeout parameter is passed'''
        if self.timeout:
            timeout = self.timeout
        response = self.get_response(timeout=timeout)
        if response is None:
            return response
        if response.status == 'ERROR':
            e = Exception(response.error_value)
            e.traceback = response.traceback
            e.type = response.error_type
            raise e
        return response.data
    
    def get_response(self, timeout=0):
        resp = self.redis.brpop(self.queue, timeout=timeout)
        if not resp:
            return None
        _, value = resp
        return self.loader.from_serialized(value)


class BaseRequest(object):
    def __init__(self, redis, queue, args=tuple(), kwds=dict(), timeout=None, offline=False):
        self.queue = queue
        self.args = args
        self.kwds = kwds
        self.redis = redis
        self.response_queue = uuid.uuid4().hex
        self.timeout = timeout
        self.raw = None
        self.offline = offline
    
    @classmethod
    def send_raw(self, redis, queue, request_data):
        redis.lpush(queue, request_data)
    
    def send(self):
        request_data = self.serialize({
            'response_queue' : self.response_queue,
            'args' : self.serialize(self.args),
            'kwds' : self.serialize(self.kwds),
            'queue' : self.queue,
            'offline' : self.offline,
        })
        request_data = '%s:%s' % (self.format, request_data)
        if self.timeout:
            pipe = self.redis.pipeline()
            pipe.lpush(self.queue, request_data)
            # pipe.expire(self.timeout)
            pipe.execute()
        else:
            self.redis.lpush(self.queue, request_data)
        return Promise(self.redis, self.queue, self.response_queue, self.response_class, self.timeout)
    
    @property
    def response_class(self):
        return FORMAT_TO_RESPONSE_CLASS[self.format]
    
    @classmethod
    def from_serialized(cls, ser):
        format, _, data = ser.partition(':')
        assert format in ['json', 'pickle']
        if format == 'json':
            cls = JSONRequest
        elif format == 'pickle':
            cls = PRequest
        deser = cls.deserialize(data)
        instance = cls(None, deser['queue'], args=deser['args'], kwds=deser['kwds'])
        instance.response_queue = deser['response_queue']
        instance.offline = deser.get('offline', False) # temporarily use get for old format compatability
        instance.raw = ser
        return instance
        

class JSONRequest(BaseRequest):
    ''' A request using json to serialize/deserialize '''
    serialize = classmethod(lambda self, x : json.dumps(x))
    deserialize = classmethod(lambda self, x : json.loads(x))
    format = 'json'

class PRequest(BaseRequest):
    ''' A request using cPickle to serialize/deserialize '''
    serialize = classmethod(lambda self, x : pickle.dumps(x))
    deserialize = classmethod(lambda self, x : pickle.loads(x))
    format = 'pickle'

class BaseResponse(object):
    def __init__(self, queue, status, data):
        self.status = status
        self.data = data
        self.queue = queue
        self.error_type = None
        self.traceback = None
        self.error_value = None
    
    def serialize_resp(self):
        response_data = self.serialize(self.response_dict)
        return '%s:%s' % (self.format, response_data)
    
    @property
    def response_dict(self):
        response_data = {
            'status' : self.status,
            'data' : self.data,
            'queue' : self.queue,
            
        }
        if self.status == 'ERROR':
            response_data.update(traceback=self.traceback, error_type=self.error_type, error_value=self.error_value)
        return response_data
    
    def serialize_failed_resp(self, request):
        resp = {
            'id' : uuid.uuid4().hex,
            'response' : self.response_dict,
            'request' : request.raw,
            'time' : datetime.utcnow().isoformat()
        }
        response_data = json.dumps(resp)
        return '%s:%s' % ('json', response_data)

    
    def set_exception(self, e):
        self.traceback = traceback.format_exc()
        if hasattr(e, 'traceback'):
            self.traceback = e.traceback
        self.error_type = type(e).__name__
        self.error_value = repr(e)
    
    @classmethod
    def from_serialized(cls, ser):
        format, _, data = ser.partition(':')
        assert format in ['json', 'pickle']
        if format == 'json':
            cls = JSONResponse
        elif format == 'pickle':
            cls = PResponse
        deser = cls.deserialize(data)
        instance = cls(deser['queue'], deser['status'], deser['data'])
        if instance.status == 'ERROR':
            instance.traceback = deser['traceback']
            instance.error_type = deser['error_type']
            instance.error_value = deser['error_value']
        return instance

class JSONResponse(BaseResponse):
    ''' A request using json to serialize/deserialize '''
    serialize = classmethod(lambda cls, x : json.dumps(x))
    deserialize = classmethod(lambda cls, x : json.loads(x))
    format = 'json'

    def set_exception(self, e):
        self.traceback = traceback.format_exc()
        self.error_type = str(type(e))
        self.error_value = str(e)


class PResponse(BaseResponse):
    ''' A request using cPickle to serialize/deserialize '''
    serialize = classmethod(lambda cls, x : pickle.dumps(x))
    deserialize = classmethod(lambda cls, x : pickle.loads(x))
    format = 'pickle'

FORMAT_TO_RESPONSE_CLASS = {
    'json' : JSONResponse, 
    'pickle' : PResponse
} 