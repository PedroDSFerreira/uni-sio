from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7

def aes_encrypt(key, iv, data):
    """Encrypt data with AES"""
    padder = PKCS7(256).padder()
    data = padder.update(data) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    return encryptor.update(data) + encryptor.finalize()

def aes_decrypt(key, iv, data):
    """Decrypt data with AES"""
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    data = decryptor.update(data) + decryptor.finalize()

    unpadder = PKCS7(256).unpadder()
    return unpadder.update(data) + unpadder.finalize()