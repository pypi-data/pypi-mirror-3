import importlib
import sys
import urllib

# Args
assert len(sys.argv) == 4, 'Usage: load_task.py host path entry'
host = sys.argv[1]
path = sys.argv[2]
entry = sys.argv[3]

# Import Functions
sys.path.insert(0, path)
module, _, fun = entry.rpartition('.')
module = importlib.import_module(module)
fun = getattr(module, fun)
assert hasattr(fun, 'paxd_queue'), 'This function is not a paxd task'
queue = fun.paxd_queue

url = 'http://{host}:22100/load?path={path}&entry={entry}&queue={queue}'.format(**vars())

print urllib.urlopen(url).read()