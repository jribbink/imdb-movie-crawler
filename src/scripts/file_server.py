from http.server import HTTPServer as BaseHTTPServer, SimpleHTTPRequestHandler
import socketserver
import os
from config import config

port = int(config["HTTP"]["port"])
directory = config["HTTP"]["directory"]


class HTTPHandler(SimpleHTTPRequestHandler):
    """This handler uses server.base_path instead of always using os.getcwd()"""
    def translate_path(self, path):
        path = SimpleHTTPRequestHandler.translate_path(self, path)
        relpath = os.path.relpath(path, os.getcwd())
        fullpath = os.path.join(self.server.base_path, relpath)
        return fullpath


class HTTPServer(BaseHTTPServer):
    """The main server, you pass in base_path which is the path you want to serve requests from"""
    def __init__(self, base_path, server_address, RequestHandlerClass=HTTPHandler):
        self.base_path = base_path
        BaseHTTPServer.__init__(self, server_address, RequestHandlerClass)

def file_server():
    print("Serving files from {} on port {}".format(directory, port))
    httpd = HTTPServer(directory, ("", port))
    httpd.serve_forever()