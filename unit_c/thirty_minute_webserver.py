#
# ws30 -- the thirty minute web server
# author: Wilhelm Fitzpatrick (rafial@well.com)
# date: August 3rd, 2002
# version: 1.0
#
# Written after attending a Dave Thomas talk at PNSS and hearing about
# his "write a web server in Ruby in one hour" challenge.
#
# Actual time spent:
#  30 minutes reading socket man page
#  30 minutes coding to first page fetched
#   3 hours making it prettier & more pythonic
#
# updated by Brian Dorsey
#

import os
import socket
import sys

host = ""
port = 8080
mime_types = {'.jpg': 'image/jpg',
             '.gif': 'image/gif',
             '.png': 'image/png',
             '.html': 'text/html',
             '.pdf': 'application/pdf'}
response_headers = {}

response_headers[200] =\
"""HTTP/1.0 200 Okay
Server: ws30
Content-type: %s

%s
"""

response_headers[301] =\
"""HTTP/1.0 301 Moved
Server: ws30
Content-type: text/plain
Location: %s

moved
"""

response_headers[404] =\
"""HTTP/1.0 404 Not Found
Server: ws30
Content-type: text/plain

%s not found
"""

DIRECTORY_LISTING =\
"""<html>
<head><title>%s</title></head>
<body>
<a href="%s..">..</a><br>
%s
</body>
</html>
"""

DIRECTORY_LINE = '<a href="%s">%s</a><br>'


def server_socket(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(1)
    return s


def parse_request(sock):
    data = sock.recv(4096)
    if not data:
        print "Bad request: no data"
        return ''
    line = data[0:data.find("\r")]
    print line
    #print headers
    #headers = data[0:data.find("\r\n\r\n")]
    method, uri, protocol = line.split()
    return uri


def list_directory(uri):
    entries = os.listdir('.' + uri)
    entries.sort()
    return DIRECTORY_LISTING % (uri, uri, '\n'.join(
        [DIRECTORY_LINE % (e, e) for e in entries]))


def get_file(path):
    f = open(path)
    try:
        return f.read()
    finally:
        f.close()


def get_content(uri):
    try:
        path = '.' + uri
        if os.path.isfile(path):
            return (200, get_mime(uri), get_file(path))
        if os.path.isdir(path):
            if(uri.endswith('/')):
                return (200, 'text/html', list_directory(uri))
            else:
                return (301, uri + '/')
        else:
            return (404, uri)
    except IOError, e:
        return (404, e)


def get_mime(uri):
    return mime_types.get(os.path.splitext(uri)[1], 'text/plain')


def send_response(sock, content):
    template = response_headers[content[0]]
    data = template % content[1:]
    sock.sendall(data)


if __name__ == '__main__':
    server = server_socket(host, int(port))
    print 'starting %s on %s...' % (host, port)
    try:
        while True:
            sock, client_address = server.accept()
            uri = parse_request(sock)
            if uri:
                content = get_content(uri)
                send_response(sock, content)
            sock.close()
    except KeyboardInterrupt:
        print 'shutting down...'
    server.close()
