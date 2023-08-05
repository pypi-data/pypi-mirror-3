#!/usr/bin/env python

import sys
import socket

REQUEST_TEMPLATE = ('%(method)s %(path)s HTTP/1.1\r\n'
                    'Host: %(host)s\r\n\r\n')

SUPPORTED_METHODS = ('HEAD', 'GET')

def sockhttp(sockpath, method, path, host):
    """Make an HTTP request over a unix socket."""
    req = REQUEST_TEMPLATE % locals()
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(sockpath)
    s.send(req)
    out = ''
    while 1:
        data = s.recv(1024)
        out += data
        if not data: break
    s.close()
    return out

def usage():
    """Print usage information for this program"""
    print ("This program allows you to make http requests to unix sockets. "
           "Usage:\n\n"
           "python %s /path/to/socket METHOD request_path host_name\n" %
           __file__)

    print "Supported methods are: %s" % ", ".join(SUPPORTED_METHODS)

if __name__ == '__main__':
    try:
        _, sockpath, method, path, host = sys.argv
    except ValueError:
        usage()
        sys.exit(1)
    print sockhttp(sockpath, method, path, host)

