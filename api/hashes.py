import hashlib

def protect(string, salt):
    protect = str(string + salt).encode('utf-8')
    return hashlib.sha1(protect).hexdigest()
