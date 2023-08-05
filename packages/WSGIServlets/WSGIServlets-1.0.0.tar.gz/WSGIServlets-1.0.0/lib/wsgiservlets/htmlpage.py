# -*- python -*-

## Copyright 2011 Daniel J. Popowich
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.

import cgi

from wsgiservlets.wsgiservlet import *
from wsgiservlets.constants import *

__all__ = ['HTMLPage']

class _NotDefined:
    pass

class HTMLPage(WSGIServlet):

    """
    ``HTMLPage`` is the servlet that most developers wanting to
    generate HTML will want to subclass.  The
    :meth:`WSGIServlet._lifecycle` method is implemented simply::

            try:
                self.prep()
                if not self.write_html():
                    raise HTTPNoContent
            finally:
                self.wrapup()


    In other words, for each request, first :meth:`prep` is called,
    followed by :meth:`write_html` and, *finally*, :meth:`wrapup`.

    ``prep`` is the place to do any preprocessing of the incoming
    request that might influence how the page is written (e.g., has
    the user logged in?).  ``write_html`` is where content is written.
    ``wrapup`` is a place for post-processing (e.g., logging the
    success or failure of the request).

    Many methods and instance variables offer features to the
    developer to allow the customization of their content.  Use of
    subclassing can produce site-wide continuity of content; e.g., you
    can create a servlet called ``SitePage`` (that inherits from
    ``HTMLPage``) that will provide your site-wide look and feel, then
    individual servlets can inherit from ``SitePage``.

    To see how ``HTMLPage`` generates an HTML document, look at
    :meth:`write_html` and the methods it calls.

    Methods and attributes:

    """

    def _lifecycle(self):
        """HTMLPage's implementation of the servlet lifecycle.  It
        calls the following methods in the specified order:

            #.  :meth:`prep`
            #.  :meth:`write_html`
            #.  :meth:`wrapup`

        ``prep`` and ``write_html`` are called within a ``try`` statement
        with ``wrapup`` called in its ``finally`` clause.
        """

        try:
            self.prep()
            if not self.write_html():
                raise HTTPNoContent
        finally:
            self.wrapup()

    def prep(self):
        '''This is the first method called by :meth:`_lifecycle`.  It
        should be used as a means to prep the servlet for
        :meth:`write_html`, e.g., opening data files, acquiring db
        connections, preprocessing form data, etc.  The return value
        is ignored.  The default implementation is a no-op.
        '''

        pass

    def write_html(self):
        '''This method produces a well-formed HTML document and writes
        it to the client.

        It first calls :meth:`write_doctype` which writes the DOCTYPE
        element.  It then writes "<HTML>".  In turn it calls
        :meth:`write_head` and :meth:`write_body` which write the HEAD
        and BODY sections, respectively.  It finishes by writing
        "</HTML>".  Returns ``True``.
        '''

        self.write_doctype()
        self.writeln('<HTML>')
        self.write_head()
        self.write_body()
        self.writeln('</HTML>')
        return True

    def wrapup(self):
        '''This is the last method called by :meth:`_lifecycle`,
        immediately after calling :meth:`write_html`.  This method
        should be used to "tidy up" after a request, e.g., flush
        output data, create a log entry, etc.  The return value is
        ignored by the handler.  The default implementation is a
        no-op.

        '''

        pass
        

    def write_doctype(self):
        '''Writes the <!DOCTYPE...> tag.  By default, the following is
        used::

            <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
                      "http://www.w3.org/TR/html4/loose.dtd">        


        This can be controlled by setting the :attr:`doctype` instance
        variable.  If set, it will be written, as-is, to the client.
        If it is not set, then the :attr:`dtd` instance variable will
        be checked; it can be one of "strict", "loose" or "frameset".
        The default is "loose" and the resulting DOCTYPE is shown
        above.  If set to "strict" or "frameset" an appropriate
        DOCTYPE will be generated.
        '''
        

        if self.doctype is _NotDefined:

            # doctype not provided, so we'll generate it
            
            doctype = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01%s//EN"
            "http://www.w3.org/TR/html4/%s.dtd">'''

            dtds = {'strict' : '',
                    'loose'  : ' Transitional',
                    'frameset' : ' Frameset'}

            if self.dtd is _NotDefined:
                # DTD not provided, we'll assume the most liberal
                dtd = 'loose'
                
            if dtd not in dtds.keys():
                # if we were given an erroneous DTD, we'll quietly fix it
                dtd = 'loose'
                
            extra = dtds.get(dtd)

            # set doctype and cache it so we don't have to generate it again
            doctype = self.doctype = doctype % (extra, dtd)
        else:
            # doctype provided
            doctype = self.doctype

        self.writeln(doctype)

    doctype = _NotDefined
    'See :meth:`write_doctype`'

    dtd = _NotDefined
    'See :meth:`write_doctype`'

    def write_head(self):
        '''This writes the HEAD section of the HTML document to the
        client.  It first writes "<HEAD>" then calls
        :meth:`write_head_parts` and, lastly, writes "</HEAD>".

        This method need not be typically overridden.  To modify the
        content of the HEAD section, see :meth:`write_head_parts`.
        '''

        self.writeln('<HEAD>')
        self.write_head_parts()
        self.writeln('</HEAD>')

    def write_head_parts(self):
        '''This method calls, in order:

          #. :meth:`write_title`
          #. :meth:`write_shortcut_icon`
          #. :meth:`write_base`
          #. :meth:`write_meta`
          #. :meth:`write_css`
          #. :meth:`write_js`
          
        See the above methods for details about what each writes to
        the client.  All of the above methods can have the content
        they generate controlled by setting (or unsetting) various
        instance variables.

        While the base method will serve most developer needs, this
        method is a likely candidate to be overridden.  If you want to
        *add* to the HEAD you will likely want to call the superclass
        method and then write additional content in your method,
        e.g.::

            class MyServlet(HTMLPage):
               ...

               def write_head_parts(self):
                   HTMLPage.write_head_parts(self)
                   # add my own content
                   self.writeln(...)
                   

        '''

        self.write_title()
        self.write_shortcut_icon()
        self.write_base()
        self.write_meta()
        self.write_css()
        self.write_js()

    def write_title(self):
        '''Writes the TITLE tag to the client.

        It checks for the :attr:`title` instance variable.  If it does
        not exist it uses the name of the servlet for the title.  If
        :attr:`title` is callable it will be called (with no
        arguments) and its output will be used as the title.
        '''

        title = self.title

        if title is _NotDefined:
            title = self.title = self.__class__.__name__

        if callable(title):
            title = title()
            
        self.writeln('<TITLE>\n', title, '\n</TITLE>')

    title = _NotDefined
    '''The title of the HTML page.  If not set, it defaults
    to the name of the servlet.  ``title`` can be a callable that
    accepts no arguments, in which case the title will be the output
    of the callable.'''

    def __write_head_tag(self, tag, tagtype, content):
        'utility method to write HEAD tags'

        if type(content) in (list, tuple):
            content = '\n'.join(content)
                
        self.writeln('''
<%(tag)s type="%(tagtype)s">
<!--
%(content)s
-->
</%(tag)s>''' % locals())

    def write_shortcut_icon(self):
        '''Writes a LINK tag to the client specifying the shortcut
        icon.  See :attr:`shortcut_icon`.
        '''

        if self.shortcut_icon:
            self.writeln('<LINK rel="shortcut icon" href="%s"/>'
                         % self.shortcut_icon)
            
    shortcut_icon = ''
    '''If non empty, specifies the href to a shortcut icon and
    produces a LINK tag in the HEAD: <LINK rel="shortcut icon"
    href="``shortcut_icon``"/>'''

    def write_base(self):
        '''Write BASE tag to the client in the HEAD.  See
        :attr:`base`.
        '''

        if not self.base:
            return

        if type(self.base) is tuple:
            href, target = self.base
        else:
            href, target = self.base, ''

        if href:
            href = 'href="%s"' % href
        if target:
            target = 'target="%s"' % target

        if href or target:
            self.writeln('<base %s %s>' % (href, target))
        
    
    base = ''
    '''If set, this will specify the BASE tag in the HEAD.  If
    ``base`` is a string it will be the value of the ``href``
    attribute.  If ``base`` is a tuple, it should have two string
    elements of the form (*href*, *target*) which will be the values
    of those BASE tag attributes.'''
    
    def __write_meta(self, tag, mapping):
        'utility method to write META tags'

        for name, content in mapping.iteritems():

            if type(content) not in (list, tuple):
                content = (content,)

            for c in content:
                self.writeln('<meta %s="%s" content="%s">' % (tag, name, c))
                
            
    def write_meta(self):
        '''Writes META tags to the client in the HEAD.  See
        :attr:`meta` and :attr:`http_equiv`.
        '''
        
        if self.meta:
            self.__write_meta('name', self.meta)

        if self.http_equiv:
            self.__write_meta('http-equiv', self.http_equiv)

    meta = {}
    '''A dict, which if non-empty will produce META tags in the HEAD.
    The keys of the dict will be the values of the ``name`` attribute
    of the element and their values will become the ``content``
    attribute of the element.  For example, the following value of
    meta::

       meta = {"Author" : "John Doe",
               "Date"   : "October 6, 2011"}

    will produce the following output in the HEAD::

       <META name="Author" content="John Doe">
       <META name="Date" content="October 6, 2011">


    The values of the dict may be a list or tuple of strings, in which
    case multiple META tags will be produced for the same ``name``
    attribute.  For example::

       meta = {"Author" : ["Tom", "Jerry"]}

    will produce the following output in the HEAD::

       <META name="Author" content="Tom">
       <META name="Author" content="Jerry">'''


    http_equiv = {}
    '''http_equiv, like :attr:`meta`, produces META tags in the HEAD, but
    instead of the keys being the value of the ``name`` attribute, they
    are the value of the ``http-equiv`` attribute.  See :attr:`meta` for
    details.'''


    def write_css(self):
        '''Writes CSS to the client in the HEAD.  See :attr:`css_links`
        and :attr:`css`.
        '''

        for link in  self.css_links:
            self.writeln('<LINK type="text/css" rel="stylesheet" href="%s"/>'
                         % link)

        if self.css:
            self.__write_head_tag('STYLE', 'text/css', self.css)

    css = ''
    '''A string or list of strings of CSS.  If non empty, a <STYLE
    type="text/css">...</STYLE> section will be placed in the HEAD.
    If css is a list of strings, the elements will be joined
    (seperated by newlines) and placed in a single STYLE element.'''


    css_links = []
    '''A list of hrefs (strings).  For each href, a <LINK
    type="text/css" rel="stylesheet" href=HREF/> be placed in the HEAD.'''
    
    def write_js(self):
       '''Writes javascript to the client in the HEAD.  See
       :attr:`js_src` and :attr:`js`.
        '''

       for src in self.js_src:
            self.writeln('<SCRIPT src="%s" type="text/javascript"></SCRIPT>'
                         % src)

       if self.js:
            self.__write_head_tag('SCRIPT', 'text/javascript', self.js)

    js = ''
    '''A string or list of strings of javascript.  If non empty, a
    <SCRIPT type="text/javascript">...</SCRIPT> section will be placed
    in the HEAD.  If ``js`` is a list of strings, the elements will be
    joined (seperated by newlines) and placed in a single SCRIPT element.'''
    
    js_src = []
    '''A list of hrefs (strings).  For each href, a <SCRIPT
    type="text/javascript" src=HREF></SCRIPT> will be placed in the
    HEAD.'''
    
    def write_body(self):
        '''Writes the BODY section to the client.

        This method writes "<BODY...>", taking into account the
        :attr:`body_attrs` instance variable.  It then calls
        :meth:`write_body_parts` and finally writes "</BODY>".

        This method need not be typically overridden.  To modify the
        content of the BODY section, see :meth:`write_body_parts`.

        '''

        body_attrs = []
        for attr, val in self.body_attrs.items():
            body_attrs.append('%s="%s"' % (attr, val))
        self.writeln('<BODY %s>' % ' '.join(body_attrs))
        self.write_body_parts()
        self.writeln('</BODY>')

    body_attrs = {}
    '''Attributes for BODY tag.  Default is empty dict.
    If non empty, the keys will become attribute names for the BODY
    tag and the values will be the attribute values.'''
    
    def write_body_parts(self):
        '''Write the content of the BODY section.

        The base implementation simply calls :meth:`write_content`.

        For complex pages that have many sections (navigation sidebar,
        title menu, etc.) this method will typically be overridden,
        e.g., write the layout of the site look-and-feel and where
        page-specific content should appear, call ``write_content``.

        See the tutorial that comes with the distribution for examples
        of how overriding this method can be used to generate
        site-wide look-and-feel.
        '''

        self.write_content()

    def write_content(self):
        '''This method must be overridden to produce content on the
        page with calls to :meth:`WSGIServlet.writeln`.
        '''

        self.writeln('<strong>Override method <code>write_content'
                     '</code></strong>')


if __name__ == '__main__':

    class helloworld(HTMLPage):
	title = 'Hello, World!'
	css = 'strong {color: red}'

	def write_content(self):

	    self.writeln("Here's a simple demo to say "
			 "<strong>Hello, World</strong>!")

    helloworld.test_server()
    
