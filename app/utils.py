import hashlib

from app.config import SECRET_KEY


def generate_signature(data):
    sorted_keys = sorted(data.keys())
    concat_str = ''.join(str(data[key]) for key in sorted_keys) + SECRET_KEY
    return hashlib.sha256(concat_str.encode()).hexdigest()


def verify_signature(data, signature):
    return generate_signature(data) == signature
