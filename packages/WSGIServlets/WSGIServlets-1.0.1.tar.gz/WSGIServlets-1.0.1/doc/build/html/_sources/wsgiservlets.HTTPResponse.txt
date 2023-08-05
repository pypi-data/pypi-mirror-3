wsgiservlets.HTTPResponse
=========================

.. currentmodule:: wsgiservlets

.. autoexception:: HTTPResponse
    :members:

    .. automethod:: __init__
    

.. data:: http_responses_map

   A mapping of HTTP status codes to :class:`HTTPResponse` subclasses.
   I.e::

     >>> http_reponses_map[404] is HTTPNotFound
     True


Responses are Exceptions     
^^^^^^^^^^^^^^^^^^^^^^^^

Because :class:`HTTPResponse` subclasses :exc:`Exception`, any of
these responses can be raised as an exception to abort the request.
For example, if it is programmitcally determined that a resource
doesn't exist, one can write::

    if cannot_find_smoke_shifter:
        raise HTTPNotFound('Could not find the left-handed smoke shifter')


HTTP 1.1 Responses
^^^^^^^^^^^^^^^^^^

Each repsonse defined in HTTP 1.1 is represented by a subclass of
:exc:`HTTPRepsonse`.  The list of responses, their code and titles:
  

.. exception:: HTTPContinue

    * **status** -- ``100``
    * **title** -- ``Continue``

.. exception:: HTTPSwitchingProtocols

    * **status** -- ``101``
    * **title** -- ``Switching Protocols``

.. exception:: HTTPOK

    * **status** -- ``200``
    * **title** -- ``OK``

.. exception:: HTTPCreated

    * **status** -- ``201``
    * **title** -- ``Created``

.. exception:: HTTPAccepted

    * **status** -- ``202``
    * **title** -- ``Accepted``

.. exception:: HTTPNonAuthoritativeInformation

    * **status** -- ``203``
    * **title** -- ``Non-Authoritative Information``

.. exception:: HTTPNoContent

    * **status** -- ``204``
    * **title** -- ``No Content``

.. exception:: HTTPResetContent

    * **status** -- ``205``
    * **title** -- ``Reset Content``

.. exception:: HTTPPartialContent

    * **status** -- ``206``
    * **title** -- ``Partial Content``

.. exception:: HTTPMultipleChoices

    * **status** -- ``300``
    * **title** -- ``Multiple Choices``

.. exception:: HTTPMovedPermanently

    * **status** -- ``301``
    * **title** -- ``Moved Permanently``

.. exception:: HTTPFound

    * **status** -- ``302``
    * **title** -- ``Found``

.. exception:: HTTPSeeOther

    * **status** -- ``303``
    * **title** -- ``See Other``

.. exception:: HTTPNotModified

    * **status** -- ``304``
    * **title** -- ``Not Modified``

.. exception:: HTTPUseProxy

    * **status** -- ``305``
    * **title** -- ``Use Proxy``

.. exception:: HTTPUnused

    * **status** -- ``306``
    * **title** -- ``Unused``

.. exception:: HTTPTemporaryRedirect

    * **status** -- ``307``
    * **title** -- ``Temporary Redirect``

.. exception:: HTTPBadRequest

    * **status** -- ``400``
    * **title** -- ``Bad Request``

.. exception:: HTTPUnauthorized

    * **status** -- ``401``
    * **title** -- ``Unauthorized``

.. exception:: HTTPPaymentRequired

    * **status** -- ``402``
    * **title** -- ``Payment Required``

.. exception:: HTTPForbidden

    * **status** -- ``403``
    * **title** -- ``Forbidden``

.. exception:: HTTPNotFound

    * **status** -- ``404``
    * **title** -- ``Not Found``

.. exception:: HTTPMethodNotAllowed

    * **status** -- ``405``
    * **title** -- ``Method Not Allowed``

.. exception:: HTTPNotAcceptable

    * **status** -- ``406``
    * **title** -- ``Not Acceptable``

.. exception:: HTTPProxyAuthenticationRequired

    * **status** -- ``407``
    * **title** -- ``Proxy Authentication Required``

.. exception:: HTTPRequestTimeOut

    * **status** -- ``408``
    * **title** -- ``Request Time-out``

.. exception:: HTTPConflict

    * **status** -- ``409``
    * **title** -- ``Conflict``

.. exception:: HTTPGone

    * **status** -- ``410``
    * **title** -- ``Gone``

.. exception:: HTTPLengthRequired

    * **status** -- ``411``
    * **title** -- ``Length Required``

.. exception:: HTTPPreconditionFailed

    * **status** -- ``412``
    * **title** -- ``Precondition Failed``

.. exception:: HTTPRequestEntityTooLarge

    * **status** -- ``413``
    * **title** -- ``Request Entity Too Large``

.. exception:: HTTPRequestUriTooLarge

    * **status** -- ``414``
    * **title** -- ``Request-URI Too Large``

.. exception:: HTTPUnsupportedMediaType

    * **status** -- ``415``
    * **title** -- ``Unsupported Media Type``

.. exception:: HTTPRequestedRangeNotSatisfiable

    * **status** -- ``416``
    * **title** -- ``Requested Range Not Satisfiable``

.. exception:: HTTPExpectationFailed

    * **status** -- ``417``
    * **title** -- ``Expectation Failed``

.. exception:: HTTPInternalServerError

    * **status** -- ``500``
    * **title** -- ``Internal Server Error``

.. exception:: HTTPNotImplemented

    * **status** -- ``501``
    * **title** -- ``Not Implemented``

.. exception:: HTTPBadGateway

    * **status** -- ``502``
    * **title** -- ``Bad Gateway``

.. exception:: HTTPServiceUnavailable

    * **status** -- ``503``
    * **title** -- ``Service Unavailable``

.. exception:: HTTPGatewayTimeOut

    * **status** -- ``504``
    * **title** -- ``Gateway Time-out``

.. exception:: HTTPVersionNotSupported

    * **status** -- ``505``
    * **title** -- ``HTTP Version not supported``

