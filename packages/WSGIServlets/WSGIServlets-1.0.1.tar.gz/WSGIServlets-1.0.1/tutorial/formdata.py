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

class formdata(HTMLPage):

    "Introduction to processing URL and FORM data using the form attribute."

    title = 'Processing URL and FORM Data'

    def write_content(self):

        # write overview text
        self.writeln(OVERVIEW)

        # Attribute method will be POST or GET depending on the
        # incoming request method.  If POST, the form has been
        # submitted.
        if self.method == 'POST':

            # Retrieve the firstname and age from the form
            firstname = self.form.getfirst('firstname')
            age = self.form.getfirst('age')

            # write the results.  FORMRESULTS is a str and we use the
            # new python2.6 format method to fill in the form results
            self.writeln(FORMRESULTS.format(firstname=firstname,
                                            age=age))

        # Write out the form
        self.writeln(THEFORM)





# -*-*- DOC -*-*-

OVERVIEW = make_overview("""
### Nomenclature

[RFC 2396](http://www.ietf.org/rfc/rfc2396.txt)
refers to the part of a URI to the right of a '?' as the
query, as in:

        <scheme>://<authority><path>?<query>

An example of an HTTP URL with a query:
    
        http://somehost/somepath?firstname=Bob&age=42

Here we say that *firstname* and *age* are **query variables** and
that *Bob* and *42* are their **values**.

In HTML FORM elements, as in:

        <INPUT type="text" name="firstname">
        <INPUT type="text" name="age">

we say *firstname* and *age* are **form variables**, *if and only if*
the form is submitted with method POST.  If the form is submitted with
method GET, the data will be placed in the URL and so will become
**query variables**.

Why we make this distinction between **query variables** and
**form variables** will be made clear in the next few
servlets.

### Retrieving Data

For each request processed by a servlet an attribute is created,
`form`, and is an instance of `cgi.FieldStorage` (refer to the python
standard library documentation for details).  Here we will briefly
show how you can use the `form` attribute to retrieve data.
            
""")


FORMRESULTS = make_formresults("""
First Name: {firstname}      
Age: {age}
""")

THEFORM = """
<div align="center">
<form method="POST">

<table class="formdisplay">
<tr>
<td>First Name:</td>
<td><input name="firstname"></td>
</tr>
<tr>
<td>Age:</td>
<td><input name="age" size="4"></td>
</tr>
<tr>
<td colspan="2" align="center"><input type="submit" value="Try Me"></td>
</tr>
</table>

</form>                     
</div>
"""
