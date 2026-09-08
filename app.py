#!/usr/bin/env python

import os
import subprocess
from datetime import datetime
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

FILE_PATH = os.environ.get('FILE_PATH', './.tmp')
openhttp = os.environ.get('OPENHTTP', '1')
port = int(os.environ.get('PORT', 8080))
# port = int(os.environ.get('PORT') or os.environ.get('SERVER_PORT') or 8080)
DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'

def log(level, msg):
    if not DEBUG and level != "INFO":
        return
    print(f"{datetime.now()} - {level} - {msg}")

def info(msg): log("INFO", msg)
def debug(msg):
    if DEBUG:
        log("DEBUG", msg)

proc = subprocess.Popen(
    ['bash', './start.sh'],
    env={**os.environ, 'OPENHTTP': openhttp},
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

def read_output(stream, prefix):
    for line in stream:
        debug(f"{prefix}{line}")
threading.Thread(target=read_output, args=(proc.stdout, ''), daemon=True).start()

info("Starting Server...")
if openhttp == '1':
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/':
                try:
                    with open('index.html', 'rb') as file:
                        content = file.read()
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(content)
                except FileNotFoundError:
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/plain; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(b'Hello, world')
                except Exception as e:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(f'Server error: {str(e)}'.encode())
            elif self.path == '/sub':
                try:
                    with open(os.path.join(FILE_PATH, 'log.txt'), 'rb') as file:
                        content = file.read()
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/plain; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(content)
                except FileNotFoundError:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(b'Error reading file')
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'Not found')

        def log_message(self, *args):
            pass

    info(f'server is listening on port: {port}')
    httpd = HTTPServer(('', port), Handler)
    httpd.serve_forever()
elif openhttp == '0':
    info(f'server is listening on port: {port}')
    proc.wait()
