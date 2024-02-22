import hashlib

def hash_email(email):
    hashed_email = hashlib.sha256(email.encode()).hexdigest()
    return hashed_email