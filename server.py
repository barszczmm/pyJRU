#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import cgi
import mimetypes
#from string import Template

from jabber import RosterUtility
import tools



def index(environ, start_response):
    #template = Template(open('templates/index.html').read())
    #return [template.substitute(dict(content='Hello World Application'))]
    templates_path = environ.get('TEMPLATES_PATH', 'templates')
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [open(templates_path + '/index.html').read()]


def roster(environ, start_response):
    #parameters = cgi.parse_qs(environ.get('QUERY_STRING', ''))
    #print parameters
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

    ret_str = ''
    if retrieve is not None:
        xmpp = RosterUtility(jid, password)
        if xmpp.connect((host, port)):
            xmpp.process(threaded=False)
            ret_str = xmpp.get_client_roster_as_csv()
        else:
            start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
            return "Unable to connect to XMPP server."

    elif update is not None:
        roster = form.getvalue('roster')
        xmpp = RosterUtility(jid, password, roster)
        if xmpp.connect((host, port)):
            xmpp.process(threaded=False)
            ret_str = roster
        else:
            start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
            return "Unable to connect to XMPP server."

    start_response('200 OK', [('Content-Type', 'text/plain'), ('Content-length', str(len(ret_str)))])
    return [str(ret_str)]


def static(environ, start_response):

    def send_file(file_path, size):
        BLOCK_SIZE = 1024
        with open(file_path) as f:
            block = f.read(BLOCK_SIZE)
            while block:
                yield block
                block = f.read(BLOCK_SIZE)

    file_path = environ.get('PATH_INFO', '').lstrip('/')
    try:
        size = os.path.getsize(file_path)
    except Exception as e:
        start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
        return ['Not Found']
    mimetype = mimetypes.guess_type(file_path)[0]

    start_response('200 OK', [('Content-Type', mimetype), ('Content-length', str(size))])
    return send_file(file_path, size)


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
