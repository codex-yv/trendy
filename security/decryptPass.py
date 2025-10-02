from cryptography.fernet import Fernet

def decryptt(token:bytes, key:bytes):
    encryptor = Fernet(key)
    dcpt_token = encryptor.decrypt(token).decode()
    
    return dcpt_token