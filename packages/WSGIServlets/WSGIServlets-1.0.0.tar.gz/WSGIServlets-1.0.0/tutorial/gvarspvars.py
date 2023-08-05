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

GVAR_DEFAULT = 'Gvar default'
PVAR_DEFAULT = 'Pvar default'

class gvarspvars(HTMLPage):
      'Query variables vs form variables and the introduction of POST_var().'

      title = 'Query Variables vs. Form Variables'

      Gvar = GET_var(GVAR_DEFAULT)
      Pvar = POST_var(PVAR_DEFAULT)

      def write_content(self):
            self.writeln(OVERVIEW)

            if (self.Gvar != GVAR_DEFAULT
                or self.Pvar != PVAR_DEFAULT):
                  self.writeln(FORMRESULTS.format(Gvar=self.Gvar,
                                                  Pvar=self.Pvar))
            self.writeln(THEFORM)


            
                         

# -*-*- DOC -*-*-

OVERVIEW = make_overview("""
In a [previous servlet](formdata), both **query variables** and **form
variables** were defined.  Since then, we have only used `GET_var` to
demonstrate processing URL and form data.  Now we will look at
`POST_var`.

`POST_var` is identical to `GET_var` except for one detail: while a
`GET_var` is processed for all requests, any `POST_var` is only
processed for **POST** requests.  For **GET** requests, `POST_var`s
are set to their default values, whether or not they are in the URL or
form data.  You may be wondering why this distinction is made and why
this functionality exists.  Here are two examples:

  1. There may be applications where you do not want users to submit
     sensitive data with an URL (like usernames and passwords), but
     only through your form submissions.

  2. Imagine a list of options a user can choose from (checkboxes,
     multiple selects), but you want to offer a default selection.
     With only `GET_vars` there is no way to distinguish between a
     user deselecting all options from a user viewing a page for the
     first time.  Using `POST_vars` solves this problem: first time
     viewing is by GET, so defaults will always be used, but when the
     form is POSTed, the value will be retrieved with `form.getlist`,
     which may return an empty list, if all are deselected.

Below are three ways of setting two variables, `Gvar` and `Pvar`, both
to the value `1`: setting variables with a URL (via GET) and setting
the variables with forms (one via GET, one via POST).  You will notice
that `Gvar` is set each time, but `Pvar` is only set with a POST:""")

FORMRESULTS = make_formresults("""
Value of **Gvar**: {Gvar}  
Value of **Pvar**: {Pvar}
""")

THEFORM = """
<DIV align="center">
  <TABLE class="formdisplay">
    <TR>
      <TD><A href="?Gvar=1&Pvar=1">Set Gvar and Pvar to "1"</A></TD>
      <TD>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</TD>
      <TD><FORM method="GET">
              <INPUT type="hidden" name="Gvar" value="1">
              <INPUT type="hidden" name="Pvar" value="1">
              <INPUT type="submit" value="GET submit">
          </FORM></TD>
      <TD>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</TD>
      <TD><FORM method="POST">
              <INPUT type="hidden" name="Gvar" value="1">
              <INPUT type="hidden" name="Pvar" value="1">
              <INPUT type="submit" value="POST submit">
          </FORM></TD>
    </TR>
  </TABLE>
</DIV>
"""
