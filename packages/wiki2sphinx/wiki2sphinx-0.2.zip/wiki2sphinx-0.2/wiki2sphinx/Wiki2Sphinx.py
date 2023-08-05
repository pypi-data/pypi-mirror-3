#!/usr/bin/env python
"""
    wiki2sphinx
    -----------
    
    converts wiki rst pages to sphinx document structure

    :copyright: 2011 by Henning Fleddermann
    :license: GNU GPL, see COPYING for details.
"""
import argparse
import codecs
import getpass
import os
import shutil
import sys
import wiki2sphinx


def main():
    parser = argparse.ArgumentParser(description='send files to a wiki')
    parser.add_argument('-w', '--wikiurl', dest="wikiurl", type=str, default="http://localhost:8080", required=True,
                       help='url of the wiki to send to')
    parser.add_argument('-p', '--prefix', dest='prefix', required=True, nargs="+",
                       help='space-delimited list of the wiki pages to get. the first one determines the document-structure')
    parser.add_argument('-u', '--username', dest='username', required=True,
                       help='name of the user in that wiki')
    parser.add_argument('-r', '--recursive', dest='recursive', action='store_true', required=False,
                       help='use recursive algorithm to download only the needed pages. warning: might get stuck on back-links')

    args = parser.parse_args()
    password = getpass.getpass("password: ")
    prefix = args.prefix
    sphinx_dir = os.path.join(os.path.abspath(os.path.dirname(wiki2sphinx.__file__)), 'sphinx')
    if not os.path.exists(wiki2sphinx.SPHINX_SOURCE_DIR):
        shutil.copytree(sphinx_dir, './sphinx')
    wikigetter = wiki2sphinx.WikiGetter(prefix[0], args.username, password, args.wikiurl)
    if args.recursive:
        pages = wikigetter.get_pagenames_recursive(prefix[0])
    else:
        pages = wikigetter.get_pagenames()
    pages.extend(prefix)
    for page in pages:
        print page
        wikigetter.get_attachments(page)
        wikigetter.get_and_write_page(page)
    include_name = prefix[0].split('/')[-1]
    index_rst = wiki2sphinx.INDEX % {"include_name": include_name}

    fid = codecs.open(os.path.join(wiki2sphinx.SPHINX_SOURCE_DIR, "index.rst"), 'wb')
    fid.write(index_rst)
    fid.close()
    
if __name__ == '__main__':
    sys.exit(main())
