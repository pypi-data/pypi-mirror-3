import time
import os
import os.path
# from appserver import Application
from paxd.server.controller import Controller

def main(id):
    assert 'BROKER_HOST' in os.environ, 'BROKER_HOST is required as an environment variable'
    broker_host = os.environ['BROKER_HOST']
    broker_port = int(os.environ.get('BROKER_PORT', 6379))
    c = Controller(id, broker_host, broker_port=broker_port)
    c.run()


if __name__ == '__main__':
    import sys
    main(sys.argv[1])
    