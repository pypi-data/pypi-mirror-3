FileServer
===========

a simple static fileserver and directory index server in python (WSGI app)

About
-----

Often for testing you will want a static fileserver and directory
index as part of your WSGI stack.  In addition, you may have
requirements to run such as part of a production WSGI
stack. FileServer fits these needs.

Motivation
----------

I needed a directory index server a la Apache to test a PyPI clone I
was using.  After surveying what was out there, there didn't seem
anything out there that was easily consumable for my purposes.  So I
wrote one only depending on
`webob <http://www.webob.org/>`_ .

Contents
--------

``from fileserver import *`` should give you access to all of the
usable components of fileserver:

 * ``file_response``: return a webob response object appropriate to a
   file name
 * ``FileApp``: WSGI app that wraps ``file_response``
 * ``Directory Server``: serves a directory tree and generated indices
 * ``main``: command line entry point

``FileApp`` and ``file_response`` are heavily borrowed from
http://docs.webob.org/en/latest/file-example.html though the example
there is more complete.  I will work on making this more thorough
going forward.  I also borrowed from Paste's ``StaticURLParser`` and
``static.Cling``.

In addition there is a command line script, ``serve``, which may be
used to serve a directory with the
`wsgiref <http://docs.python.org/library/wsgiref.html>`_ server.

Other Projects
--------------

While I didn't find them suitable for my use, there are other
standalone static fileservers available for python:

 * `static <http://lukearno.com/projects/static/>`_

 * `Paste <http://pythonpaste.org/modules/urlparser.html>`_ ``StaticURLParser``

 * `SimpleHTTPServer <http://docs.python.org/library/simplehttpserver.html>`_

----

Jeff Hammel

http://k0s.org/hg/FileServer
