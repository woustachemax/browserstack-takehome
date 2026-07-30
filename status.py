import threading

_lock = threading.Lock()
_status = {}

def set_status(key, value):
    with _lock:
        _status[key] = value

def get_status():
    with _lock:
        return dict(_status)