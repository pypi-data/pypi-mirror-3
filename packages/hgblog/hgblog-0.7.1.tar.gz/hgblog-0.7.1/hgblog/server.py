#!/usr/bin/env python
# -*- coding: utf-8 -*-

from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from optparse import OptionParser
import os

from hgblog.utils import get_repo

def serve():
    """Begins a static HTML web server for an HgBlog"""

    # determine the port on which to listen for traffic
    parser = OptionParser()
    parser.add_option('-p', '--port', dest='port', default=8000,
            help="The port to serve your blog on")
    options, args = parser.parse_args()
    port = int(options.port)

    # get the root directory for the HgBlog repo
    repo = get_repo()
    html_path = os.path.join(repo.root, 'build', 'html')
    os.chdir(html_path)

    try:
        server = HTTPServer(('', port), SimpleHTTPRequestHandler)
        print 'Serving HTML in %s on port %s...' % (html_path, port)
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()

if __name__ == '__main__':
    serve()

