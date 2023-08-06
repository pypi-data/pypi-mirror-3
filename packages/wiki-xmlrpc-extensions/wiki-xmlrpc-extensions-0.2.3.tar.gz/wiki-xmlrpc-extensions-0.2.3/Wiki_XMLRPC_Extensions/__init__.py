# -*- coding: iso-8859-1 -*-

"""
    Wiki_XMLRPC_Extensions
    ----------------------

    toolset for xmlrpc requests using a MoinMoin wiki. Includes send and receive attachments, get and put pages etc. 
    
    most of this is copied from 
    https://coconuts.icg.kfa-juelich.de/hg/coconuts-0.4/file/2ced0001c0d5/Coconuts/xmlrpc/__init__.py

    :copyright: 2010-2011 by ReimarBauer
    :license: GNU GPL, see COPYING for details.
"""

import logging
import os
import re
import xmlrpclib


def taintfilename(basename):
    """
    from MoinMoin - Wiki Utility Functions

    Make a filename that is supposed to be a plain name secure, i.e.
    remove any possible path components that compromise our system.

    :param basename: (possibly unsafe) filename
    :rtype: string
    :return: (safer) filename
    
    :copyright: 2000-2004 Juergen Hermann <jh@web.de>,
                2004 by Florian Festi,
                2006 by Mikko Virkkil,
                2005-2008 MoinMoin:ThomasWaldmann,
                2007 MoinMoin:ReimarBauer
    :license: GNU GPL, see COPYING for details.
    """
    for x in (os.pardir, ':', '/', '\\', '<', '>'):
        basename = basename.replace(x, '_')

    return basename

class Wiki_XMLRPC(object):
    """
    base class for communication with a wiki
    """
    def __init__(self, wikiurl, username, password):
        """
        initializes a XmlRpc object

        :param wikurl: url to the wiki
        :param username: username to login in wiki
        :param password: password for username
        """
        self.wiki = xmlrpclib.ServerProxy(wikiurl + "?action=xmlrpc2",
                                          allow_none=True)
        self.auth_token = self.wiki.getAuthToken(username, password)

    def send_attachment(self, pagename, attachname, datafile):
        """
        sends a file to a wiki pagename

        :param pagename: name of the wikipage
        :param attachname: name of the attachment
        :param datafile: file like object of data for attachment
        """
        mc = xmlrpclib.MultiCall(self.wiki)
        mc.applyAuthToken(self.auth_token)
        data = xmlrpclib.Binary(datafile.read())
        mc.putAttachment(pagename, attachname, data)
        try:
            result = mc()
        except xmlrpclib.ProtocolError, err:
            logging.debug("Error: %s Pagename: %s Name: %s" % (err, pagename, name))
            result = xmlrpclib.Fault(1, "Upload of file content failed")
        return result

    def send_page(self, pagename, text):
        """
        sends text to a wiki page

        :param pagename: wikipagename to write to
        :param text: text to write on the wiki page
        """
        mc = xmlrpclib.MultiCall(self.wiki)
        mc.applyAuthToken(self.auth_token)
        mc.putPage(pagename, text)
        try:
            result = mc()
        except xmlrpclib.ProtocolError, err:
            logging.debug("Error: %s Pagename: %s" % (err, pagename))
            result = xmlrpclib.Fault(1, "Upload of page content failed")
        return result

    def attachments_list(self, pagename):
        """
        lists attachments of a wiki page

        :param pagename: name of wiki page
        """
        mc = xmlrpclib.MultiCall(self.wiki)
        mc.applyAuthToken(self.auth_token)
        mc.listAttachments(pagename)
        try:
            msg, attachments = tuple(mc())
        except (xmlrpclib.Fault, xmlrpclib.ProtocolError), err:
            logging.debug("Error: %s Pagename: %s" % (err, pagename))
            return []
        return attachments

    def attachment_exists(self, pagename, attachname):
        """
        checks if attachment on page exists

        :param pagename: name of page
        :param attachname: name of attachment
        """
        attachments = self.attachments_list(pagename)
        return attachname in attachments

    def get_attachment(self, pagename, attachname):
        """
        gets attachment from wiki page

        :param pagename: name of wiki page
        :param attachname: name of attachment
        """
        if self.attachment_exists(pagename, attachname):
            mc = xmlrpclib.MultiCall(self.wiki)
            mc.applyAuthToken(self.auth_token)
            mc.getAttachment(pagename, attachname)
            msg, data = mc()
            return data.data

    def get_package(self, pagename):
        """
        gets a Package of a page with all attachments from a MoinMoin wiki
        this requires a plugin http://hg.moinmo.in/moin/extensions/file/tip/data/plugin/xmlrpc/getPackage.py

        :param pagename: name of wiki page
        """
        mc = xmlrpclib.MultiCall(self.wiki)
        mc.applyAuthToken(self.auth_token)
        mc.getPackage(pagename)
        try:
            msg, data = mc()
            return data.data
        except xmlrpclib.Fault, err:
            logging.debug("Error: %s Pagename: %s" % (err, pagename))
            return []

    def get_page(self, pagename):
        """
        gets the raw text of a wiki page

        :param pagename: name of page
        """
        mc = xmlrpclib.MultiCall(self.wiki)
        mc.applyAuthToken(self.auth_token)
        mc.getPage(pagename)
        try:
            msg, data = mc()
            return data
        except xmlrpclib.Fault, err:
            logging.debug("Error: %s Pagename: %s" % (err, pagename))
            return ""

    def get_html_page(self, pagename):
        """
        gets the html content of the page. Requesting a html rendered page
        creates all cache files.

        :param pagename: name of wiki page
        """
        mc = xmlrpclib.MultiCall(self.wiki)
        mc.applyAuthToken(self.auth_token)
        mc.getPageHTML(pagename)
        try:
            msg, data = mc()
            return data
        except xmlrpclib.Fault, err:
            logging.debug("Error: %s Pagename: %s" % (err, pagename))
            return ""

    def get_orphaned_attachments(self, pagename):
        """
        gets a list of attachments orphaned on a page

        :param pagename: name of wiki page
        """
        page_attachments = self.attachments_list(pagename)
        html_text = self.get_page(pagename)
        # regex for extracting images
        img_regex = re.compile(ur'\<\<Image\((?P<value>.*?\S*)\)\>\>', re.MULTILINE | re.UNICODE)
        images = [match.groups()[0].strip('"') for match in img_regex.finditer(html_text)]
        att_regex = re.compile(ur'(?:attachment|drawing)\:(?P<value>.*?\S*)(?:}}|]])', re.MULTILINE | re.UNICODE)
        attachments = [match.groups()[0].strip('"').strip("'") for match in att_regex.finditer(html_text)]
        return list(set(page_attachments) - set(images + attachments))

    def delete_attachment(self, pagename, attachment):
        """
        deletes attachment from a wiki page

        :param pagename: name of wiki page
        :param attachment: name of attachment
        """
        mc = xmlrpclib.MultiCall(self.wiki)
        mc.applyAuthToken(self.auth_token)
        for name in attachment:
            mc.deleteAttachment(pagename, name)
        try:
            msg = mc()
        except xmlrpclib.Fault, err:
            logging.debug("Error: %s Pagename: %s" % (err, pagename))
        return "Done"

    def receive_files(self, pagename, path='./', file_filter='.*'):
        """
        fetches all files by the given filter of a wiki page and downloads to path
        
        :param pagename: name of wiki page
        :param path: path to store to
        :param file_filter: filter expression
        """
        if self.auth_token:
            all_attachments = self.attachments_list(pagename)
            filter_obj = re.compile(file_filter)
            files = filter(filter_obj.search, all_attachments)
            if not os.path.exists(path):
                os.makedirs(path)
            for attachment in files:
                data = self.get_attachment(pagename, attachment)
                logging.info('downloading from wikipage: "%(pagename)s" file: "%(attachment)s" to path: "%(path)s"' % {"pagename": pagename,
                                                                                                            "attachment": attachment,
                                                                                                            "path": path
                                                                                                            })
                fid = open(os.path.join(path, taintfilename(attachment)), "wb")
                fid.write(data)
                fid.close()
            return True
        else:
            logging.error("Error: Check your credentials!")
            return False

    def send_files(self, pagename=None, path='./', file_filter='.*', page_text=None, skip_page_update=False):
        """
        uploads all files matching the given filter expression from a local storage path to a wiki page
        
        :param pagename: name of wiki page
        :param path: path to read from
        :param file_filter: filter expression
        :param skip_page_update: if set page_text is not written to page
        """
        if self.auth_token and pagename:
            if not os.path.exists(path):
                return "ERROR: No such file or directory: %s" % path
            all_attachments = os.listdir(path)
            filter_obj = re.compile(file_filter)
            files = filter(filter_obj.search, all_attachments)
            if not files:
                return "ERROR: Check filter or path, nothing to submit"
            for filename in files:
                fid = open(os.path.join(path, filename), "rb")
                flag = self.send_attachment(pagename, filename, fid)
                fid.close()
            if page_text and not skip_page_update:
                flag = self.send_page(pagename, page_text)
                return "INFO: Done and page created: %s" % tuple(flag)[1]
            return "INFO: Done"
        else:
            return "ERROR: Check your credentials!"

    def all_pages(self, opts=None):
        """
        lists all pages a user can access from a wiki
        
        :param opts: dictionary that can contain the following arguments:
                     include_system:: set it to false if you do not want to see system pages
                     include_revno:: set it to True if you want to have lists with [pagename, revno]
                     include_deleted:: set it to True if you want to include deleted pages
                     exclude_non_writable:: do not include pages that the current user may not write to
                     include_underlay:: return underlay pagenames as well
                     prefix:: the page name must begin with this prefix to be included
                     mark_deleted:: returns the revision number -rev_no if the page was deleted.
                        Makes only sense if you enable include_revno and include_deleted.
        """
        if not opts:
            opts = {"include_system": False,
                    "include_underlay": False
                   }
        mc = xmlrpclib.MultiCall(self.wiki)
        mc.applyAuthToken(self.auth_token)
        if self.auth_token:
            mc.getAllPagesEx(opts)
            result = mc()
            return tuple(result)[1]
        else:
            return "ERROR: Check your credentials!"

