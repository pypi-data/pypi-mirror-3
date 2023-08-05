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

from SitePage import *

class overriding2(SitePage):
    'Continuing discussions of overriding HTMLPage methods'
    
    simulate_modification = True
    title = 'Overriding HTMLPage Methods (Revisited)'

    def write_content(self):
          self.writeln(OVERVIEW)

    # extend SitePage.write_sidebar
    def write_sidebar(self):
          # call super
          SitePage.write_sidebar(self)
          # append our own stuff
          self.writeln(MORESIDEBAR)

          
# -*-*- DOC -*-*-


OVERVIEW = make_overview("""

###### &uarr;&uarr;&uarr; Look!  A banner! &uarr;&uarr;&uarr;

So, after some time with a sidebar & content page layout you decide you
really need to have a banner as well:
    

    ---------------------------------------------------
    |                                                 |
    |                   BANNER                        |
    |                                                 |
    ---------------------------------------------------
    |            |                                    |
    | SIDEBAR    |  CONTENT                           |
    |            |                                    |
    |            |                                    |
    |            |                                    |
    |            |                                    |
    ---------------------------------------------------

All you need to do is tweak the code in `SitePage.write_body_parts` to
add a DIV and call a method, say, `write_banner`, inside the DIV:


    def write_body_parts(self):

        self.writeln('<div id="banner">')  ###
        self.write_banner()                ###
        self.writeln('</div>')             ###
        self.writeln('<div id="sidebar">')
        self.write_sidebar()
        self.writeln('</div>')
        self.writeln('<div id="content">')
        self.write_content()
        self.writeln('</div>')


[Note: The three lines marked with trailing **###** are the only
changes from the sample code in the previous servlet.]


This is what we have done with this servlet.  Well, you didn't
actually edit `SitePage.py`, we have simulated modifying
`SitePage.write_body_parts` by turning on a flag,
`simulate_modification`; look at the code in [SitePage.py](SitePage.py) for
details.  (Note: This also demonstrates how page layout can be
computed dynamically on the fly!)  Now, every servlet subclassing
`SitePage` will get the change.

##### &larr; Notice, too, how the sidebar has been extended!
""")
                    
MORESIDEBAR = markdown("""
____


We have extended the sidebar by calling the superclass method and then
adding a horizontal rule and this text.  View the python source for
details.  """)

