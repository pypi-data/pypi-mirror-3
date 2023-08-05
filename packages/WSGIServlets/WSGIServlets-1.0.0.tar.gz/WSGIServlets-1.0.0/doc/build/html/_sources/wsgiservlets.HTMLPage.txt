wsgiservlets.HTMLPage
=====================

.. role:: boldred

.. raw:: html

    <style type="text/css">.boldred{color: red;font-weight:bolder}</style>


``HTMLPage`` generates well-formed HTML documents and has many
methods and attributes to make generating web pages and processing
form data easy.

Here's a simple example::

    from wsgiservlets import *

    class helloworld(HTMLPage):
	title = 'Hello, World!'
	css = 'strong {color: red}'

	def write_content(self):

	    self.writeln("Here's a simple demo to say "
			 "<strong>Hello, World</strong>!")

    
The ``helloworld`` servlet will generate a HTML page with title
*Hello, World!* and writes to the page:

______________________________________________________________________


    Here's a simple demo to say :boldred:`Hello, World`!

______________________________________________________________________


The tutorial that comes with the distribution has several examples of
how to exploit the attributes and methods of ``HTMLPage`` to generate
dynamic code **simply**!

API:

.. currentmodule:: wsgiservlets

.. autoclass:: HTMLPage
   :members:
   :member-order: bysource

   .. automethod:: _lifecycle
   
   
   
