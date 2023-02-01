import PyKCS11
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend as db
from datetime import datetime
from getpass import getpass
from datetimerange import DateTimeRange
import os

LIB = '/usr/lib/x86_64-linux-gnu/pkcs11/opensc-pkcs11.so'

def load_certificate_file(pem_file):
    with open(pem_file, 'rb') as file:
        cert = x509.load_pem_x509_certificate(file.read(), backend=db())
        return cert
    
def load_private_key_file(pem_file, password=None):
    with open(pem_file, 'rb') as file:
        key = serialization.load_pem_private_key(
            file.read(),
            password=password,
            backend=db()
        )
        return key

def get_trusted_certs():
    # Load all PEM certs located in /trusted-certs
    trusted_certs = []
    for file in os.listdir('trusted-certs'):
        if file.endswith(('.pem', '.crt')):
            trusted_certs.append(load_certificate_file('trusted-certs/' + file))

    return trusted_certs

        
def is_cert_valid(cert: x509.Certificate, cert_chain: x509.Certificate, trusted_certs):
    """Check certificate validity"""

    # Check if cert is in cert_chain
    if cert not in cert_chain:
        return False

    # Validate certificate time interval
    interval = DateTimeRange(cert.not_valid_before, cert.not_valid_after)
    if not datetime.today() in interval:
        return False

    # Validate certificate chain time interval
    for c in cert_chain:
        interval = DateTimeRange(c.not_valid_before, c.not_valid_after)
        if not datetime.today() in interval:
            return False
    
    for authority in trusted_certs:
        # Validate authority time interval
        interval = DateTimeRange(authority.not_valid_before, authority.not_valid_after)
        if not datetime.today() in interval:
            return False

        # Validate certificate chain
        for c in cert_chain:
            if authority.subject == c.issuer:
                return True

    return False

def get_session():
    """Create session with the smart card"""

    # Input smart card password
    password = getpass()

    # Create a PKCS11 library object
    lib = PyKCS11.PyKCS11Lib()
    # Load the library
    lib.load(LIB)

    # Get the list of available slots
    slots = lib.getSlotList()

    # Choose the first slot
    slot = slots[0]

    # Open a session with the slot
    session = lib.openSession(slot)
    session.login(password)

    return session


def get_certificate_chain(session: PyKCS11.Session):
    """Get certificate chain from smart card"""

    # Get the list of available certificates in the slot
    template = [
        (PyKCS11.CKA_CLASS, PyKCS11.CKO_CERTIFICATE),
    ]
    
    # Get citizen authentication certificate
    c_cert = session.findObjects([
        (PyKCS11.CKA_CLASS, PyKCS11.CKO_CERTIFICATE),
        (PyKCS11.CKA_LABEL, 'CITIZEN AUTHENTICATION CERTIFICATE')
    ])[0]
    
    c_cert_data = bytes(c_cert.to_dict()['CKA_VALUE'])
    certificate = x509.load_der_x509_certificate(c_cert_data, backend=db())
    
    
    chain = []
    # Convert certificates to Certificate object
    for cert in session.findObjects(template):
        cert_data = bytes(cert.to_dict()['CKA_VALUE'])
        cert = x509.load_der_x509_certificate(cert_data, backend=db())
        chain.append(cert)


    # Return the certificate and the certificate chain
    return certificate, chain


def cc_sign(message: bytes, session: PyKCS11.Session):
    """Sign a message with the citizen card"""

    # Get the private key object
    priv_key = session.findObjects([(PyKCS11.CKA_CLASS, PyKCS11.CKO_PRIVATE_KEY)])[0]

    mechanism = PyKCS11.Mechanism(PyKCS11.CKM_SHA1_RSA_PKCS, None)

    signature = bytes(session.sign(priv_key, message, mechanism))

    return signature

def cert_to_pem(cert: x509.Certificate):
    return cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")

def pem_to_cert(pem: str):
    return x509.load_pem_x509_certificate(pem.encode('utf-8'), backend=db())