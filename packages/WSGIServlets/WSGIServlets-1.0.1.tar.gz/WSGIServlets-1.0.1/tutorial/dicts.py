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

class dicts(HTMLPage):

    'Converting form data to python dicts'

    title = 'Converting URL/Form Data to Python Dicts'

    fields = ['name', 'address', 'city', 'state', 'zip', 'email']

    # the default value for each field will be an empty string
    userinfo = GET_var(dict([(f,'') for f in fields]))

    def write_content(self):

        self.writeln(OVERVIEW)
        
        if self.method == 'POST':
            self.writeln(self.process_form())

        self.writeln(self.theform())
        

    def process_form(self):

        # make a copy so we can display a "?" for missing fields
        # without having to modify the descriptor
        userinfo = self.userinfo.copy()

        # search for empty fields
        for field in self.fields:
            if not userinfo[field]:
                userinfo[field] = '?'

        # write the form results
        return FORMRESULTS.format(**userinfo)

    def theform(self):

        return THEFORM.format(**self.userinfo)



# -*-*- DOC -*-*-

OVERVIEW = make_overview("""
This servlet demonstrates how you can use standard python dicts in
processing forms.  If the `default` parameter to the `GET_var`
constructor is a dict, as in:

{codesample}

then for each request, the servlet will search `form` for names of the
form *userinfo[KEY]*.  For every such occurrence a new key will
be inserted into `userinfo`.

The dict specified as `default` does not have to be empty.  If
non-empty then the keys must be strings and their values must be
strings or lists.  If the value is a string then it will be retrieved
with `form.getfirst`, if a list, it will be retrieved with
`form.getlist`.  Note: `default`s that are strings or lists are
*replaced* when found in `form`, however, with dicts, when keys are
found in `form` that are not found in the default, they are *merged*
with default dict.

The benefits of collecting form data under the umbrella of one dict
are considerable: fewer attributes to manage, resulting in fewer lines
of cleaner code.  If you create a class that subclasses dict you can
use an instance of that class as `default` which will completely
encapsulate your form in an object!

### Example

In the form below we name each text INPUT element with the special
syntax:

        <input type="text" name="userinfo[name]">
        <input type="text" name="userinfo[address]">
        <input type="text" name="userinfo[city]">
        <input type="text" name="userinfo[state]">
        <input type="text" name="userinfo[zip]">
        <input type="text" name="userinfo[email]">

When the servlet processes the incoming form it will create one dict
with six elements.
""")

OVERVIEW = OVERVIEW.format(codesample='<span class="codesample">userinfo = GET_var({})</span>')        

FORMRESULTS = make_formresults("""
name: {name}    
address: {address}    
city: {city}    
state: {state}    
zip: {zip}    
email: {email}    
""")


THEFORM="""
<FORM method="POST">
  <DIV align="center">
    <TABLE class="formdisplay">
      <TR>
        <TD>name: </TD>
        <TD><INPUT type="text" name="userinfo[name]" value="{name}"></TD>
      </TR>
      <TR>
        <TD>address: </TD>
        <TD><INPUT type="text" name="userinfo[address]" value="{address}"></TD>
      </TR>
      <TR>
        <TD>city: </TD>

        <TD><INPUT type="text" name="userinfo[city]" value="{city}"></TD>
      </TR>
      <TR>
        <TD>state: </TD>
        <TD><INPUT type="text" name="userinfo[state]" value="{state}"></TD>
      </TR>
      <TR>
        <TD>zip: </TD>
        <TD><INPUT type="text" name="userinfo[zip]" value="{zip}"></TD>
      </TR>
      <TR>
        <TD>email: </TD>
        <TD><INPUT type="text" name="userinfo[email]" value="{email}"></TD>
      </TR>
      <TR>
        <TD colspan="2" align="center"><INPUT type="submit"></TD>
      </TR>
    </TABLE>
  </DIV>
</FORM>
"""
