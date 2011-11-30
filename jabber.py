#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
import csv

import sleekxmpp
from sleekxmpp.exceptions import IqError, IqTimeout


class RosterUtility(sleekxmpp.ClientXMPP):

    def __init__(self, jid, password, roster_csv=None):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use. We want to
        # listen for this event so that we we can intialize
        # our roster. We need threaded=True so that the
        # session_start handler doesn't block event processing
        # while we wait for presence stanzas to arrive.
        self.add_event_handler("session_start", self.start, threaded=True)
        self.add_event_handler("changed_status", self.wait_for_presences)

        self.received = set()
        self.presences_received = threading.Event()

        self.roster_csv = roster_csv

    def get_client_roster_as_csv(self):
        ret_str = ''
        for jid in self.client_roster:
            name = self.client_roster[jid]['name']
            if name.find(',') != -1:
                name = '"%s"' % name
            if not name:
                name = ''
            sub = self.client_roster[jid]['subscription']
            groups = ','.join(map(lambda x: x if x.find(',') == -1 else '"'+x+'"', self.client_roster[jid]['groups']))
            ret_str += '+,%s,%s,%s,%s\n' % (jid, name, sub, groups)
        return ret_str

    def start(self, event):
        """
        Process the session_start event.

        Typical actions for the session_start event are
        requesting the roster and broadcasting an intial
        presence stanza.

        Arguments:
            event -- An empty dictionary. The session_start
                     event does not provide any additional
                     data.
        """
        try:
            self.get_roster()
        except IqError as err:
            print('Error: %' % err.iq['error']['condition'])
        except IqTimeout:
            print('Error: Request timed out')

        if self.roster_csv is not None:
            csv_reader = csv.reader(self.roster_csv.split('\n'))
            for jid in csv_reader:
                if len(jid):
                    if jid[0] == '+':
                        groups = []
                        for i in range(4, len(jid)):
                            groups.append(jid[i])
                        self.update_roster(jid[1], name=jid[2], subscription=jid[3], groups=groups)
                    elif jid[0] == '-':
                        self.del_roster_item(jid[1])

        self.send_presence()

        self.presences_received.wait(5)

        self.disconnect(False)

    def wait_for_presences(self, pres):
        """
        Track how many roster entries have received presence updates.
        """
        self.received.add(pres['from'].bare)
        if len(self.received) >= len(self.client_roster.keys()):
            self.presences_received.set()
        else:
            self.presences_received.clear()



if __name__ == '__main__':

    import sys
    import logging
    from optparse import OptionParser

    import tools

    # Python versions before 3.0 do not use UTF-8 encoding
    # by default. To ensure that Unicode is handled properly
    # throughout SleekXMPP, we will set the default encoding
    # ourselves to UTF-8.
    if sys.version_info < (3, 0):
        reload(sys)
        sys.setdefaultencoding('utf8')


    # Setup the command line arguments.
    optp = OptionParser(usage="Usage: %prog [options] jid password")
    optp.add_option('-q','--quiet', help='set logging to ERROR',
                    action='store_const',
                    dest='loglevel',
                    const=logging.ERROR,
                    default=logging.ERROR)
    optp.add_option('-d','--debug', help='set logging to DEBUG',
                    action='store_const',
                    dest='loglevel',
                    const=logging.DEBUG,
                    default=logging.ERROR)
    optp.add_option('-v','--verbose', help='set logging to COMM',
                    action='store_const',
                    dest='loglevel',
                    const=5,
                    default=logging.ERROR)

    # Port and server options
    optp.add_option("-P", "--port", dest="port", type="int", default=5222,
                    help="port to use (default: 5222)")
    optp.add_option("-H", "--host", dest="host",
                    help="host name to use")

    opts,args = optp.parse_args()

    if len(args) != 2:
        optp.print_help()
        sys.exit(1)

    # Setup logging.
    logging.basicConfig(level=opts.loglevel,
                        format='%(levelname)-8s %(message)s')

    jid = args[0]
    password = args[1]

    if not tools.validate_email(jid):
        print 'Invalid JID:', jid
        sys.exit(1)

    if not opts.host:
        opts.host = tools.get_host_from_email(jid)

    roster_csv = None
    if not sys.stdin.isatty():
        roster_csv = sys.stdin.read()

    xmpp = RosterUtility(jid, password, roster_csv)

    # If you are working with an OpenFire server, you may need
    # to adjust the SSL version used:
    # xmpp.ssl_version = ssl.PROTOCOL_SSLv3

    # If you want to verify the SSL certificates offered by a server:
    # xmpp.ca_certs = "path/to/ca/cert"

    # Connect to the XMPP server and start processing XMPP stanzas.
    if xmpp.connect((opts.host, opts.port), reattempt=False):
        # If you do not have the pydns library installed, you will need
        # to manually specify the name of the server if it does not match
        # the one in the JID. For example, to use Google Talk you would
        # need to use:
        #
        # if xmpp.connect(('talk.google.com', 5222)):
        #     ...
        xmpp.process(threaded=False)
        if not roster_csv:
            print xmpp.get_client_roster_as_csv()
    else:
        print("Unable to connect.")

