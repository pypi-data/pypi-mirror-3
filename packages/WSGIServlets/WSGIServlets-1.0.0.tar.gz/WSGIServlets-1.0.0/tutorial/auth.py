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

class auth(HTMLPage):
      'Basic HTTP authentication, Part I.'

      title = 'Basic HTTP Authentication (1 of 2)'

      def write_content(self):

            self.writeln(OVERVIEW)




# -*-*- DOC -*-*-

OVERVIEW = make_overview("""
WSGIServlets offers methods to assist in managing Basic HTTP
Authentication.  The next servlet will demonstrate this functionality.
This servlet exists in the tutorial to give you the username and
password you will need for the next servlet:

> **username:** wsgi  
> **password:** servlets


* * *

**Note:** if this tutorial is being served by apache mod_wsgi, the
next servlet will not work unless the following mod_wsgi directive is
set for the containing directory:

        WSGIPassAuthorization On

See mod_wsgi documentation for details.        
""")

