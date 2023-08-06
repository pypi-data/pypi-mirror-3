# -*- coding: utf-8 -*-

import argparse
import logging
import os
import shutil

try:
    from urllib.parse import unquote
    from http.server import HTTPServer, SimpleHTTPRequestHandler
    from socketserver import ForkingMixIn, ThreadingMixIn
except ImportError:
    from urllib import unquote
    from BaseHTTPServer import HTTPServer
    from SimpleHTTPServer import SimpleHTTPRequestHandler
    from SocketServer import ForkingMixIn, ThreadingMixIn

from .utils.env import add_index_dir, get_document_rootdir

__version__ = "0.1.1"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

class ProcessedHTTPServer(ForkingMixIn, HTTPServer):
    """Handle requests in multi process."""

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

class LittleHTTPRequestHandler(SimpleHTTPRequestHandler):
    """Little HTTP request handler is inspired from SimpleHTTPRequestHandler.
    """

    server_version = "LittleHTTP/" + __version__
    tmp_path = ""

    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.

        This function is originally defined on SimpleHTTPRequestHandler.
        Though SimpleHTTPRequestHandler returns local path based on
        current directory in which involved, LittleHTTPRequestHandler
        returns temporary directory in which has symlinks to
        document directories.
        """
        # abandon query parameters
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        path = os.path.normpath(unquote(path))
        words = path.split('/')
        words = filter(None, words)
        actual_path = self.tmp_path
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            actual_path = os.path.join(actual_path, word)
        return actual_path

def parse_argument():
    parser = argparse.ArgumentParser()
    parser.set_defaults(doc_dirs=[], port=8000, index_dir=None,
            protocol="HTTP/1.0", server_type="process", verbose=False)
    parser.add_argument("-d", "--dir", dest="doc_dirs", action="append",
            metavar="DOCUMENT_DIR", help="set some document directories")
    parser.add_argument("-i", "--indexdir", dest="index_dir",
            metavar="INDEX_DIRECTORY", help="set arbitrary top directory")
    parser.add_argument("-p", "--port", dest="port", type=int,
            metavar="PORT_NUMBER", help="set server port number")
    parser.add_argument("-v", "--verbose", action="store_true",
            help="set verbose mode")
    parser.add_argument("--protocol", dest="protocol",
            metavar="PROTOCOL", help="set protocol")
    parser.add_argument("--servertype", dest="server_type",
            choices=("process", "thread"), help="set server type")
    parser.add_argument("--version", action="version",
            version="%%(prog)s %s" % __version__,
            help="show program version")
    args = parser.parse_args()
    if not (args.doc_dirs or args.index_dir):
        args.index_dir = "."

    # verbose mode
    if args.verbose:
        logging.root.setLevel(logging.DEBUG)
    logging.debug("args: {0}".format(args))
    return args

_HTTP_SERVER = {
    "process": ProcessedHTTPServer,
    "thread": ThreadedHTTPServer,
}

def test(args):
    server = _HTTP_SERVER[args.server_type]
    server_address = ('', args.port)

    doc_root = get_document_rootdir(args.doc_dirs)
    LittleHTTPRequestHandler.protocol_version = args.protocol
    LittleHTTPRequestHandler.tmp_path = doc_root

    if args.index_dir:
        add_index_dir(doc_root, args.index_dir)

    httpd = server(server_address, LittleHTTPRequestHandler)
    sa = httpd.socket.getsockname()
    logging.info("Serving {protocol} on {0}, port: {port} ...".format(
                    sa[0], **vars(args)))
    try:
        httpd.serve_forever()
    except:
        shutil.rmtree(doc_root)
        logging.info("Server is shutdown")

def main():
    test(parse_argument())

if __name__ == '__main__':
    main()
