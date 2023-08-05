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

from wsgiservlets import *
from TutorialBase import TutorialBase, markdown


class index(HTMLPage):

    title = 'WSGIServlets Tutorial'
    css_links = ['/tutorial.css']

    def write_content(self):

        dispatcher = self.environ['wsgiservlets.dispatcher']

        self.write(OVERVIEW)
        self.writeln('<table id="toc">')
        for i, tutorial in enumerate(TutorialBase.tutorials):
            klass = dispatcher.servlet_mapping[tutorial][0]
            docstring = klass.toc_summary()

            link = '<a href="/{t}">{t}</a>'.format(t=tutorial)
            tr = '<tr class="odd">' if ((i+1) % 2) else '<tr>'
            self.writeln(tr, '<td class="num">', i+1, '</td>',
                         '<td class="link">', link, '</td>',
                         '<td class="summary">', docstring, '</td></tr>')
            
        self.writeln('</table>')




# -*-*- DOC -*-*-

OVERVIEW = markdown('''

# WSGIServlets Tutorial

Welcome to the WSGIServlets tutorial!

If you are new to WSGIServlets, start at the beginning with the
[helloworld](helloworld) tutorial.  Moving in sequence through the
servlets will introduce ever-more detail, later examples building on
earlier concepts, so it is recommended you continue straight on
through without skipping around too much.

Once you go through the tutorial and start writing your own servlets
you will find this tutorial (as its author does!) a handy how-to
reference to return to over and over again.

Each page in this tutorial is a separate servlet with hyperlinks to
move forward and backward through the tutorial.  The top of each page
has a global index of all servlets, a link back to this page, and a
link to the [Reference Manual](/ref).  In the upper left of every page
is a link to view the source code for the page you are viewing.

Now, on to the tutorial...

## Table of Contents

''')
