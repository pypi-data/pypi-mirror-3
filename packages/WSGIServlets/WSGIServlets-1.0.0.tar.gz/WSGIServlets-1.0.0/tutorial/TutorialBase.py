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

import sys
import os
import cgi

try:
    from markdown import markdown
    USEMARKDOWN = True
except:
    USEMARKDOWN = False
    def markdown(text, *args, **kw):
        return '\n<pre>\n' + cgi.escape(text) + '\n</pre>\n'

from wsgiservlets import *
from HTMLHighlightedPy import HTMLHighlightedPy

BR = '<br/>'
HR = '<hr/>'

class TutorialBase(HTMLPage):

    tutdebug = False

    py = {}

    meta = {'author' : 'Daniel J. Popowich',
            'copyright' : '2011'}

    tutorials = ['helloworld', 'nooverride', 'markdowntxt',
                 'ivars', 'more_ivars', 'formdata',
                 'getvars', 'getvars2', 'conversion',
                 'lists', 'dicts', 'gvarspvars',
                 'cookie', 'sessions',
                 'lifecycle', 'overriding', 'overriding2',
                 'auth', 'auth2', 'environ', 'httpresponses',
                 'dispatching', 'jsonrpc', 'fini',
                 
                 ]

    @classmethod
    def toc_summary(klass):
        if klass.__doc__ is None:
            raise NotImplementedError, \
                  'class %s needs docstring for TOC summary.' % klass.__name__
        return klass.__doc__

    def __repr__(self):
        return self.__str__()

    def _lifecycle(self):

        try:
            self.tutprep()
            self.prep()
            if not self.write_html():
                raise HTTPNoContent
        finally:
            self.wrapup()
            
    def tutprep(self):

        self.this = os.path.basename(self.script_name)
        try:
            index = self.tutorials.index(self.this)
        except:
            index = 0

        self.nav = ((index and [index - 1] or [None])[0],
                    index < len(self.tutorials) - 1 and index+1 or None)
        self.index = index + 1

        self.brief_nav = self.script_name[:7] == '/brief_'

    def write_nav(self):
        prev, next = self.nav

        self.write(('<a href="/%s">Previous</a>' % self.tutorials[prev])
                   if prev is not None
                   else 'Previous')
        self.write('&nbsp;')
        self.write(('<a href="/%s">Next</a>' % self.tutorials[next])
                   if next is not None
                   else 'Next')

    def write_css(self):
        '''Normally not overridden, but need to hard-code the tutorial
        CSS file without having to code it in the samples'''

        self.writeln('<LINK type="text/css" rel="stylesheet" '
                     'href="/tutorial.css"/>')
        super(TutorialBase, self).write_css()
        
    def write_js(self):
        '''Normally not overridden, but need to hard-code the tutorial
        javascript file without having to code it in the samples'''

        self.writeln('<SCRIPT src="/tutorial.js" '
                     'type="text/javascript"></SCRIPT>')
        super(TutorialBase, self).write_js()
    
    def write_body(self):
        '''Write out the BODY.

           Normally, this method would not be overridden, but since
           this tutorial wants to demonstrate overriding
           write_body_parts, we need to do special things here and
           leave write_body_parts free to be overridden in tutorial
           examples.

           '''

        # the following is copied verbatim from the base class
        body_attrs = []
        for attr, val in self.body_attrs.items():
            body_attrs.append('%s="%s"' % (attr, val))
        self.writeln('<body %s>' % ' '.join(body_attrs))

        self.before()
        self.write_body_parts()
        self.after()
            
        self.writeln('</body>')

    def before(self):

        # add the TITLE, index links and Hide/View Source links
        title = self.title
        if callable(title):
            title = title()

        self.writeln('<div class="tutmachinery">')
        self.writeln('<div align="center"><h1>%s</h1></div>' % title)

        if self.brief_nav:
            self.writeln('<hr>\n</div>')
            return

        index = []
        for x in range(len(self.tutorials)):
            if x+1 == self.index:
                index.append('%d&nbsp;&nbsp;' % (x+1))
                continue
            index.append('<a href="/%s">%d</a>&nbsp;&nbsp;'
                         % (self.tutorials[x], x+1))
        home = '<a href="/index">Home</a>&nbsp;&nbsp;|&nbsp;&nbsp;'
        index = ''.join(index)
        toc = '<div align="center">{home}{index}<br/>{ref}</div><br/>'
        ref = '<a href="javascript:refman()">Reference Manual</a>'
        self.writeln(toc.format(home=home, index=index, ref=ref))
        

        fname = self.sourcefilename()
        self.writeln('''<a href="#" id="srcbtn" onclick="toggle_collapse('src', 'srcbtn')">Show</a>&nbsp;Source''')
        
        self.writeln(self.py.setdefault(self,
                     HTMLHighlightedPy(open(fname).read())))

        # write out navigation and HR
        self.writeln(BR)
        self.write_nav()
        self.writeln('</div>')
        self.writeln(HR)
        
        # now call write_body_parts

    def after(self):

        if self.brief_nav:
            return
        
        # closing HR and navigation
        self.writeln('\n', HR)
        self.writeln('<div class="tutmachinery">')
        self.write_nav()

        if self.tutdebug:
            self.writeln('<pre>\n',self.format_environ(),'\n</pre>')
            
        # now close the body
        self.writeln('</div>')
        

    def sourcefilename(self):
        src = sys.modules[self.__module__].__file__
        if src[-4:] == '.pyc':
            src = src[:-1]
        return os.path.abspath(src)

# trickery for tutorial documentation
HTMLPage = TutorialBase

SHOWHIDEBUTTON = """
<div id="showhidediv" style="display:none">

  <button onclick="toggle_collapse('overview','showhidebutton')"
          id="showhidebutton"></button> the overview again.

</div>

"""

SHOWHIDESCRIPT = """
<script>

  document.getElementById('showhidediv').style.display = 'block';
  toggle_collapse('overview', 'showhidebutton');

</script>

"""


def make_overview(txt):
    return (SHOWHIDEBUTTON
            + '<div id="overview" style="display:block">\n'
            + markdown(txt, ['footnotes', 'tables'])
            + '\n</div>\n')
            
def make_formresults(txt):
    return (SHOWHIDESCRIPT
            + '<div align="center">\n<div class="formoutput">\n\n'
            + markdown('**This servlet has been posted via a form:**\n\n'
                       + txt)
            + '</div>\n</div>\n')
