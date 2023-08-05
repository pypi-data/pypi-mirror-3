#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    ExampleWiki - creates a set of pages for a Wiki
                  with different ACLs per page set
    

    :copyright: 2011 ReimarBauer
    :license: GnuGPL
"""


import argparse
import getpass
import sys

from Wiki_XMLRPC_Extensions import Wiki_XMLRPC


MAPPING = {
           # Maps Instrument to Group name (for accessing the page)
           "FISH": "FzjGroup",
           "FSSP": "UniMainzGroup",
           "FRIDGE": "UniFrankfurtGroup",
           "AVIONIK": "AvionikGroup",
           }


MAIN_CONTENT = """#acl %(group)s:read,write,delete,revert UserGroup:read

<<TableOfContents>>
= %(instrument)s =

== PIs ==

== Instruments Description ==

== Data ==
<<ListPages(search_term="Instruments/%(instrument)s/Flight.*", link=subpage,list_type=bullet_list)>>

----
CategoryInstrument
"""

FULLACCESS_CONTENT = """#acl %(group)s:read,write,delete,revert UserGroup:read

Here our public data from the testflight

(!) For uploading files click <<Action(AttachFile)>> and for further information read [[HelpOnActions/AttachFile]].



<<AttachList>>

== Plots ==
{{{#!arnica show_tools=0,show_date=0,thumbnail_width=320
}}}


"""

RESTRICTED_CONTENT = """#acl %(group)s:read,write,delete,revert UserGroup: All:

Here our data from Flight%(number)d  


(!) For uploading files click <<Action(AttachFile)>> and for further information read [[HelpOnActions/AttachFile]].


<<AttachList>>

== Plots ==
{{{#!arnica show_tools=0,show_date=0,thumbnail_width=320
}}}
"""


def setup_instrument_pages_for_a_wiki(args, password):

    xmlrpc_init = Wiki_XMLRPC(args.wikiurl, args.username, password)
    if xmlrpc_init.auth_token:
        keys = MAPPING.keys()
        content = """<<Navigation(children)>>

(!) Add your content here.

"""
        xmlrpc_init.send_page("Instruments", content)
        for key in keys:
            pagename = "Instruments/%s" % key
            instrument_page = MAIN_CONTENT % {
                                              "group": MAPPING[key],
                                              "instrument": key,
                                              }
            xmlrpc_init.send_page(pagename, instrument_page)
            pagename = "Instruments/%s/Flight1" % key
            test_flight_page = FULLACCESS_CONTENT % {
                                                     "group": MAPPING[key]
                                                    }

            xmlrpc_init.send_page(pagename, test_flight_page)
            for index in range(7)[2:]:
                pagename = "Instruments/%s/Flight%d" % (key, index)
                if not key == "AVIONIK":
                    flight_page = RESTRICTED_CONTENT % {
                                                    "group": MAPPING[key],
                                                    "number": index
                                                    }
                else:
                    flight_page = FULLACCESS_CONTENT % {
                                                     "group": MAPPING[key]
                                                    }
                xmlrpc_init.send_page(pagename, flight_page)
            return "INFO: Done"
    else:
        return "ERROR: Check your credentials!"

def main():
    parser = argparse.ArgumentParser(description='send files to a wiki')
    parser.add_argument('-w', '--wikiurl', dest="wikiurl", type=str, required=True,
                       help='url of the wiki to send to')
    parser.add_argument('-u', '--username', dest='username', required=True,
                       help='name of the user in that wiki')
    args = parser.parse_args()
    password = getpass.getpass("password: ")

    print setup_instrument_pages_for_a_wiki(args, password)

if __name__ == "__main__":
    sys.exit(main())

