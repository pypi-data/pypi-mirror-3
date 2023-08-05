from __future__ import division, absolute_import

import os.path
import posixpath
import tempfile
from urllib import urlencode
from urlparse import urlunparse

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.parsers.rst import Directive



class youtube_node(nodes.General, nodes.Element):
    pass

class YouTubeDirective(Directive):

    """Embeds a youtube video in the document.
    
    Used like this:
   
    .. youtube:: 0tgzdefY4
       :time: 2m43s
       :size: {small,[medium],large,xl} # TODO
       :width: 800 # TODO
       :height: 450 # TODO
       :ssl: false # TODO
       :hd: false # TODO
    """
    
    has_content = False
    required_arguments = 1
    optional_arguments = 0

    option_spec = {
        'time': directives.unchanged
    }

    def run(self):
        """Do it."""

        node = youtube_node()
	node['video'] = self.arguments[0]
        node['time'] = self.options.get('time', None)
        return [node]

    @staticmethod
    def parse_time(self):
	# This method is here to allow multiple time formats, once it's
	# fleshed out.  Currently time must be in XmYYs format.
	return time



def build_youtube_url(node):
    if getattr(node, 'ssl', False) == True:
	scheme = 'https'
    else:
	scheme = 'http'
    path = '/embed/%s' % node['video']
    args = {}
    time = node.get('time', None)
    if time:
	args['start'] = time
    url = urlunparse((scheme, 'youtube.com', path, None, urlencode(args), None))
    print url
    return url

# HTML Visitor for youtube nodes
def html_visit_youtube_node(self, node):
    url = build_youtube_url(node)
    self.body.append(self.starttag(node, 'iframe', width=640, height=360, CLASS='youtube', src=url, frameborder='0', allowfullscreen='allowfullscreen'))
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
