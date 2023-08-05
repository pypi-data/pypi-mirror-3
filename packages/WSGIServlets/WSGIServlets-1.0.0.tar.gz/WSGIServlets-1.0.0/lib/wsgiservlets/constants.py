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

import re

# A legal python identifier
NAME = r'[A-Za-z_]\w*'

# re for matching dictionaries in form variables:
#
#    NAME "[" KEY "]"
#
# Group #1 is NAME, group #2 is KEY
DICTVAR = re.compile(r'(%s)\[(.*)\]$' % NAME)

# re for matching form vars returned by INPUT tags of type image:
#
#    NAME "." [xy]
#
# Group #1 is NAME, group #2 is either 'x' or 'y'.
IMAGEVAR = re.compile(r'(%s)\.([xy])$' % NAME)

del re, NAME

