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

import sys
import os

from wsgiservlets import Dispatcher
from TutorialBase import TutorialBase

servlet_mapping = {}

importcode = '''
import {t}
{t} = reload({t})
servlet_mapping["{t}"] = {t}.{t}
servlet_mapping["brief_{t}"] = {t}.{t}
'''

# The directory containing the tutorial
docroot = os.path.dirname(sys.modules[TutorialBase.__module__].__file__)

# import all the tutorials listed in TutorialBase plus the home page,
# the jsonrpc server, and the reference manual
for tutorial in TutorialBase.tutorials + ['index', 'jsonrpc_srv', 'ref',]:
    exec(importcode.format(t=tutorial))

## for modwsgi and the like
# application = Dispatcher(servlet_mapping = servlet_mapping,
#                         docroot = docroot)

if __name__ == '__main__':

    port = 8000
    if len(sys.argv) == 2:
        try:
            port = int(sys.argv[1])
        except:
            print >> sys.stderr, 'usage: %s [port]' % sys.argv[0]
            sys.exit(1)

    print 'Starting the tutorial on port:', port
    print 'In your browser, visit http://localhost:%d/' % port
    try:
        Dispatcher.test_server(port=port,
                               servlet_mapping = servlet_mapping.copy(),
                               docroot = docroot,
                               forbid_extensions = ('.pyc', '.pyo'))
    except KeyboardInterrupt:
        pass
    
