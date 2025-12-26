import time
from .uid_generator import d_uid

def current_millis() -> int:
    return int(time.time() * 1000)