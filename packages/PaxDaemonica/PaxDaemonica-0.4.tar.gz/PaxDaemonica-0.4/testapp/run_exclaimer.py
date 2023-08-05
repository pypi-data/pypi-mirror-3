import time
import uuid
import pickle
import json
from redis import Redis
from app import exclaimer


if __name__ == '__main__':
    rqs = []
    for i in range(0, 2000):
        promise = exclaimer.delay(str(i), paxd_timeout=4)
        rqs.append(promise)
    
    for pr in rqs:
        print pr.get()
        # try:
        #     rqs.append(request.send())
        # except Exception, e:
        #     print e.type, e.traceback
        # time.sleep(1)
        # str(i),
        #     'response_queue' : rq,
        # }))
