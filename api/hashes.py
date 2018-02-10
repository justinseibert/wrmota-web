from os import urandom
from binascii import hexlify
import hashlib
from flask import current_app

def protect(string, salt):
    protect = str(string + salt).encode('utf-8')
    return hashlib.sha1(protect).hexdigest()

def hash_password(password,salt):
    password = password.encode('utf-8')
    return hexlify(hashlib.pbkdf2_hmac('sha256', password, salt, 100000))

def store_password(password):
    uuid = hexlify(urandom(16))
    salt = hexlify(urandom(16))
    hash = hash_password(password,salt)
    return {
        'password': hash,
        'salt': salt,
        'uuid': uuid
    }

def check_password(stored_password,stored_salt,password):
    hash = hash_password(password,stored_salt)
    return str(stored_password) == str(hash)

def generate_token():
    return hexlify(urandom(16))
