#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import cgi
import mimetypes
from string import Template

from jabber import RosterUtility
import tools


version = '0.1'


def index(environ, start_response):
    """Main view."""
    pyjru_path = environ.get('PYJRU_PATH', '').lstrip('/')
    if pyjru_path:
        pyjru_path += '/'
    body = Template(open(pyjru_path + 'templates/index.html').read()).substitute(dict(version=version))
    start_response('200 OK', [('Content-Type', 'text/html'), ('Content-length', str(len(body)))])
    return [body]


def roster(environ, start_response):
    """Roster retrieve or update."""
    form = cgi.FieldStorage(fp=environ['wsgi.input'],
                            environ=environ,
                            keep_blank_values=True)

    jid = form.getvalue('jid')
    password = form.getvalue('password')
    if not jid:
        start_response('403 Forbidden', [('Content-Type', 'text/plain')])
        return ["JID required"]
    if not tools.validate_email(jid):
        start_response('403 Forbidden', [('Content-Type', 'text/plain')])
        return ["JID incorrect"]
    if not password:
        start_response('403 Forbidden', [('Content-Type', 'text/plain')])
        return ["Password required"]
    host = form.getvalue('host')
    port = form.getvalue('port')
    retrieve = form.getvalue('retrieve')
    update = form.getvalue('update')

    if not port:
        port = 5222
    if not host:
        host = tools.get_host_from_email(jid)

    body = ''
    error = False
    if retrieve is not None:
        # retrieve roster
        xmpp = RosterUtility(jid, password)
        if xmpp.connect((host, port), reattempt=False):
            xmpp.process(threaded=False)
            body = xmpp.get_client_roster_as_csv()
        else:
            error = True

    elif update is not None:
        # update roster
        roster = form.getvalue('roster')
        xmpp = RosterUtility(jid, password, roster)
        if xmpp.connect((host, port), reattempt=False):
            xmpp.process(threaded=False)
            body = roster
        else:
            error = True
            
    if error:
        body = 'Unable to connect to XMPP server.'
        start_response('500 Internal Server Error', [('Content-Type', 'text/plain'), ('Content-length', str(len(body)))])
    else:
        start_response('200 OK', [('Content-Type', 'text/plain'), ('Content-length', str(len(body)))])
        
    return [str(body)]


def static(environ, start_response):
    """Serve static files"""
    
    def send_file(file_path, size):
        """Generator that yields chunks of static files so they don't have to be loaded into memory."""
        BLOCK_SIZE = 1024
        with open(file_path) as f:
            block = f.read(BLOCK_SIZE)
            while block:
                yield block
                block = f.read(BLOCK_SIZE)

    file_path = environ.get('PATH_INFO', '').lstrip('/')
    pyjru_path = environ.get('PYJRU_PATH', '').lstrip('/')
    if pyjru_path:
        pyjru_path += '/'
    try:
        size = os.path.getsize(pyjru_path + file_path)
    except Exception as e:
        start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
        return ['Not Found']
    mimetype = mimetypes.guess_type(pyjru_path + file_path)[0]

    start_response('200 OK', [('Content-Type', mimetype), ('Content-length', str(size))])
    return send_file(pyjru_path + file_path, size)


def not_found(environ, start_response):
    """Called if no URL matches."""
    start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
    return ['Not Found']


# map urls to functions
urls = [
    (r'^$', index),
    (r'roster/?$', roster),
    (r'static/(.+)$', static),
]


def application(environ, start_response):
    """
    The main WSGI application. Dispatch the current request to
    the functions from above.

    If nothing matches call the `not_found` function.
    """
    path = environ.get('PATH_INFO', '').lstrip('/')
    for regex, callback in urls:
        match = re.search(regex, path)
        if match is not None:
            return callback(environ, start_response)
    return not_found(environ, start_response)


if __name__ == '__main__':

    from optparse import OptionParser
    from wsgiref.simple_server import make_server

    optp = OptionParser()
    optp.add_option("-P", "--port", dest="port", type="int", default=8080,
                    help="port to use (default: 8080)")
    optp.add_option("-H", "--host", dest="host", default="127.0.0.1",
                    help="host name or IP to use (default: 127.0.0.1)")
    opts,args = optp.parse_args()

    srv = make_server(opts.host, opts.port, application)
    print "Server started, use Ctrc+C to stop server"
    print "You can now visit: http://%s:%d/" % (opts.host, opts.port)
    print
    srv.serve_forever()
