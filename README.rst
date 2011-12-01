Python Jabber Roster Utility
############################

This is `Python <http://python.org/>`_ version of `Jabber Roster Utility <http://beta.unclassified.de/projekte/jru-php/>`_ with some additional features like specifying connection host and port, ability to find host from domain's SRV records, using AJAX requests and more. It is written using `SleekXMPP <https://github.com/fritzy/SleekXMPP>`_ library.
With this tool, you can manage your Jabber roster: add, remove and alter items in a large scale.



Requirements
------------

 - `SleekXMPP <https://github.com/fritzy/SleekXMPP>`_
 - `dnspython <http://www.dnspython.org/>`_ (optional)

 

Installation
------------
Install SleekXMPP and optionally dnspython (read more about installation of both `here <https://github.com/fritzy/SleekXMPP/blob/master/README.rst>`_)::

  pip install sleekxmpp
  pip install dnspython

Grab pyJRU from github: https://github.com/barszczmm/pyJRU/tarball/master



Usage
-----

**As command line tool:**

  For getting roster and printing it to stdout::

    cd pyjru
    python jabber.py jid password

  For updating roster from stdin::

    cd pyjru
    python jabber.py jid password < roster_file

  Check more options::

    cd pyjru
    python jabber.py --help

**As web tool:**

  You can easily run simple server that serves web application::

    cd pyjru
    python server.py

  Check more options::

    cd pyjru
    python server.py --help

**Serving application for public:**

  You should not use above method if you want to serve this app somewhere on the web so anyone can use it. For this you should use some application server that can serve `wsgi <http://www.wsgi.org/en/latest/index.html>`_ applications. There are sample configuration files for `uwsgi <http://projects.unbit.it/uwsgi/>`_ and `nginx <http://nginx.org/>`_ setup in ``hosting_conf`` directory.



Credits
-------
**Main Author:** Maciej 'barszcz' Marczewski
    `www.barszcz.info <http://www.barszcz.info>`_

