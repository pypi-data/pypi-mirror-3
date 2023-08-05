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

from wsgiservlets import *
import os.path

RELPATH_TO_MAN = '../doc/build/html'

class ref(WSGIServlet):

    use_form = False
    use_session = False

    def _lifecycle(self):

        pi = self.path_info
        if pi: pi = pi[1:]
        if not pi:
            self.redirect('/ref/index.html')

        path = os.path.join(RELPATH_TO_MAN, pi)
        if not os.path.exists(path):
            raise HTTPNotFound('Could not find: ' + path)

        self.send_file(path)
