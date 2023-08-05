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

from TutorialBase import *

class markdowntxt(HTMLPage):
    "A note about using markdown in the tutorial."

    title = 'Using Markdown'

    def write_content(self):
        self.writeln(OVERVIEW)





# -*-*- DOC -*-*- 

OVERVIEW = make_overview("""
{divstart}

A note about the generated HTML for this tutorial.  The text you are
reading throughout this tutorial is written in
[Markdown](http://daringfireball.net/projects/markdown/).  From
Markdown's website:

> *Markdown is a text-to-HTML conversion tool for web
> writers. Markdown allows you to write using an easy-to-read,
> easy-to-write plain text format, then convert it to structurally
> valid XHTML (or HTML).*

This tutorial is written assuming the Markdown [python
package](http://pypi.python.org/pypi/Markdown) is installed on
the host machine running this tutorial and is available to import.  If
the package is not found[^1], you will see readable, albeit plain, text.
(And that folks is the beauty of markdown.)

[^1]:
    And apparently it **{markdownfound}** found on this server!
    
{divend}

And one final comment about the text you see: when viewing the source
code (via the links on each tutorial page), to make the source code as
readable as possible, I have moved the markdown text processing to the
bottom of the files, so when you see this:

        # -*-*- DOC -*-*-

you should know that what follows is uninteresting text processing.
""")

DIVSTART = '''<div style="background-color:gold;margin:50px;padding:5px;border-style:solid">'''
DIVEND = '</div>'

OVERVIEW=OVERVIEW.format(divstart=DIVSTART, divend=DIVEND,
                         markdownfound = 'is' if USEMARKDOWN else 'is not')

