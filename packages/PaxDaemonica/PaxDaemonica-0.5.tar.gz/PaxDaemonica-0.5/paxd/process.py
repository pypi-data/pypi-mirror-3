import traceback

class print_exc(object):
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type == KeyboardInterrupt:
            return
        if exc_type:
            print ''.join(traceback.format_exception(exc_type, exc_val, exc_tb))
        return True

print_exc = print_exc()