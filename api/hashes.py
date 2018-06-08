from os import urandom
from binascii import hexlify
import hashlib, hmac
from flask import current_app

def hash_password(password,salt):
    password = password.encode('utf-8')
    return hexlify(hashlib.pbkdf2_hmac('sha256', password, salt, 100000))

def store_password(password,unique_salt=True):
    uuid = hexlify(urandom(16))
    salt = hexlify(urandom(16))
    if not unique_salt:
        salt = hash_password(current_app.config['SECRET_KEY'],current_app.config['SECRET_SALT'])
    hash = hash_password(password,salt)
    return {
        'password': hash,
        'salt': salt,
        'uuid': uuid
    }

def check_password(stored_password,stored_salt,password):
    hash = hash_password(password,stored_salt)
    print('check_password: {}'.format(str(stored_password)))
    print('                {}'.format(str(hash)))
    return str(stored_password) == str(hash)

def generate_token(bits):
    return hexlify(urandom(bits))

def verify_mail_origin(api_key, email):
    for i in email:
        print(i, email[i])
    print('')

    try:
        hmac_digest = hmac.new(
            key=api_key,
            msg='{}{}'.format(email['timestamp'], email['token']),
            digestmod=hashlib.sha256
        ).hexdigest()
        print(unicode(email['signature']))
        print(unicode(hmac_digest))

        hmac_comparison = hmac.compare_digest(
            unicode(email['signature']),
            unicode(hmac_digest)
        )
    except:
        return False

    return hmac_comparison
