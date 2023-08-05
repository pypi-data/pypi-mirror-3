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

class fini(HTMLPage):
    'Proselytizing with an example.'

    title = 'Fini'

    js_src = ['/fini.js']
    css_links = ['/fini.css']
                 
    def write_content(self):

        self.writeln(OVERVIEW)

        self.writeln('<div id="thumbnails">')
        for tut in TutorialBase.tutorials[:-1]:
            self.write(IMG.format(t=tut))
        self.writeln('</div>')


# -*-*- DOC -*-*-

OVERVIEW = make_overview('''
I wrote WSGIServlets because I believe strongly in the power of object
oriented programming, generally, and how it can be applied to web
application programming, specifically.  Combining OOP techniques with
web technologies which promote separation of form (css) and logic
(javascript) from content, WSGIServlets offers a very powerful tool to
quickly prototype and develop rich web applications.

As a small example of this power I leave you with this servlet which
shows every other servlet in this tutorial.  Click on one of the
images and a popup will appear running that servlet.  View the source
of this page...excluding the textual content and underlying
css/javascript, there are about 10 lines of python code.  

<hr>

<div id="mask">
    <div id="container">
        <span id="close" onclick="popUpClose()">X</span>
        <iframe src="about:blank" id="popup"></iframe>
    </div>
</div>
''')

IMG = '''<IMG width="350" height="200" onclick="popUp('brief_{t}')" src=/thumbnails/{t}.png/ alt="{t} thumbnail">'''


