#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    SendFiles Sends files as attachment to a wiki page
    --------------------------------------------------

    :copyright: 2011 by ReimarBauer
    :license: GNU GPL, see COPYING for details.
"""


import argparse
import getpass
import sys

from Wiki_XMLRPC_Extensions import Wiki_XMLRPC

def main():
    page_text = """\
#format wiki
<<AttachList>>
"""
    parser = argparse.ArgumentParser(description='gets attachments from a wiki')
    parser.add_argument('-w', '--wikiurl', dest="wikiurl", type=str, required=True,
                       help='url of the wiki to send to')
    parser.add_argument('--pagename', dest='pagename', required=True,
                       help='pagename of the wiki to store items')
    parser.add_argument('-u', '--username', dest='username', required=True,
                       help='name of the user in that wiki')
    parser.add_argument('--path', dest='path', default='./',
                       help='local path where files are located')
    parser.add_argument('--filter', dest='filter', default='.*',
                       help='regex for file filter')
    parser.add_argument('--text', dest='page_text', default=page_text, required=False,
                       help='text to write to the upload wiki page')
    args = parser.parse_args()
    password = getpass.getpass("password: ")
    print args.pagename
    xmlrpc_init = Wiki_XMLRPC(args.wikiurl, args.username, password)
    print xmlrpc_init.send_files(pagename=args.pagename, path=args.path,
                                 file_filter=args.filter, page_text=args.page_text)

if __name__ == "__main__":
    sys.exit(main())

