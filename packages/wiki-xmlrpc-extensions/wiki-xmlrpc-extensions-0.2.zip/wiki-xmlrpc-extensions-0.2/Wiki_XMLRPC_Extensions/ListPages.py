#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Lists pages of a wiki
---------------------

 :copyright: 2011 by ReimarBauer
 :license: GNU GPL, see COPYING for details.
"""

import argparse
import getpass
import xmlrpclib
import sys
from Wiki_XMLRPC_Extensions import Wiki_XMLRPC

OPTS = {"include_system": False,
        "include_underlay": False
       }


def get_anonymous_readable_pages(args, opts=OPTS):
    wiki = xmlrpclib.ServerProxy(args.wikiurl + "?action=xmlrpc2",
                                 allow_none=True)

    anonymous_readable_pages = wiki.getAllPagesEx(opts)
    return anonymous_readable_pages


def main():
    parser = argparse.ArgumentParser(description='send files to a wiki')
    parser.add_argument('-w', '--wikiurl', dest="wikiurl", required=True,
                       help='url of the wiki for listing pages')
    parser.add_argument('-u', '--username', dest="username", help="Name of user")

    args = parser.parse_args()
    if not args.username:
        print get_anonymous_readable_pages(args, OPTS)
        sys.exit()

    password = getpass.getpass("Password: ")
    xmlrpc_init = Wiki_XMLRPC(args.wikiurl, args.username, password)
    print xmlrpc_init.all_pages(OPTS)

if __name__ == '__main__':
    sys.exit(main())

