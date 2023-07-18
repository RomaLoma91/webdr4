from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from threading import Thread
from datetime import datetime
import urllib.parse
import mimetypes
import logging
import socket
import json

BASE_DIR = Path()

class HTTPHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        route = urllib.parse.urlparse(self.path)
        if route.path == '/':
            self.send_html('index.html')
            logging.debug(f'Route to {route.path}')
        elif route.path == '/message':
            self.send_html('message.html')
            logging.debug(f'Route to {route.path}')
        else:
            file =  BASE_DIR / self.path[1:]
            if file.exists():
                self.send_static(file)
            else:
                self.send_html('error.html', 404)

    def do_POST(self):
        body = self.rfile.read(int(self.headers['Content-Length']))
        send_data_to_socket(body)

        # print(body)

        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()
    

    def send_html(self, filename, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'text/html')    
        self.end_headers()       
        with open(BASE_DIR / filename, 'rb') as fd:
                self.wfile.write(fd.read())

    def send_static(self, filename, status_code=200):
        mime_type, *mt = mimetypes.guess_type(BASE_DIR / self.path)
        self.send_response(status_code)
        if mime_type:
            self.send_header('Content-type', mime_type)
        else:
            self.send_header('Content-type', 'text/plain')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())
    def log_message(self, format, *args):
        return

def save_data_to_json(data):
    try:
        with open(BASE_DIR.joinpath('storage/data.json'), 'r') as fd:
            content = json.load(fd)
        
        content.update(data)

        with open(BASE_DIR.joinpath('storage/data.json'), 'w', encoding="utf-8") as fd:
            json.dump(content, fd, ensure_ascii=False, indent=4)
    except ValueError as e:
        logging.error(f'Failed parse data {data}: with error - {e}')
    except OSError as e:
        logging.error(f'Failed write data {data}: with error - {e}')

def run(server=HTTPServer, handler=HTTPHandler, port=3000):
    address = ('localhost', port)
    http_server = server(address, handler)
    try:
        print(f'\nHTTP SERVER ---')
        print(f'ADDRESS: http://localhost:{port}\nPORT: {port}\n')
        http_server.serve_forever()
        
        
    except KeyboardInterrupt:
        http_server.server_close()
    except BrokenPipeError:
        pass
            
def send_data_to_socket(data, ip='127.0.0.1', port=5000):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.sendto(data, (ip, port))
    client_socket.close()

def run_socket_server(ip='127.0.0.1', port=5000, buffer=1024):
    print(f'\nSOCKET SERVER ---\nIP: {ip}\nPORT:{port}\n')
    
    server = (ip, port)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(server)

    try:
        while True:
            data, address = server_socket.recvfrom(buffer)

            print(f'GET DATA - {data}')
            data = urllib.parse.unquote_plus(data.decode())
            data = {str(datetime.now()): {key: value for key, value in [el.split('=') for el in data.split('&')]}}
            save_data_to_json(data)

    except KeyboardInterrupt:
        logging.info('Socket server stoped.')
    finally:
        logging.info('Socket server successfully closed.')
        server_socket.close()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(threadName)s - %(message)s')
    http_server = Thread(target=run)
    http_server.start()

    socket_server = Thread(target=run_socket_server)
    socket_server.start()

    http_server.join()
    socket_server.join()

    print('All servers stoped!')


