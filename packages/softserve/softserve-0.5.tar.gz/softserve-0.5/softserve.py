#!/usr/bin/env python

# Copyright (C) 2012 Eric J. Suh
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

'''Serve static files with a tunable simulated network delay. Useful for
developing web apps that can handle network degradation with grace.

Serves files from the current directory.'''

import sys
import os
import argparse
import random
import time
import threading
import socket

try: # Python 3.x
    from urllib.parse import unquote
    from http.server import SimpleHTTPRequestHandler
    from socketserver import ThreadingTCPServer
except ImportError: # Python 2.7.x
    from urllib import unquote
    from SimpleHTTPServer import SimpleHTTPRequestHandler
    from SocketServer import ThreadingTCPServer

def get_request_handler_class(delay_min, delay_max, srvpath=None):
    '''Returns a subclass of SimpleHTTPRequestHandler that will add delays
    and serve from a different directory.'''
    if srvpath is None:
        srvpath = '.'

    class RequestHandler(SimpleHTTPRequestHandler, object):
        def handle(self):
            delay = random.randint(delay_min, delay_max)
            print('Delaying {} ms'.format(delay))
            time.sleep(float(delay)/1000.0)
            super(RequestHandler, self).handle()

        def translate_path(self, path):
            path = path.split('?',1)[0].split('#',1)[0]
            path = os.path.normpath(unquote(path))
            words = path.split('/')
            words = filter(None, words)
            path = os.path.abspath(srvpath)
            for word in words:
                word = os.path.splitdrive(word)[1]
                word = os.path.split(word)[1]
                if word in (os.curdir, os.pardir): continue
                path = os.path.join(path, word)
            return path

    return RequestHandler


class SoftserveTCPServer(ThreadingTCPServer, object):
    allow_reuse_address = True

    def handle_error(self, request, client_address):
        etype, evalue, etrace = sys.exc_info()
        if (evalue is not None
            and isinstance(evalue, socket.error)
            and evalue.errno == 32):
            pass # Just means a connection closed early
        else:
            super(SoftserveTCPServer, self).handle_error(request,
                                                         client_address)

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8000,
        help='port on which to serve files (default: %(default)s)')
    parser.add_argument('--min', type=int, default=1000,
        help='minimum delay in milliseconds (default: %(default)s)')
    parser.add_argument('--max', type=int, default=5000,
        help='maximum delay in milliseconds (default: %(default)s)')
    parser.add_argument('path', default='.', nargs='?', metavar='PATH',
        help='path relative to which to serve files (default: %(default)s)')

    args = parser.parse_args(argv)

    if (args.max < args.min):
        sys.stderr.write('Error: minimum delay must be less than maximum '
                         'delay\n')
        return 1

    random.seed()

    Handler = get_request_handler_class(args.min, args.max, args.path)
    httpd = SoftserveTCPServer(("localhost", args.port), Handler)
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.start()

    print('Softserving files from {} on port {}. '
          'Type Ctrl-C to exit.'.format(args.path, args.port))
    try:
        while server_thread.is_alive():
            pass
    except KeyboardInterrupt:
        pass
    finally:
        print('\nShutting down Softserve.')
        httpd.shutdown()
        httpd.server_close()
        print('Goodbye!')

    return 0

if __name__ == '__main__':
    sys.exit(main())
