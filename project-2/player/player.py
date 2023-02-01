from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet import reactor
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.asymmetric import x25519, padding
import json
import base64
import os
import sys
  
# append the path of the parent directory
sys.path.append("..")

from security import *

class Client(Protocol):
    def __init__(self):
        self.cert = None
        self.cert_chain = None
        self.salt = None
        self.session_key = None
        

    def connectionMade(self):
        # Establish session
        self.session = get_session()

        # Get cert and cert_chain
        self.cert, self.cert_chain = get_certificate_chain(self.session)


        print("Authenticating...")

        # Export cert and cert_chain to PEM
        cert = cert_to_pem(self.cert)

        cert_chain = []
        for _cert in self.cert_chain:
            cert_chain.append(cert_to_pem(_cert))


        # Send cert and cert_chain
        msg = {
            "op": "AUTH",
            "stage":"1",
            "cert": cert,
            "cert_chain": cert_chain
        }
        self.send_message(msg)



    def connectionLost(self, reason):
        pass

    def dataReceived(self, data):
        msg = self.parse_message(data, self.session_key)

        try:
            match msg["op"]:
                case "AUTH":
                    match msg["stage"]:
                        case "1":
                            # Recieves server's cert, cert_chain and challenge
                            server_cert = pem_to_cert(msg['cert'])
                            
                            server_cert_chain = []
                            for cert in msg['cert_chain']:
                                server_cert_chain.append(pem_to_cert(cert))
                            
                            challenge = base64.b64decode(msg['challenge'])


                            # Check if server's cert is valid
                            if is_cert_valid(server_cert, server_cert_chain, self.factory.trusted_certs):
                                # Store server's public key
                                self.server_pub_key = server_cert.public_key()

                            
                            # Sign challenge with cc's session
                            signature = cc_sign(challenge, self.session)


                            # Create challenge
                            self.challenge = os.urandom(16)


                            response = {
                                "op": "AUTH",
                                "stage":"2",
                                "signed_challenge": base64.b64encode(signature).decode("utf-8"),
                                "challenge": base64.b64encode(self.challenge).decode("utf-8"),
                            }

                        case "2":
                            # Recieves signed challenge
                            signed_challenge = base64.b64decode(msg['signed_challenge'])

                            # Verify signed challenge
                            try:
                                self.server_pub_key.verify(
                                    signed_challenge,
                                    self.challenge,
                                    padding = padding.PSS(
                                        mgf = padding.MGF1(hashes.SHA256()),
                                        salt_length = padding.PSS.MAX_LENGTH
                                    ),
                                    algorithm = hashes.SHA256()
                                )

                                
                            except:
                                print("Signature not verified")
                                self.transport.loseConnection()
                                return

                            # Generate elliptic curve Diffie-Hellman keypair
                            self.dh_priv_key, self.dh_pub_key = ecdh_keygen()

                            # Export pub_key to bytes
                            pub_bytes = self.dh_pub_key.public_bytes(
                                encoding=serialization.Encoding.Raw,
                                format=serialization.PublicFormat.Raw
                            )

                            signature = cc_sign(pub_bytes, self.session)


                            # Send pub_key e signature
                            response = {
                                "op": "AUTH",
                                "stage":"3",
                                "pub_key": base64.b64encode(pub_bytes).decode("utf-8"),
                                "signature": base64.b64encode(signature).decode("utf-8")
                            }


                        case "3":
                            # Recieves server's pub_key and signature
                            pub_bytes = base64.b64decode(msg['pub_key'])
                            signature = base64.b64decode(msg['signature'])

                            # Verify signature
                            try:
                                self.server_pub_key.verify(
                                    signature,
                                    pub_bytes,
                                    padding = padding.PSS(
                                        mgf = padding.MGF1(hashes.SHA256()),
                                        salt_length = padding.PSS.MAX_LENGTH
                                    ),
                                    algorithm = hashes.SHA256()
                                )

                                # Create session key
                                dh_pub_key_2 = x25519.X25519PublicKey.from_public_bytes(pub_bytes)

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


                                # Generate an rsa keypair (will be used for the game, instead of smartcard)
                                self.priv_key, self.pub_key = rsa_keygen()

                                response = {
                                    "op": "AUTH",
                                    "stage":"4",
                                    "pub_key": base64.b64encode(self.pub_key).decode("utf-8")
                                }

                            except:
                                print("Signature not verified")
                                self.transport.loseConnection()
                                return


                        case _:
                            self.transport.loseConnection()
                            return

                case "NICK":
                    # Ask for nickname
                    nickname = self.choose_nick()

                    response = {
                        "op": "NICK",
                        "nickname": nickname
                    }
                
                case "WAIT":
                    print(f'You are player {msg["nickname"]}, number {msg["seq"]}')
                    print("Waiting for the game to start...")
                    return
                
                case "START":
                    print("Game started!")
                    return

                case "ERROR":
                    print(msg["msg"])
                    self.transport.loseConnection()
                    return


                case _:
                    self.transport.loseConnection()
                    return
                
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

    def choose_nick(self):
        while True:
            nick = input("Enter your nickname: ").lower()
            if nick != '' and nick != 'caller':
                break
            print("Invalid nickname")
        return nick


class ClientFactory(ClientFactory):
    protocol = Client

    def __init__(self):
        self.trusted_certs = get_trusted_certs()

    def clientConnectionFailed(self, connector, reason):
        print("Connection failed")
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print("Connection lost")
        reactor.stop()

if __name__ == "__main__":
    print("Starting client...")
    # Start client
    reactor.connectTCP("localhost", 1234, ClientFactory())
    reactor.run()
