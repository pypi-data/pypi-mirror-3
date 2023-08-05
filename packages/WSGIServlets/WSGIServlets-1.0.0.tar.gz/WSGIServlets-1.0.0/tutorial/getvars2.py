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

class getvars2(HTMLPage):
    "Using defaults while processing query variables with GET_var()."

    title = 'Using Defaults with  Query Variables'

    name = GET_var('World')

    def write_content(self):

        self.writeln(OVERVIEW)

        self.writeln(THEFORM.format(name=self.name, script=self.script_name))


# -*-*- DOC -*-*-

OVERVIEW = make_overview("""
In the previous example we checked to see if `name` was an empty
string and, if so, set it to the default, *World*.  In this servlet we
set the default of `name` when we initialize it with `GET_var`.  The
first argument to the constructor is the default value, should it not
be present in the query.

{codesample}

The next tutorial will give the full specification to the `GET_var`
constructor.  

""")

OVERVIEW = OVERVIEW.format(codesample='''<span class="codesample">name = GET_var('World')</span>''')

THEFORM = """
<span class="formoutput">Hello, {name}!</span>

<p>
Say hello to <a href="{script}?name=Mo">Mo</a><br/>
Say hello to <a href="{script}?name=Larry">Larry</a><br/>
Say hello to <a href="{script}?name=Curly">Curly</a><br/>
Say hello to the <a href="{script}">World</a>
</p>
"""

