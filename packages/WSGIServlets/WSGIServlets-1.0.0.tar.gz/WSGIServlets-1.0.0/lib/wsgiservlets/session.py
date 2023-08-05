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

import Cookie
import cPickle as pickle
import os
import fcntl
import hmac
from hashlib import md5, sha1
import random
from time import time as now

__all__ = ['SESSION_TIMEOUT', 'FILESESSION_CACHEDIR',
           'SignedCookie', 'signed_cookie_class',
           'SessionBackend', 'FileSessionBackend',
           'session_init', ]

# default session expiration timeout...30 minutes
SESSION_TIMEOUT = 1800
# the root directory of the file-based session storage
FILESESSION_CACHEDIR = '/tmp/wsgisrv_sess'

class SignedCookie(Cookie.BaseCookie):

    """Extends python standard library Cookie.BaseCookie with a
    digital signature"""

    @property
    def secret(self):
        '''A SignedCookie needs a secret (a string to seed the digital
        signature).  It is purposefully unimplemented in the base
        class, forcing developers to subclass, e.g:

            class MySignedCookie(SignedCookie):
                secret = "my application secret"

        Doing it this way allows the constructor to be exactly the
        same as other standard Cookie.BaseCookie subclasses, i.e.,
        many impls of signed cookies require the secret as part of the
        constructor, making the interface different than other
        BaseCookie subclasses and therefore not an easy drop-in
        replacement.

        See signed_cookie_class for a convenience function to generate
        SignedCookie classes.
        '''
        raise NotImplementedError

    def value_decode(self, val):

        digest = hmac.new(self.secret, val[40:], sha1).hexdigest()
        return (val[40:], val) if digest == val[:40] else (None, val)
        
    def value_encode(self, val):

        strval = str(val)
        digest = hmac.new(self.secret, strval, sha1).hexdigest()
        return strval, digest + strval


def signed_cookie_class(thesecret):

    '''Given a secret, returns a subclass of SignedCookie with the
    given secret.'''

    class anon_scc(SignedCookie):
        secret = thesecret

    return anon_scc


class SessionBackend(object):
    'Abstract base class for backend storage engines for sessions'

    def do_acquire_shared_lock(self, sid):
        '''Acquire a shared lock for the session with ID sid.
        Multiple requests can hold a shared lock.'''

        raise NotImplementedError

    def do_release_shared_lock(self, sid):
        'Release the shared lock for the session with ID sid.'

        raise NotImplementedError

    def do_acquire_exclusive_lock(self, sid):
        '''Acquire an exclusive lock for the session with ID sid.
        Only one request can hold an exclusive lock.'''

        raise NotImplementedError

    def do_release_exclusive_lock(self, sid):
        'Release the exclusive lock for the session with ID sid.'

        raise NotImplementedError

    def do_load(self, sid):
        '''Load the session with ID sid from storage.  This method
        should return a two-element tuple:

            (expires, data)

        Where expires is the expiration timestamp (in seconds since
        the epoch) and data is a suitable argument to dict.update(),
        e.g., a sequence of two-element tuples, or a dict.

        If the sid does not exist or the session is invalid it should
        return: (None, None).
        '''
        
        raise NotImplementedError


    def do_save(self, session):
        '''Store the session instance in the backend storage.  The
        only data that needs to be saved is the expiration timestamp
        and data.
        '''

        raise NotImplementedError
    
    
class FileSessionBackend(SessionBackend):

    '''A file-based session store: each session is stored in its own
    file.  The directory hierarchy is:

         cachedir/
                  files/    
                  locks/

    Note: no files or locks are deleted from the storage.  This is
    left as an exercise for the system administrator.  One possible
    method is a cron job such as:

        `find cachedir -type f -mtime +TIME | xargs rm`

    '''

    def __init__(self, config):
        '''Insure the root directories of the cachedir directory
        hierarchy are created.'''

        cachedir = config.get('cachedir', FILESESSION_CACHEDIR)

        self.lockdir = lockdir = os.path.join(cachedir, 'locks')
        self.filedir = filedir = os.path.join(cachedir, 'files')
        self.lock = None
        if not os.path.isdir(cachedir):
            os.makedirs(cachedir)
            os.mkdir(lockdir)
            os.mkdir(filedir)

    def _open_lock_file(self, sid, mode):
        'Set self.lock to an open file for locking for sid'

        # find the directory for this lock file and create if necessary
        lockdir = os.path.join(self.lockdir, sid[0], sid[:2])
        if not os.path.isdir(lockdir):
            os.makedirs(lockdir)
        # create the lock file
        lockfile = os.path.join(lockdir, sid + '.lock')
        self.lock = os.open(lockfile, mode)

    def _get_cache_file(self, sid):
        'Return the path to the cache file'

        # find the directory for this cache file and create if necessary
        filedir = os.path.join(self.filedir, sid[0], sid[:2])
        if not os.path.isdir(filedir):
            os.makedirs(filedir)
        # return the path
        return os.path.join(filedir, sid + '.cache')

    def _release_lock(self):
        'Release the lock on self.lock and close it.'
        
        lock = self.lock
        if lock is not None:
            fcntl.flock(lock, fcntl.LOCK_UN)
            os.close(lock)
            self.lock = None

    #################################################
    # LOCKS are created using fcntl.flock
    #
    def do_acquire_shared_lock(self, sid):

        self._open_lock_file(sid, os.O_CREAT | os.O_RDONLY)
        fcntl.flock(self.lock, fcntl.LOCK_SH)
        
    def do_release_shared_lock(self, sid):

        self._release_lock()
            
    def do_acquire_exclusive_lock(self, sid):

        self._open_lock_file(sid, os.O_CREAT | os.O_WRONLY)
        fcntl.flock(self.lock, fcntl.LOCK_EX)

    def do_release_exclusive_lock(self, sid):

        self._release_lock()
    #
    #################################################

    def do_load(self, sid):
        'Load the pickle from the cache file'
        
        cachefile = self._get_cache_file(sid)
        if not os.path.exists(cachefile):
            return None, None
        with open(cachefile, 'rb') as pfile:
            expires, data = pickle.load(pfile)
        return expires, data

    def do_save(self, session):
        'Save the expiration and data to a pickle file'
        
        cachefile = self._get_cache_file(session.sid)

        with open(cachefile, 'wb') as pfile:
            pickle.dump((session.expires, session.items()), pfile,
                        pickle.HIGHEST_PROTOCOL)
        

def session_init(sid, backend, config):

    '''Create a Session instance for the given session ID, backend
    storage and configuration options.

    '''

    class Session(dict):
        'The session class'

        def __init__(self, sid, data, expires, is_new, backend, hold_exclusive):
            self.sid = sid
            self.expires = expires
            self.is_new = is_new
            self.__be = backend
            self.__he = hold_exclusive
            self.__data = data

            self.update(data)

        def save(self):
            'Acquire proper locks and call the backend to save the session'

            backend = self.__be

            if not self.__he:
                backend.do_acquire_exclusive_lock(self.sid)
            try:
                backend.do_save(self)
            finally:
                backend.do_release_exclusive_lock(self.sid)
                self.__he = False

        def revert(self):
            'Revert the session data to its originally stored data'

            self.clear()
            self.update(self.__data)

        def expire(self):
            'Expire the session'

            self.clear()
            self.expires = 1

    # How many seconds into the future will the session expire
    timeout = config.get('timeout', SESSION_TIMEOUT)

    # Typical session handling for a request will be:
    #
    #   1. acquire a shared lock for the sid
    #   2. load the the session
    #   3. release the shared lock
    #   4. use the session during the request
    #   5. acquire an exclusive lock
    #   6. save the session
    #   7. release the exclusive lock
    #
    # If hold_exclusive_lock is True, then session handling will be as
    # follows:
    #
    #   1. acquire an exclusive lock
    #   2. use the session
    #   3. release the lock
    #
    # This will, in effect, serialize requests for the *same* session,
    # which gives accurate results for cumulative changes, but at a
    # performance cost.
    #
    hold_exclusive = config.get('hold_exclusive_lock', False)
                         
    data = None
    # An sid was specified so call the backend to retrieve the session
    if sid is not None:

        # shared or exclusive lock?
        if hold_exclusive:
            backend.do_acquire_exclusive_lock(sid)
        else:
            backend.do_acquire_shared_lock(sid)
        try:
            # call the backend
            expires, data = backend.do_load(sid)
            is_new = False
            # if it expired, flag it as such
            if expires is not None and expires > 0 and now() >= expires:
                data = None
        except:
            data = None
        finally:
            if not hold_exclusive:
                backend.do_release_shared_lock(sid)

    # A new session, so generate an sid
    if sid is None or data is None:
        sid = md5('%f%d%f%d' % (now(),            # timestamp   
                                id([]),           # random mem address
                                random.random(),  # random number
                                os.getpid()       # PID
                                )).hexdigest()
        expires = now() + timeout if timeout > 0 else 0
        is_new = True
        data = {}

    # return the Session instance
    return Session(sid, data, expires, is_new, backend, hold_exclusive)
