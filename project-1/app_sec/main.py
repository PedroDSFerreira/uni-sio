import json
import cherrypy
import sqlite3
import os
import html
import base64
from cryptography.hazmat.primitives import hashes

def calculate_hash(block):
    # Converto block to bytes
    block = block.encode('utf-8')
    digest = hashes.Hash(hashes.SHA256())
    digest.update(block)
    return digest.finalize()

class Root(object):
    def __init__(self):
        self.api = Api()
    # HTML pages
    @cherrypy.expose
    def index(self):
        return open("resources/html/index.html")

class Api(object):
    @cherrypy.expose
    def get_test_result(self, code):
        with sqlite3.connect("db/db.sqlite3") as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM site_test_results WHERE code = ?", (calculate_hash(code),))
            result = c.fetchone()
            if result is not None:
                # Open file, encode it to base64 and return it
                with open(result[2], "rb") as pdf_file:
                    encoded_string = base64.b64encode(pdf_file.read())
                    return encoded_string


    @cherrypy.expose
    def contact_us(self, name, email, phone, message):
        with sqlite3.connect("db/db.sqlite3") as conn:
            _name = html.escape(name)
            _email = html.escape(email)
            _phone = html.escape(phone)
            _message = html.escape(message)

            c = conn.cursor()
            c.execute("INSERT INTO site_contact_us (name, email, phone, message) VALUES (?, ?, ?, ?)", (_name, _email, _phone, _message))
            conn.commit()
            return {"status": True}
    
    @cherrypy.expose
    def review(self, name, email, message):
        with sqlite3.connect("db/db.sqlite3") as conn:
            _name = html.escape(name)
            _email = html.escape(email)
            _message = html.escape(message)

            c = conn.cursor()
            c.execute("INSERT INTO site_reviews (name, email, message) VALUES (?, ?, ?)", (_name, _email, _message))
            conn.commit()
            return {"status": True}

    @cherrypy.expose
    def get_reviews(self):
        with sqlite3.connect("db/db.sqlite3") as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM site_reviews")
            result = c.fetchall()

            return json.dumps(result)
    
    @cherrypy.expose
    def query_services(self, query):
        with sqlite3.connect("db/db.sqlite3") as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM site_services WHERE name LIKE ?", (query+'%',))
            result = c.fetchall()
            return json.dumps(result)

def error_page(status, message, traceback, version):
    return "Error"


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
conf = {
    "/": {    
        "tools.staticdir.root": BASE_DIR + "/resources", 
        "error_page.default": error_page,
    },

    "/html": {
        "tools.staticdir.on": True,
        "tools.staticdir.dir": "html"
    },

    "/js": {
        "tools.staticdir.on": True,
        "tools.staticdir.dir": "js"
    },

    "/css": {
        "tools.staticdir.on": True,
        "tools.staticdir.dir": "css"
    },

    "/images": {
        "tools.staticdir.on": True,
        "tools.staticdir.dir": "images"
    },    
}




if __name__ == "__main__":
    cherrypy.server.socket_port = 8000
    cherrypy.server.socket_host = '0.0.0.0'

    cherrypy.config.update(
        {
            
            "server.ssl_module": "builtin",
            "server.ssl_certificate": "ssl/cert.pem",
            "server.ssl_private_key": "ssl/privkey.pem",
            
            "tools.sessions.secure": "True",
            "tools.sessions.httponly": "True",
        }
    )

    cherrypy.quickstart(Root(), "/", conf)