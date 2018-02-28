from os import urandom
from binascii import hexlify
import hashlib, hmac

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

def generate_token(bits):
    return hexlify(urandom(bits))

def verify_mail_origin(api_key, email):
    for i in email:
        print(email[i])
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
