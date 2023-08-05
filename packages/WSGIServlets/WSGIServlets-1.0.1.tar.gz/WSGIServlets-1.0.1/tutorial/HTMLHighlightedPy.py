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

import tokenize, keyword, cgi
from cStringIO import StringIO

class HTMLHighlightedPy:


    colors = {'NUMBER'  : 'blue',
              'STRING'  : 'brown',
              'COMMENT' : 'red',
              'DEF'     : 'green',
              'KEYWORD' : 'blue'}

    bgcolor = '#dddddd'

    def __init__(self, src):

        # store line offsets (first line is 1)
        lines = [None, 0]
        pos = 0
        while True:
            pos = src.find('\n', pos) + 1
            if not pos: break
            lines.append(pos)

        pos = 0
        prev_tok_is_def = False

        out = StringIO()

        for (tok_type, tok_str, (srow, scol), (erow, ecol), line) \
                in tokenize.generate_tokens(StringIO(src).readline):

            # calculate new position
            newpos = lines[srow] + scol

            # check for special "tokens"
            iskeyword = tok_type==tokenize.NAME and keyword.iskeyword(tok_str)
            isdefname = tok_type==tokenize.NAME and prev_tok_is_def

            # write text that's been skipped by tokenizer
            if newpos > pos:
                out.write(cgi.escape(src[pos:newpos]))
                pos = newpos

            # get the correct color
            if iskeyword:
                color = self.colors.get('KEYWORD')
            elif isdefname:
                color = self.colors.get('DEF')
            else:
                color = self.colors.get(tokenize.tok_name[tok_type])

            # escape token and write it out
            escaped = cgi.escape(tok_str)
            if color:
                out.write('<span style="color:%s">%s</span>' % (color,escaped))
            else:
                out.write(escaped)

            # calculate position
            pos += len(tok_str)
            prev_tok_is_def = iskeyword and tok_str in ['def', 'class']

        # cache the html in the instance
        self.html = '''
<pre id="src" style="display:none;background-color:%s;padding:10px;border-style:solid">
%s
</pre>
''' % (self.bgcolor, out.getvalue())
        # free up the IO
        out.close()

    def __str__(self):
        return self.html

if __name__ == '__main__':

    import sys

    if len(sys.argv) != 2:
        print >> sys.stderr, 'usage: %s python_file' % sys.argv[0]
        sys.exit(1)

    try:
        src = open(sys.argv[1]).read()
    except IOError, msg:
        print >> sys.stderr, msg
        sys.exit(1)

    print '<html>\n<head>\n<title>%s</title>\n</head>\n<body>'
    print HTMLHighlightedPy(src)
    print '</body>\n</html>'
