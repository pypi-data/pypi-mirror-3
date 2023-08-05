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
from time import ctime

class sessions(HTMLPage):

    'How to manage sessions.'

    title = 'State Management, Part 2: Sessions'

    use_session = True
    session_config = {'timeout' : 180} # three minutes
    session_cookie_secret = 'wsgisrv tutorial'

    expirenow = GET_var('', bool) # expire session
    deletenow = GET_var('', bool) # delete session cookie on client

    def prep(self):

        HTMLPage.prep(self)

        if self.expirenow:

            # expire the session and redirect
            self.session.expire()
            self.redirect(self.script_name)
            # does not return

        if self.deletenow:

            # make our response a redirect and delete the cookie.  We
            # can't call redirect(), like above, because we need to
            # set Set-Cookie header with an expiration date
            self.response = HTTPTemporaryRedirect(location=self.script_name)
            self.del_cookie(self.session_cookie_name)
            # raise our response
            raise self.response
          
    def write_content(self):

        # generate cookie/session info
        found = self.found()

        # calculate the number of visists
        visits = self.session['visits'] = self.session.get('visits', 0) + 1

        self.writeln(FORMRESULTS.format(visits = visits,
                                        plural = 's' if visits > 1 else '',
                                        cookiename=self.session_cookie_name,
                                        found=found,
                                        expire=EXPIRELINK,
                                        delete=DELETELINK))
        self.writeln(OVERVIEW)


    def found(self):

        '''Piece together parts of the output based on cookie/session
        existance and validity'''
        
        c = self.cookies.get(self.session_cookie_name)
        if c:
            c = c.value
            # session cookies are signed with 40 character SHA1 digest
            if c[40:] == self.session.sid:
                valid = ('It is valid and will expire %s'
                         % ctime(self.session.expires))
            else:
                valid = ('It expired, so a new session was generated.  '
                         'Refresh the page to see the new cookie value')

            isnew = ('It is a new session.' if self.session.is_new else
                     'It is a reloaded session.')

            found = ('found with value: <em>%s</em><strong>%s</strong>.'
                     '<br>%s.<br>%s'
                     % (c[:40], c[40:], valid, isnew))
                  
        else:
            found = ('not found.  A new session was generated.  '
                     'Refresh the page to see the new cookie value.')

        return found
            


# -*-*- DOC -*-*-            

    css = '''#floatbox {  
    float: right;
    width: 50%;
    padding: 10px;
    margin: 10px;            
    background-color:lightgreen;
    }'''


OVERVIEW = make_overview("""
Each servlet has a `session` attribute; its value is controlled by the
value of another attribute, `use_session`.  If `use_session` evaluates
to `False` (the default) then sessions are not used and the value of
the `session` attribute will be `None`.  If `use_session` evaluates to
`True` then the `session` attribute will be an instance of `Session`
which is a subclass of the standard python `dict` and can be used in
your servlets like any other mapping; the only restriction is that its
keys and values must be pickleable.

A Session has a `save()` method which is automatically called at the
end of a request and saves the `dict` server-side for future retrieval
by subsequent requests using the same session ID. The session ID is
stored on the client via a cookie (yes, cookies must be enabled to use
session management).  If the cookie expires or the session times out,
then a new session will be created automatically.  The session cookie
stored on the client is a signed cookie using a SHA1 digest; the first
40 characters is the digest, the last 32 characters is the session ID.

A Session has two other methods: `revert()` reverts the items in the
session to the contents it had at the beginning of the request.
`expire()` expires the session, clearing its items and flagging the
session cookie for deletion.

A Session has three attributes: `sid`, the session ID; `expires`, a
timestamp (seconds since the epoch) indicating when the session will
expire; `is_new`, a boolean indicating if the session was newly
created for this request.

Session timeout is controlled by the `timeout` item of
`session_config`, an attribute of servlets (view the source to see how
it is set for this tutorial).  The value is in seconds (default: 1800,
or thirty minutes) and for this demo is set to three minutes.

Other servlet attributes that affect sessions:

  * `session_cookie_name`: the name of the cookie stored on the
    client.  The default value is `wsgisrv_sid`.
  * `session_cookie_secret`: THIS MUST BE SET to use sessions.  This is
     the seed for the signed cookie digest.
  * `session_config`: mentioned above, this is a mapping containing
    items that configure general session behaviour
  * `session_backend`: a class that subclasses
    `wsgiservlets.SessionBackend` and manages the backend storage of
    sessions.  As of this writing there is only one backend,
    `FileSessionBackend`, which stores sessions as pickled data in a
    directory hierarchy.
  * `session_backend_init`: a mapping which configures the session
    backend.  For FileSessionBackend there is only one item in the
    mapping, `cachedir` which is the root directory for saving
    sessions.  The default value is `{cachedir}`.
  
This servlet demonstrates using sessions with a trivial
*how-many-times-have-I-visited-this-page* counter.  Reload the page
and watch the counter.
""".format(cachedir=FILESESSION_CACHEDIR))


FORMRESULTS = ("""<div id="floatbox">
<p>The session cookie name is <code>{cookiename}</code> and it was {found}</p>

You can expire it by clicking {expire}.<br>
You can delete the cookie by clicking {delete}.

<p>You have visited this page <strong>{visits}</strong> time{plural}.</p>
</div>
""")

EXPIRELINK = '<a href="?expirenow=1">here</a>'
DELETELINK = '<a href="?deletenow=1">here</a>'
