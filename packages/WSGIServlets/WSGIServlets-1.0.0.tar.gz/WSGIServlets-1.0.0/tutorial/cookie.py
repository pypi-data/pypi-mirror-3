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

TIMEOUT = 30
COLORS = ['red', 'blue', 'green', 'orange', 'brown']
FILL_COOKIE = 'fill-pref'
DEF_FILL = 'grey'
        

class cookie(HTMLPage):

    'How to manage cookies.'

    title = 'State Management, Part 1: Cookies'

    fillpref = GET_var()

    def prep(self):
        HTMLPage.prep(self)

        self.fill = fill = None
        
        if self.method == 'POST':
            # check the form 
            fill = self.fillpref
            if not fill or fill not in COLORS:
                self.del_cookie(FILL_COOKIE)
                fill = DEF_FILL
            else:
                self.set_cookie(FILL_COOKIE, fill, expires=TIMEOUT)
                self.fill = fill

        if not fill:
            # check for fill setting in cookies
            fill = self.cookies.get(FILL_COOKIE)
            if fill:
                fill = fill.value
                if fill not in COLORS:
                    # rogue setting by user?
                    self.del_cookie(FILL_COOKIE)
                    fill = DEF_FILL
                else:
                    self.fill = fill
            else:
                fill = DEF_FILL

        self.css = self.csstmpl.format(fillpref=fill)
        
    def write_content(self):

        self.writeln(DEMO.format(fillpref=self.fill))
        self.writeln(OVERVIEW)
        

# -*-*- DOC -*-*-

    csstmpl = '''
    #floatbox {{
    float: right;
    margin: 20px 50px;
    }}
    #demobox {{
    margin-top: 10px;
    border: 3px solid black;
    background-color: {fillpref};
    width: 100px;
    height: 100px;
    }}
    '''

OVERVIEW = make_overview("""

Cookies are easily managed with WSGIServlets.  Servlets have an
attrbiute, `cookies`, which is a container for incoming cookies and
is, by default, an instance of `Cookie.SimpleCookie`, a class defined
in the standard python `Cookie` module.  Any subclass of
`Cookie.BaseCookie` can be used for incoming cookies.  Which class is
used is determined by the servlet attribute `cookieclass`.

If you are unfamiliar with the `Cookie` module you should review the
standard python documentation.

It is recommended you use the standard `Cookie.SimpleCookie` for
unsigned cookies and `SignedCookie` for cookies where end-user
manipulation can present a security risk (e.g., session IDs).  Note,
`SignedCookie` is *not* part of the standard `Cookie` module and is a
class defined in wsgiservlets.

To set a cookie, use the set_cookie method:

        servlet.set_cookie('default_border', 'red')

To delete a cookie, use the del_cookie method:

        servlet.del_cookie('default_border')

In the box in the upper right is a colored box. By submitting the form
below you can set your preference for the fill color.  Then navigate
away from this page and back and you will see your preference has been
remembered: it was stored in a cookie, `fill-pref`.  The cookie is set
to timeout in {timeout} seconds so you can see how the box returns to its
default grey after the cookie expires.


""")

FORM = '''
<hr>
<div style="margin-left: 30px;">
<form method="POST">
<table>
<tr>
<td>
Fill Preference:&nbsp;&nbsp;<select name="fillpref">
<option selected>Delete Pref</option>
<option>red</option>
<option>blue</option>
<option>green</option>
<option>orange</option>
<option>brown</option>
</select)
</td>
<td>
<input type="submit" value="Set Preferences">
</td>
</tr>
</table>
</form>
</div>
'''        

OVERVIEW = OVERVIEW.format(timeout=TIMEOUT) + FORM

DEMO = '''
<div id="floatbox">
Default&nbsp;fill:&nbsp;grey<br>
Your&nbsp;fill&nbsp;pref:&nbsp;{fillpref}
<div id="demobox"></div>
</div>
'''        

