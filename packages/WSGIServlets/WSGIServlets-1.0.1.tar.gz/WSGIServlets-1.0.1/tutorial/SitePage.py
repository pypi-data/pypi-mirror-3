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

class SitePage(HTMLPage):

    simulate_modification = False

    def write_body_parts(self):

        if self.simulate_modification:
            self.writeln('<div id="banner">')
            self.write_banner()
            self.writeln('</div>')
        self.writeln('<div id="sidebar">')
        self.write_sidebar()
        self.writeln('</div>')
        self.writeln('<div id="content">')
        self.write_content()
        self.writeln('</div>')

    def write_sidebar(self):

        self.writeln('<ol>')
        for tutorial in TutorialBase.tutorials:
            if tutorial == self.__class__.__name__:
                li = tutorial
            else:
                li = '<a href=/{t}>{t}</a>'.format(t=tutorial)
            self.writeln('<li>{li}</li>'.format(li=li))
        
        self.writeln('</ol>')


    def write_banner(self):

        self.writeln('WSGIServlets Tutorial')

