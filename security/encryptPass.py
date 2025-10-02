from cryptography.fernet import Fernet

def encryptt(password:str):
    encoded_statement = password.encode()
    key = Fernet.generate_key()
    encryptor = Fernet(key)
    token = encryptor.encrypt(encoded_statement)

    return key, token