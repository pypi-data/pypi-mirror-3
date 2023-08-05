======
README
======

``rstyoutube`` is a package for embedding youtube videos in reStructuredText
documents.

The code lives at http://bitbucket.org/cliff/rstyoutube.  Bug reports, feature
requests, and contributions are all welcome.  If you find the code useful,
hop on bitbucket and send me a quick message letting me know.

.. To use with sphinx, add 'rstyotube' to your list of extensions.  


To use with pelican or another docutils-based system, add the following to 
your pelican configuration file::

    import rstyoutube
    rstyoutube.setup_docutils()
    
To use rstyoutube in standalone rst files, you can use the included
``rst2html+youtube.py`` script, which should get installed onto your PATH.

In your reST document, include a youtube directive with the video's id as 
the sole argument as follows::

    This is my document

    .. youtube:: 5blbv4WFriM

    Hope you enjoyed the video.

That's all it takes.

Changelog
=========

0.1.0 -- 2011/10/27
-------------------

Initial release


To Do
=====

* Add options to allow people to customize their videos.
