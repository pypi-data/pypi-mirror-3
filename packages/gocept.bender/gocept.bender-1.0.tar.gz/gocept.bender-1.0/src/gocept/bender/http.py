# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import BaseHTTPServer
import logging
import threading
import urllib2


log = logging.getLogger(__name__)


class HTTPServer(BaseHTTPServer.HTTPServer):
    # shutdown mechanism borrowed from gocept.selenium.static.HTTPServer

    _continue = True

    @classmethod
    def start(cls, host, port, bender, username, password):
        server_address = (host, port)
        BenderRequestHandler.bender = bender
        BenderRequestHandler.username = username
        BenderRequestHandler.password = password
        httpd = cls(server_address, BenderRequestHandler)
        thread = threading.Thread(target=httpd.serve_until_shutdown)
        thread.daemon = True
        thread.start()
        log.info('HTTP server started on %r', server_address)
        return httpd

    def serve_until_shutdown(self):
        while self._continue:
            self.handle_request()

    def shutdown(self):
        self._continue = False
        # We fire a last request at the server in order to take it out of the
        # while loop in `self.serve_until_shutdown`.
        try:
            urllib2.urlopen(
                'http://%s:%s/die' % (self.server_name, self.server_port),
                timeout=1)
        except urllib2.URLError:
            # If the server is already shut down, we receive a socket error,
            # which we ignore.
            pass
        self.server_close()


class BaseHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        pass


class BenderRequestHandler(BaseHTTPRequestHandler):

    bender = None
    username = None
    password = None

    def authorize(self):
        auth_header = self.headers.getheader('Authorization')
        hash = '%s:%s' % (self.username, self.password)
        hash = hash.encode('base64').strip()
        if auth_header == 'Basic %s' % hash:
            return True
        return False

    def do_POST(self):
        if not self.authorize():
            self.send_response(401)
            self.send_header(
                'WWW-Authenticate', 'Basic realm="Bender Jabber Bot"')
            self.render(
                'ERROR - Unauthorized: You sent no or invalid credentials')
            return

        length = int(self.headers['content-length'])
        data = self.rfile.read(length)
        self.bender.say(data)
        self.send_response(200)
        log.info('Received POST from %r', self.client_address[0])
        self.render("OK - I've said that to %s" % self.bender.chatroom)

    def do_GET(self):
        self.send_response(200)
        self.render(
            "OK - Hello human! I'm Bender. If you have something"
            " for me to say, please POST it here.")

    def render(self, text):
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        if not text.endswith('\n'):
            text += '\n'
        self.wfile.write(text.encode('utf-8'))
