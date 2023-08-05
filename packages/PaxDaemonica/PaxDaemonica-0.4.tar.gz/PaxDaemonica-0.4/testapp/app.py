import time
import sys
sys.path.insert(0, '.')
import paxd.client
from paxd.client import make_task_file
import os.path 

task = make_task_file('testapp/paxd.conf')

@task(queue='testapp.app:exclaimer')
def exclaimer(thing):
    time.sleep(0.2)
    return str(thing) + '!!!!!!!'

@task(queue='testapp.app:error_test')
def error_test():
    raise Exception('BAD BAD BAD')
