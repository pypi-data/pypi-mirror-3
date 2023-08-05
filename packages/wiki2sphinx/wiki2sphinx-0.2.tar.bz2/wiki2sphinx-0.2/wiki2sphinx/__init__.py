#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    WikiGetter
    ----------
    
    gets pages and attachments from a wiki 
    
    :copyright: 2011 by Henning Fleddermann
    :license: GNU GPL, see COPYING for details.
"""

import xmlrpclib
import re
import codecs
import os
import shutil
from wiki2sphinx import placeholders

INDEX = """.. include:: %(include_name)s.rst"""
SPHINX_SOURCE_DIR = "./sphinx/source/"

class WikiGetter(object):
    
    offset = 0
    
    def __init__(self, prefix="", name="", password="", wikiurl=""):
        self.prefix = prefix
        self.name = name
        self.password = password
        self.wikiurl = wikiurl
        self.offset = prefix.rfind("/") + 1
    
    def get_pagenames(self):
        mc = self.get_mc()
        opts = {"include_system": False, "include_underlay": False, "prefix": self.prefix}
        mc.getAllPagesEx(opts)
        result = mc()
        return tuple(result)[1]
    
    def get_pagenames_recursive(self, pagename):
        mc = self.get_mc()
        pages = []
        mc.getPage(pagename)
        try:
            result = tuple(mc())
        except xmlrpclib.Fault:
            return []
        pages.append(pagename)
        success = result[0]
        raw = result[1]
        if success:
            m = re.finditer(r"`(.*)<(.*)>`_", raw)
            for match in m:
                if match.group(2)[0] == "/": # relative path
                    pages.extend(self.get_pagenames_recursive(pagename + match.group(2)))
                else: # absolute path
                    pages.extend(self.get_pagenames_recursive(match.group(2)))
        return pages

    def get_mc(self):
        homewiki = xmlrpclib.ServerProxy(self.wikiurl + "?action=xmlrpc2", allow_none=True)
        auth_token = homewiki.getAuthToken(self.name, self.password)
        mc = xmlrpclib.MultiCall(homewiki)
        mc.applyAuthToken(auth_token)
        return mc
    
    def make_path(self, file):
        d = os.path.dirname(file)
        try:
            os.makedirs(d)
        except OSError:
            pass
    
    def parse_page(self, text):
        pattern = re.compile(r"^##links2image (.*)$", re.M)
        m = pattern.search(text)
        if m:
            img_pattern = re.compile("`<(%s)>`_" % m.group(1))
            img_m = img_pattern.search(text)
            while img_m:
                text = "%s.. figure:: %s.pdf%s" % (text[:img_m.start()], img_m.group(1), text[img_m.end():])
                img_m = img_pattern.search(text)
        pattern = re.compile(r"^#.*$\n?", re.M)
        m = pattern.search(text)
        while m:
            text = "%s%s" % (text[:m.start()], text[m.end():])
            m = pattern.search(text)
        return text
    
    def replace_links(self, pagename, text):
        pattern = re.compile("`(.*)<(.*)>`_") # ToDo: fix links like `</CvMartinKaufmann>`_ 
        offset = pagename.rfind("/") + 1
        m = pattern.search(text)
        while m:
            if m.group(2)[0]=="/": # relativer Pfad
                text = "%s.. include:: %s.rst%s" % (text[:m.start()], pagename[offset:]+m.group(2), text[m.end():])
            else: # absoluter Pfad -> uebersetzen in relativen
                text = "%s.. include:: %s.rst%s" % (text[:m.start()], m.group(2)[offset:], text[m.end():])
            m = pattern.search(text)
        return text
    
    def replace_img_links(self, text):
        matches = re.finditer(".. (figure|image):: (\S*)", text)
        for m in matches:
            filename = self.workaround_sphinx_filenames(m.group(2))
            old_filename = filename
            filename = filename.rpartition("/")[2] # Haaack
            filename = filename + " "*(len(old_filename) - len(filename))
            filename_parts = filename.rpartition(".")
            if os.path.exists(os.path.join(SPHINX_SOURCE_DIR, filename_parts[0] + ".pdf")): # always prefer pdfs if they exist
                filename = filename_parts[0] + ".pdf"
                filename = filename + " "*(len(old_filename) - len(filename))
            elif os.path.exists(os.path.join(SPHINX_SOURCE_DIR, filename.rstrip())):
                pass
            else:
                file_ending = filename_parts[2].rstrip()
                if file_ending == "pdf":
                    dummy = placeholders.PDF_DUMMY
                elif file_ending == "svg":
                    dummy = placeholders.SVG_DUMMY
                else:
                    dummy = placeholders.PNG_DUMMY
                self.make_path(os.path.join(SPHINX_SOURCE_DIR, filename.rstrip()))
                shutil.copy(dummy, os.path.join(SPHINX_SOURCE_DIR, filename.rstrip()))
            text = "%s.. %s:: %s%s" % (text[:m.start()], m.group(1), filename, text[m.end():])
        return text

    def workaround_sphinx_filenames(self, filename):
        parts = list(filename.rpartition("."))
        parts[0] = parts[0].replace(".","_")
        return "".join(parts)
    
    def get_attachments(self, pagename):
        mc = self.get_mc()
        mc.listAttachments(pagename)
        result = tuple(mc())
        if result[0]:
            for attachment in result[1]:
                self.get_attachment(pagename, attachment)
    
    def get_attachment(self, pagename, attachment):
        mc = self.get_mc()
        mc.getAttachment(pagename, attachment)
        result = tuple(mc())
        if result[0]:
            fid = open(os.path.join(SPHINX_SOURCE_DIR, self.workaround_sphinx_filenames(attachment)), "wb") # WARNING: attachments have to be in the root-source directory. this might lead to file-name collision.
            fid.write(result[1].data)
            fid.close()
    
    def get_and_write_page(self, pagename):
        mc = self.get_mc()
        mc.getPage(pagename)
        result = tuple(mc())
        if result[0]:
            text = result[1]
            self.make_path(os.path.join(SPHINX_SOURCE_DIR, pagename[self.offset:]))
            f = codecs.open(os.path.join(SPHINX_SOURCE_DIR, pagename[self.offset:] + ".rst"), "wb", encoding="utf-8") # append .rst to real prefix to avoid file/directory-name collision. haaack :)
            text = self.parse_page(text)
            text = self.replace_links(pagename, text)
            text = self.replace_img_links(text)
            f.write(text)
            f.close()

