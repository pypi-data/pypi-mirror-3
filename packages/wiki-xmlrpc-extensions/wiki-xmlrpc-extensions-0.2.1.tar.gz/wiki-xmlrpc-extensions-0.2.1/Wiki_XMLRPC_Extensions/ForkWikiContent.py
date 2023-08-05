#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    ForkWikiContent - creates a fork of all content of the wiki a user can access
                      (attachments optional) 

    :copyright: 2011 ReimarBauer
    :license: GnuGPL
"""

import argparse
import getpass
import xmlrpclib
import sys
import StringIO

from Wiki_XMLRPC_Extensions import Wiki_XMLRPC

def main():
    parser = argparse.ArgumentParser(description='send files to a wiki')
    parser.add_argument('-w', '--wikiurl', dest="wikiurl", required=True,
                       help='url of the wiki to get pages and attachments')
    parser.add_argument('-f', '--forkiurl', dest="forkurl", required=True,
                       help='url of the wiki to put pages and attachments')
    parser.add_argument('-u', '--username', dest="username", required=True, help="Name of user")
    parser.add_argument('-p', '--prefix', dest="prefix",
                        help="only page names which starts with this prefix become forked")
    parser.add_argument('-a', '--attachments', dest="attachments", default=False, action='store_true',
                        help="downloads also attachments")
    

    args = parser.parse_args()
    opts = {"include_system": False,
            "include_underlay": False,
           }
    if args.prefix:
        opts["prefix"] = args.prefix

    wiki_password = getpass.getpass(args.wikiurl + " Wiki Password: ")
    fork_password = getpass.getpass(args.forkurl + " Wiki Fork Password: ")
    master_wiki = Wiki_XMLRPC(args.wikiurl, args.username, wiki_password)
    fork_wiki = Wiki_XMLRPC(args.forkurl, args.username, fork_password)
    
    all_pages = master_wiki.all_pages(opts)
    if args.prefix:
        all_pages.append(args.prefix)
    for wiki_page in all_pages:
        sys.stdout.write('.')
        sys.stdout.flush()
        attachments = master_wiki.attachments_list(wiki_page)
        wikitext = master_wiki.get_page(wiki_page)
        fork_wiki.send_page(wiki_page, wikitext)
        if args.attachments:
            for attachname in attachments:
                sys.stdout.write('+')
                sys.stdout.flush()
                data = master_wiki.get_attachment(wiki_page, attachname)
                data_buffer = StringIO.StringIO(data)
                fork_wiki.send_attachment(wiki_page, attachname, data_buffer)
                data_buffer.close()

    print ""
    print "Done!"


if __name__ == '__main__':
    sys.exit(main())