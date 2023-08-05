import time
import uuid
import pickle
import json
from redis import Redis
from app import error_test


if __name__ == '__main__':
    print error_test.delay(paxd_timeout=2).get()

