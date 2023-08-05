#!/usr/bin/env python


# $Id: rst2html+youtube.py 4564 2006-05-21 20:44:42Z wiemann $
# Author: J. Cliff Dyer <jcd@sdf.lonestar.org>
# Based on rst2html.py by: David Goodger <goodger@python.org>
# Copyright: This module is copyright (c) 2011 under the terms of the MIT 
#            License.

"""
A front end to the Docutils Publisher, registering the YouTubeDirective 
and producing HTML.  Based on rst2html.py by David Goodger, a module in the 
public domain.
"""

try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

from docutils.core import publish_cmdline, default_description

from rstyoutube import setup_docutils

setup_docutils()

description = (
    'Generates (X)HTML documents from standalone reStructuredText '
    'sources, allowing embedding of YouTube videos. ' + default_description)

publish_cmdline(writer_name='html', description=description)
