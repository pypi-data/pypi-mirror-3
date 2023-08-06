#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    receive_files
    ----------
    
    receive files from a wiki page

    :copyright: 2011 by ReimarBauer
    :license: GNU GPL, see COPYING for details.
"""


import argparse
import getpass
import sys
from Wiki_XMLRPC_Extensions import Wiki_XMLRPC


def main():

    parser = argparse.ArgumentParser(description='send files to a wiki')
    parser.add_argument('-w', '--wikiurl', dest="wikiurl", type=str, required=True,
                       help='url of the wiki to send to')
    parser.add_argument('--pagename', dest='pagename', required=True,
                       help='pagename of the wiki to store items')
    parser.add_argument('-u', '--username', dest='username', required=True,
                       help='name of the user in that wiki')
    parser.add_argument('--path', dest='path', default='./', required=True,
                       help='local path where files are located')
    parser.add_argument('--filter', dest='filter', default='.png', required=True,
                       help='regex for file filter')

    args = parser.parse_args()
    password = getpass.getpass("password: ")
    xmlrpc_init = Wiki_XMLRPC(args.wikiurl, args.username, password)
    print xmlrpc_init.receive_files(pagename=args.pagename, path=args.path, file_filter=args.filter)


if __name__ == "__main__":
    sys.exit(main())

