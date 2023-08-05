from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import threading
class HTTPTestServer(threading.Thread):
    
    def __init__(self):
        super(HTTPTestServer, self).__init__()
        self._stop = threading.Event()
    
    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()
    
    class MyHandler(BaseHTTPRequestHandler):
    
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(" ".join([self.command, self.path]))
            return
    
        def do_POST(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(" ".join([self.command, self.path]))
            return
    
        def do_PUT(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(" ".join([self.command, self.path]))
            return
        
        def do_DELETE(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(" ".join([self.command, self.path]))
            return
        
    def run(self):
        server = HTTPServer(('', 8880), HTTPTestServer.MyHandler)
        while not self.stopped():
            server.handle_request()

if __name__ == '__main__':
#    server = HTTPServer(('', 8880), MyHandler)
#    server.handle_request()
    ht = HTTPTestServer()
    ht.start()
