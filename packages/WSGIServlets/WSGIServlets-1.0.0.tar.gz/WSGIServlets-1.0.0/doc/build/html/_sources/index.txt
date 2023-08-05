.. WSGIServlets documentation master file, created by
   sphinx-quickstart on Wed Sep 28 10:19:08 2011.  You can adapt this
   file completely to your liking, but it should at least contain the
   root `toctree` directive.

.. currentmodule:: wsgiservlets


WSGIServlets Documentation
==========================


Welcome to WSGIServlets!  If you're looking for a hands-on overview of
WSGIServlets you should run the tutorial, which is included in all
source distributions::

   $ cd tutorial
   $ ./runtutorial
   Starting the tutorial on port: 8000
   In your browser, visit http://localhost:8000/

The script accepts an optional argument for the port number, so if
port 8000 is used on your host you can run it on another port::

   $ ./runtutorial 8888
   Starting the tutorial on port: 8888
   In your browser, visit http://localhost:8888/
   
As the output of the script indicates, you then go to your favorite
browser and visit the url to read the tutorial.  There are links on
every page of the tutorial for viewing this manual.


Contents:

.. toctree::
   :maxdepth: 2

   wsgiservlets.WSGIServlet
   wsgiservlets.HTMLPage
   wsgiservlets.Dispatcher
   wsgiservlets.JSONRPCServer
   wsgiservlets.HTTPResponse
   wsgiservlets.Session
   

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
