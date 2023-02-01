from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey

def ecdh_keygen():
    """Generate a elliptic curve Diffie-Hellman key pair"""

    private_key = X25519PrivateKey.generate()
    public_key = private_key.public_key()

    return private_key, public_key
