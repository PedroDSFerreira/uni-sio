from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


def rsa_keygen(priv_key = None):
    """Generate RSA key pair"""
    if priv_key is None:
        priv_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=1024,
        )
    
    pub_key = priv_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )


    return priv_key, pub_key

def rsa_load_pub_key(pub_key):
    """Load public key from bytes"""
    return serialization.load_pem_public_key(pub_key)