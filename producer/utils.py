import uuid
import hashlib
import time

def generate_uuid_from_string(text):
    return int(time.time() * 1000)