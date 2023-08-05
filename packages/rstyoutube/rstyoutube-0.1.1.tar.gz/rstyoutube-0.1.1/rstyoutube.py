from __future__ import division, absolute_import

import os.path
import posixpath
import tempfile
from urllib import urlencode
from urlparse import urlunparse

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.parsers.rst import Directive


def size_choice(value):
    return directives.choice(value, ('small', 'medium', 'large', 'xlarge'))

def is_true(value):
    if value.lower().startswith('y') or value.lower().startswith('t'):
        return True
    else:
        return False

class youtube_node(nodes.General, nodes.Element):
    pass

class YouTubeDirective(Directive):

    ("""Embeds a youtube video in the document.
    
    Used like this:
   
    .. youtube:: 0tgzdefY4
       :start: 2m43s
       """ # :size: {small,[medium],large,xlarge} # TODO
       """
       :width: 640
       :height: 360
       :ssl: false
       :hd: false
    """)
    
    has_content = False
    required_arguments = 1
    optional_arguments = 0

    option_spec = {
        'start': directives.unchanged,
        #'size': size_choice,
        'width': directives.unchanged,
        'height': directives.unchanged,
        'ssl': directives.flag,
        'hd': directives.flag,
    }

    def run(self):
        """Do it."""

        node = youtube_node()
        node['video'] = self.arguments[0]
        for option in 'start', 'width', 'height':
            if option in self.options:
                node[option] = self.options[option]
        for option in 'hd', 'ssl':
            if option in self.options:
                node[option] = True
            else:
                node[option] = False
        return [node]


def build_youtube_url(node):
    if node['ssl']:
        scheme = 'https'
    else:
        scheme = 'http'
    path = '/embed/%s' % node['video']
    args = {}
    print node
    start = node.get('start', None)
    if start:
        args['start'] = start
    if node['hd']:
        args['hd'] = 1
    url = urlunparse((scheme, 'youtube.com', path, None, urlencode(args), None))
    return url

# HTML Visitor for youtube nodes
def html_visit_youtube_node(self, node):
    url = build_youtube_url(node)
    kwargs = {
        'width': 640,
        'height': 360,
    }
    if node['hd']:
        kwargs['width'] = 1280
        kwargs['height'] = 720

    if 'width' in node:
        kwargs['width'] = node['width']

    if 'height' in node:
        kwargs['height'] = node['height']

    self.body.append(
        self.starttag(node, 'iframe', 
            CLASS='youtube', 
            src=url, 
            frameborder='0', 
            allowfullscreen='allowfullscreen', 
            **kwargs
        )
    )
    self.body.append('</iframe>')

def setup(app):
    """setup method to allow sphinx to embed youtube nodes"""
    app.add_node(youtube_node,
        html=(html_visit_youtube_node, lambda self, node: None),
    )
    app.add_directive('youtube', YouTubeDirective)

def setup_docutils():
    directives.register_directive('youtube', YouTubeDirective)
    from docutils.writers.html4css1 import HTMLTranslator
    setattr(HTMLTranslator, 'visit_youtube_node', html_visit_youtube_node)
    setattr(HTMLTranslator, 'depart_youtube_node', lambda self, node: None)
