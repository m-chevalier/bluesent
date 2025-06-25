import uuid
import hashlib

def generate_uuid_from_string(text):
    # Create a SHA-1 hash of the input string
    sha1_hash = hashlib.sha1(text.encode('utf-8')).hexdigest()

    # Take the first 32 hex digits (128 bits) from the SHA-1 hash
    # and convert it to a UUID
    uuid_str = sha1_hash[:32]

    # Format string as UUID: 8-4-4-4-12
    formatted_uuid = f'{uuid_str[:8]}-{uuid_str[8:12]}-{uuid_str[12:16]}-{uuid_str[16:20]}-{uuid_str[20:32]}'
    return formatted_uuid