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

class ivars(HTMLPage):
    "Introduction to special attributes that can control HTML generation."

    title = 'Setting Special Instance Data Attributes'

    css = '''
    DIV.ivars {
        margin: 50px 25%;
        padding: 10px;
        background: #F0EBE2;
    }

    H1 {
        color:blue
    }
    '''

    def write_content(self):

          self.writeln('<DIV class="ivars">', OVERVIEW, '</DIV>')




# -*-*- DOC -*-*-

OVERVIEW = make_overview("""
By setting various attributes in your servlet you can control the
HTML.  In this servlet we have set the `css` attribute to specify the
background color of this text's containing DIV element to be lightgrey
with margins set to center the text in the middle of the window and
the color of text in H1 elements (the title) to be blue.

View the python source.  The `css` attribute can be set to any object
that can be converted into a string or it can be a sequence (list,
tuple) of strings, in which case, the strings will be joined.
""")
