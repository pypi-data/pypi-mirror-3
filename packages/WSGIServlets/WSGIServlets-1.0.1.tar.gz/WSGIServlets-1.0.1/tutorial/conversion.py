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

def _age(age):

    'Converts age (a string) to an int.  All values < 1 return as -1'

    try:
        a = int(age)
    except:
        # bad input, return our flag
        return -1
    
    if a < 1:
        # return our flag
        return -1
    return a

class conversion(HTMLPage):

    "Converting query variables to arbitrary python types."

    title = 'Converting Query Variables to Arbitrary Types'

    firstname = GET_var()
    age = GET_var('-1', _age)

    def write_content(self):

        self.writeln(OVERVIEW)

        if self.method == 'POST':
            self.writeln(self.process_form())

        self.writeln(THEFORM.format(firstname=self.firstname,
                                    age=self.age if self.age != -1 else ''))
        

    def process_form(self):

        if self.firstname and self.age != -1:
            return FORMRESULTS.format(firstname=self.firstname,
                                      age=self.age,
                                      msg='')
        else:
            f = self.firstname if self.firstname else 'First name is required'
            a = self.age if self.age != -1 else 'A proper age is required'
            return FORMRESULTS.format(firstname=f,
                                      age=a,
                                      msg='There was a problem!')




# -*-*- DOC -*-*-

OVERVIEW = make_overview("""
By default, all data returned via an URL or the posting of a form are
strings. This can make for tedious programming having to manually
convert the incoming strings to other python types.  Using `GET_var`
eliminates much of this tedium by allowing the developer to specify
exactly what types each attribute should be by specifying a default
value and/or providing a conversion function.

This servlet will demonstrate how to convert strings to arbitrary
types by specifying a conversion function. The next servlets will
demonstrate special treatment for python lists and dicts.

The constructor for `GET_var` is:

{codesample}      

The first argument, `default`, specifies the default value for the
attribute if it is not found in `form`.  The value of default must be
a string, list or dict.

The second argument, `conv`, specifies the conversion function and
must be None (the default, which does no conversion) or be a callable
that accepts a single argument and returns the converted value. If the
conversion function raises an exception the attribute will be set to
its default value.

This servlet creates two such variables with the following
declarations:

        firstname = GET_var()
        age = GET_var('-1', _age)


`firstname` specifies no default (so the default value will be the
empty string) and no conversion (so the result will be type `str`).
`age` will be an `int`, the incoming string from the request will be
passed through the conversion function, `_age` (view the source to see
how it is implemented).  If the value passed in through the form is
illegal, the value stored in age will be -1, which can act as a flag
in the code for an unspecified or illegal value.
""")

OVERVIEW=OVERVIEW.format(codesample='''<span class="codesample">def __init__(self, default='', conv=None)</span>''')

FORMRESULTS = make_formresults("""
{span}

First Name: {{firstname}}  
Age: {{age}}
""").format(span='<span style="color:red">{msg}</span>')

THEFORM = """
<div align="center">
<form method="POST">

<table class="formdisplay">
<tr>
<td>First Name:</td>
<td><input name="firstname" value="{firstname}"></td>
</tr>
<tr>
<td>Age:</td>
<td><input name="age" value="{age}" size="4"></td>
</tr>
<tr>
<td colspan="2" align="center"><input type="submit" value="Try Me"></td>
</tr>
</table>

</form>                     
</div>
"""
