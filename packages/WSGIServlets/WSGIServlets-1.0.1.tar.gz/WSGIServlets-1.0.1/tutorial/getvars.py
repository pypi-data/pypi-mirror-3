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

class getvars(HTMLPage):

    "Simplifying processing query variables using GET_var()."

    title = 'Processing Query Variables'

    name = GET_var()

    def write_content(self):

        self.writeln(OVERVIEW)

        name = self.name or 'World'
        
        self.writeln(THEFORM.format(name=name, script=self.script_name))


# -*-*- DOC -*-*-

OVERVIEW = make_overview("""
The previous servlet defined **query variables** and **form
variables**.  This servlet begins looking at special attributes
created with the descriptor class, `GET_var`, which offers developers
a powerful tool to assist in processing **query variables**.

If you are unfamiliar with python descriptors see [this
documentation](http://docs.python.org/release/2.6.5/reference/datamodel.html#implementing-descriptors)
for an overview.


Descriptors created with `GET_var` search for values in the `form`
attribute with the same name.

In this servlet we have created a descriptor, `name`:

{codesample}

By setting `name` in this way, when accessed, the servlet will search
`form` for a key named `name` and return its value.  If it is not
found it will be set to an empty string.  This servlet checks for the
empty string and sets `name` to *World* as a default.  Note how each
of the following links adds a query string to the URL of the form
`?name=NAME`, but the last link does not.

""").format(codesample='<span class="codesample">name = GET_var()</span>')


THEFORM = """
<span class="formoutput">Hello, {name}!</span>

<p>
Say hello to <a href="{script}?name=Mo">Mo</a><br/>
Say hello to <a href="{script}?name=Larry">Larry</a><br/>
Say hello to <a href="{script}?name=Curly">Curly</a><br/>
Say hello to the <a href="{script}">World</a>
</p>
"""

