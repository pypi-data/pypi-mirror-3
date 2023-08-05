wsgiservlets.Session
====================

.. currentmodule:: wsgiservlets

.. class:: Session

   A *Session* is never directly constructed by the programmer, but is
   instantiated via servlet request initialization.  See
   :attr:`WSGIServlet.use_session` for details.

   .. method:: save
   
       Acquire proper locks and call the backend to save the session.
       
   .. method:: revert

       Revert the session data to its originally stored data.

   .. method:: expire

       Expires the session.

   .. attribute:: sid

       The session ID.

   .. attribute:: expires

       The timestamp (seconds since the epoch) after which the session
       expires.

   .. attribute:: is_new

       ``True`` if this is a newly created session during this request.
       

