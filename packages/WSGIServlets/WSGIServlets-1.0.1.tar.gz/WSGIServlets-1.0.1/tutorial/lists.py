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

class lists(HTMLPage):

    'Converting form data to python lists'

    title = 'Converting URL/Form Data to Python Lists'
    all_colors = ['red', 'blue', 'green', 'violet', 'cyan', 'amber']
    all_animals = ['dog', 'cat', 'African Sparrow', 'hippopotamus', 'grub',
                   'python']

    colors = GET_var([])
    animals = GET_var([])

    def write_content(self):

        self.writeln(OVERVIEW)

        if self.method == 'POST':
            self.writeln(self.process_form())

        self.writeln(self.theform())
        

    def process_form(self):

        nofav = """<span style="color:red">You don't have any favorite %s!</span>"""
        colors = (', '.join(self.colors)
                  if self.colors
                  else nofav % 'colors')
        
        animals = (', '.join(self.animals)
                   if self.animals
                   else nofav % 'animals')

        return FORMRESULTS.format(colors=colors, animals=animals)

    def theform(self):
        
        colors = []
        for color in self.all_colors:
            colors.append(INPUT.format(color=color,
                                       checked=('checked'
                                                if color in self.colors
                                                else '')))
            
        animals = []
        for animal in self.all_animals:
            animals.append(OPTION.format(animal=animal,
                                         selected=('selected'
                                                   if animal in self.animals
                                                   else '')))

        return THEFORM.format(colors = '<BR>\n'.join(colors),
                              animals = '\n'.join(animals))



# -*-*- DOC -*-*-


OVERVIEW = make_overview("""
I said in the previous servlet that the `default` parameter to
`GET_var` had to be a string, list or dict.  The data type of
`default` determines how the data is extracted from `form`.  If
`default` is a string, the value will be retrieved with a call to
`form.getfirst()`. If `default` is a list, the value will be retrieved
with a call to `form.getlist()`. If `default` is a dict, form will be
searched for variables with names of the form *NAME[KEY]*.

If you are not familiar with the `getfirst` and `getlist` methods, you
should review the python standard library documentation; see
`cgi.FieldStorage`.

This servlet will demonstrate lists. The next will demonstrate dicts.

When `default` specifies a list, it can be empty or have elements, but
if it has elements they must be strings.  You may also specify a
converstion object, in which case it should be a callable that expects
a list as its only argument; it may return any arbitrary object, but
typically you will want it to return a list with its elements
converted to some arbitrary type, e.g., convert a list of strings into
a list of ints.

When do you want to use lists? They are particularly handy when
processing `INPUT` elements with the `type` attribute set to
*checkbox* and `SELECT` elements with the `multiple` attribute set.
Here is an example of each:
""")


FORMRESULTS = make_formresults("""
Your favorite colors are: {colors}    
Your favorite animals are: {animals}
""")

THEFORM = """
<FORM method="POST">
  <DIV align="center">
    <TABLE class="formdisplay">
      <TR valign="top">
        <TD>Favorite Colors:</TD>
        <TD>{colors}</TD>
        <TD>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</TD>
        <TD>Favorite Animals:</TD>
        <TD><SELECT multiple name="animals" size="6">{animals}</SELECT></TD></TR>
      <TR>
        <TD colspan="5" align="center"><INPUT type="submit" value="Submit Favorites"></TD></TR></TABLE></DIV></FORM>

"""

INPUT = """<INPUT type="checkbox" {checked} name="colors" value="{color}"> {color}"""

OPTION = """<OPTION {selected}>{animal}</OPTION>"""

