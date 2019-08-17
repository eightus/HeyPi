import hashlib
import uuid


def sha512hash(pwd, salt=None):
    if salt is None:
        salt = uuid.uuid4().hex
        hashed_pwd = hashlib.sha512((pwd + salt).encode('utf-8')).hexdigest()
        return hashed_pwd, salt
    else:
        hashed_pwd = hashlib.sha512((pwd + salt).encode('utf-8')).hexdigest()
        return hashed_pwd
