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

class nooverride(HTMLPage):
    "Show what happens when you don't override write_content()."


    # This servlet shows what happens when you have an empty class
    # definition.  Not too interesting.  Note how when you don't
    # override write_content() you get the base class' version.  Note,
    # too, the default title of a page is the name of the servlet class.

    pass


