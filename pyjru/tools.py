#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

email_re = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"' # quoted-string
    r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.IGNORECASE)  # domain

def validate_email(email):
    if email_re.match(email):
        return True
    else:
        return False

def get_host_from_email(email):
    return email[email.find('@')+1:]

if __name__ == '__main__':
    import sys
    email = sys.argv[1]
    
    if validate_email(email):
        print email, "- valid email"
    else:
        print email, "- invalid email"

    print email, "- extracted host:", get_host_from_email(email)
