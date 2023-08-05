import time
import os.path
# from appserver import Application
from paxd.server.controller import Controller

def main(id):
    c = Controller(id)
    c.run()


if __name__ == '__main__':
    import sys
    main(sys.argv[1])