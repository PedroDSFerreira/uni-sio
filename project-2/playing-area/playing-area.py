from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.hashes import SHA1
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.asymmetric import x25519, padding
import json
import base64
import os
import sys
import logging

LOG_FILE = "playing_area.log"

# append the path of the parent directory
sys.path.append("..")

from security import *


LOG_FILE = "playing_area.log"


class Server(Protocol):
    def __init__(self):
        self.nick = None
        self.seq = None
        self.client_pub_key = None
        self.fingerprint = None
        self.session_key = None

    def connectionMade(self):
        pass
        


    def connectionLost(self, reason):
        if self in self.factory.clients:
            self.factory.clients.remove(self)


    def dataReceived(self, data):
        msg = self.parse_message(data, self.session_key)
        self.log(data.decode("utf-8"))

        try:
            match msg["op"]:
                case "AUTH":
                    match msg["stage"]:
                        case "1":
                            # Recieves client's cert and cert_chain
                            client_cert = pem_to_cert(msg['cert'])

                            client_cert_chain = []
                            for cert in msg['cert_chain']:
                                client_cert_chain.append(pem_to_cert(cert))
                            
                            # Check if client's cert is valid
                            if is_cert_valid(client_cert, client_cert_chain, self.factory.trusted_certs):
                                # Store client's public key
                                self.client_pub_key = client_cert.public_key()

                                # Store client's fingerprint
                                self.fingerprint = client_cert.fingerprint(hashes.SHA256())

                                # Create challenge
                                self.challenge = os.urandom(16)


                                # Export cert and cert_chain to PEM
                                cert = cert_to_pem(self.factory.cert)

                                cert_chain = []
                                for _cert in self.factory.cert_chain:
                                    cert_chain.append(cert_to_pem(_cert))

                                # Send cert, cert_chain and challenge
                                response = {
                                    "op": "AUTH",
                                    "stage":"1",
                                    "cert": cert,
                                    "cert_chain": cert_chain,
                                    "challenge": base64.b64encode(self.challenge).decode("utf-8")
                                }

                            else:
                                response = {
                                    "op": "ERROR",
                                    "msg": "Client's cert is not valid"
                                }

                        case "2":
                            # Recieves signed challenge and new challenge
                            signed_challenge = base64.b64decode(msg['signed_challenge'])
                            challenge = base64.b64decode(msg['challenge'])


                            # Verify signed challenge
                            try:
                                self.client_pub_key.verify(
                                    signed_challenge,
                                    self.challenge,
                                    PKCS1v15(),
                                    SHA1()
                                )

                                # Sign challenge
                                signature = self.factory.priv_key.sign(
                                    challenge,
                                    padding.PSS(
                                        mgf=padding.MGF1(hashes.SHA256()),
                                        salt_length=padding.PSS.MAX_LENGTH
                                    ),
                                    hashes.SHA256()
                                )

                                # Send signed challenge
                                response = {
                                    "op": "AUTH",
                                    "stage":"2",
                                    "signed_challenge": base64.b64encode(signature).decode("utf-8")
                                }

                            except:
                                response = {
                                    "op": "ERROR",
                                    "msg": "Signature is not valid"
                                }


                        case "3":
                            # Recieves pub_key and signature
                            pub_bytes = base64.b64decode(msg['pub_key'])
                            signature = base64.b64decode(msg['signature'])

                            
                            # Verify pub_key
                            try:
                                self.client_pub_key.verify(
                                    signature,
                                    pub_bytes,
                                    PKCS1v15(),
                                    SHA1()
                                )

                                
                                # Store pub_key
                                dh_pub_key_2 = x25519.X25519PublicKey.from_public_bytes(pub_bytes)


                                # Generate elliptic curve Diffie-Hellman keypair
                                self.dh_priv_key, self.dh_pub_key = ecdh_keygen()

                                # Create session key
                                shared_key = self.dh_priv_key.exchange(dh_pub_key_2)

                                # Perform key derivation.
                                self.session_key = HKDF(
                                    algorithm=hashes.SHA256(),
                                    length=32,
                                    salt=None,
                                    info=b'handshake data',
                                ).derive(shared_key)

                                # Use 256 bits of the key for AES encryption
                                self.session_key = self.session_key[:32]


                                # Export pub_key to bytes
                                pub_bytes = self.dh_pub_key.public_bytes(
                                    encoding=serialization.Encoding.Raw,
                                    format=serialization.PublicFormat.Raw
                                )

                                # Sign pub_key
                                signature = self.factory.priv_key.sign(
                                    pub_bytes,
                                    padding.PSS(
                                        mgf=padding.MGF1(hashes.SHA256()),
                                        salt_length=padding.PSS.MAX_LENGTH
                                    ),
                                    hashes.SHA256()
                                )

                                # Send pub_key e signature
                                response = {
                                    "op": "AUTH",
                                    "stage":"3",
                                    "pub_key": base64.b64encode(pub_bytes).decode("utf-8"),
                                    "signature": base64.b64encode(signature).decode("utf-8")
                                }

                                # Send message in cleartext
                                self.send_message(response, None)

                            except:
                                response = {
                                    "op": "ERROR",
                                    "msg": "Signature is not valid"
                                }

                        case "4":
                            # Stores recieved pub_key
                            pub_key = base64.b64decode(msg["pub_key"])

                            # Import rsa pub_key
                            self.client_pub_key = rsa_load_pub_key(pub_key)
                            
                            # Request nickname
                            response = {
                                "op": "NICK"
                            }   

                        case _:
                            self.transport.loseConnection()
                            return

                case "NICK":
                    # Recieves username
                    print(f'player {msg["nickname"]} connected')
                    self.nick = msg["nickname"]

                    if self.nick == 'caller':
                        self.seq = 0
                    else:
                        self.seq = self.factory.seq
                        self.factory.seq += 1

                    response = {
                        "op": "WAIT",
                        "retry": False,
                        "nickname": self.nick,
                        "seq": self.seq
                    }

                    for client in self.factory.clients:
                        # Check if nick is already in use
                        if client.nick == self.nick:
                            response = {
                                "op": "ERROR",
                                "msg": "Nickname is already in use"
                            }
                            break
                        # Check fingerprint
                        if client.fingerprint == self.fingerprint:
                            response = {
                                "op": "ERROR",
                                "msg": "Smartcard was already used"
                            }
                            break
                    self.factory.clients.append(self)
                    
                case "START":
                    # Check the number of players
                    if len(self.factory.clients) < 2:
                        response = {
                            "op": "WAIT",
                            "retry": True
                        }
                    else:
                        self.factory.in_game = True

                        # Broadcast START
                        response = {
                            "op": "START"
                        }
                        for client in self.factory.clients:
                            client.send_message(response, client.session_key)
                        return


                case "ERROR":
                    print(msg["msg"])
                    self.transport.loseConnection()
                    return


                case _:
                    self.transport.loseConnection()
                    return


            
            self.log(json.dumps(response))
            self.send_message(response, self.session_key)

        except:
            print("Invalid message")
            self.transport.loseConnection()
        



    def send_message(self, msg, session_key=None):
        msg = json.dumps(msg).encode("utf-8")

        if session_key:
            iv = os.urandom(16)
            data = aes_encrypt(session_key, iv, msg)

            # Append iv to data
            data = iv + data

        else:
            # Send in cleartext
            data = msg

        data = base64.b64encode(data)

        self.transport.write(data)


    def parse_message(self, data, session_key=None):
        data = base64.b64decode(data)
        
        if session_key:
            iv = data[:16]
            data = data[16:]

            message = json.loads(aes_decrypt(session_key, iv, data).decode("utf-8"))

        else:
            message = json.loads(data.decode("utf-8"))
        
        return message
    

    def log(self, msg=None):
        """Log message"""

        signature = self.factory.priv_key.sign(
            msg.encode("utf-8"),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        signature = base64.b64encode(signature).decode("utf-8")

        log_msg = f"{self.seq}:{datetime.now()}:{hash(self.factory.prev_entry)}:{msg}:{signature}"

        logging.debug(log_msg)
        self.factory.prev_entry = log_msg


class ServerFactory(Factory):
    protocol = Server

    def __init__(self):
        self.in_game = False
        self.prev_entry = ''
        self.seq = 1
        self.priv_key = load_private_key_file("keys/priv_key.pem")
        self.cert = load_certificate_file("certs/Parea.crt")
        self.cert_chain = [self.cert, load_certificate_file("certs/root_CA.crt")]
        self.trusted_certs = get_trusted_certs()
        self.clients = []

if __name__ == "__main__":
    # Start logging
    logging.basicConfig(filename= LOG_FILE, encoding='utf-8', level=logging.DEBUG)

    # Start server
    print("Starting server...")
    reactor.listenTCP(1234, ServerFactory())
    reactor.run()
    