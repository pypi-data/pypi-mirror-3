WSGI Middleware
===============

.. module:: openid2rp.wsgi

*This module is considered experimental until peer review has been completed.*

The openid2rp WSGI middleware allows integration of OpenID into arbitrary WSGI applications.
It supports a zero-configuration mode where the middleware can be taken as is. However, even
in that mode, the application has to cooperate with the middleware, in sending it the right
requests and expecting results in the right places.

Using this middleware currently requires the webob package.

Simple Usage
------------

In its most simple form, :class:openid2rp.wsgi.Openid2Middleware can be used as a wrapper
for the actual WSGI application. All requests to the application get filtered by the wrapper,
which will send redirects or augment the environ. The application needs to perform the following
steps:

 1. Provide a form with an input field ``openid_identifier``; alternatively, provide links
    to providers with a query parameter ``openid_identifier``. The middleware will look for this
    parameter in all GET and POST requests.
 2. Look for WSGI environment fields ``'openid2rp.identifier'`` or ``'openid2rp.error'``. See below
    for what they contain.

In addition to these steps, applications also SHOULD provide a storage object where the middleware
can persistently store information, at least if subsequent requests may get processed by different
operating system processes, or if the default in-memory storage may consume too much memory.

API Reference
-------------

.. class:: Openid2Middleware(app[, store])

   Wrapper middleware to process OpenID2 login attempts. Objects
   passed as the optional *store* parameter must implement the Store
   interface below. If no store is passed, a
   :class:memstore.InMemoryStore is used.

.. class:: Store()

   A store for openid2rp must implement the following methods. All key and value parameters are
   strings.

.. attribute:: Store.nonce_lifetime

   Minimum lifetime before nonces get discarded from the replay cache. The recommended value is
   5 minutes.

.. method:: Store.start_login(key, value)

   Store a login session under key. Login sessions that are not ended should be expired
   after some time. As a recommended value, users should get at least 10 minutes to log in;
   sessions not ended within a day can certainly be discarded.

.. method:: Store.get_login(key)

   Retrieve a value stored using :meth:`start_login`. If the key is not known, None
   must be returned.

.. method:: Store.end_login(key)

   Remove a login session. Called when a user returns from the provider.

.. method:: Store.add_nonce(nonce)

   Store a nonce in the replay cache. Each nonce has its creation time
   recorded (see :func:`openid2rp.parse_nonce`). Nonces stored for more than
   *nonce_lifetime* can be discarded.

.. method:: Store.has_nonce(nonce)

   Return True if a certain nonce is in the replay cache.

.. method:: Store.add_association(key, expires, value)

   Store a provider association. *expires* specifies the UTC seconds (since 1970)
   when the association can be deleted from the store.

.. method:: Store.get_asssocation(key)

   Return an association stored for a key. If no association can be found, None is returned.

.. class:: memstore.InMemoryStore()

   Default store, storing all key/value pairs in dictionaries. Using this implementation
   is correct if all requests use the same Python process which in turn always uses the same
   store. If the stored values are lost (e.g. after a server restart), the following consequences
   arise:

   - users returning from their OpenID providers in ongoing login sessions will be refused from
     logging in. This may in particular happen if multiple simultaneous server processes all operate
     indepdendent InMemoryStore objects, yet subsquent requests may get dispatched to different servers.

   - attackers attempting a replay attack may succeed if the replay cache is discarded, and the replay
     occurs within the nonce_lifetime.

   - users returning from their OpenID providers will also be unable to login if the provider assoiation
     is lost. In addition, losing the provider session will require to establish a new association on the
     next login attempt for the same user (resp. provider, for provider IDs). Typically, the delay caused
     by that data loss will not be noticable.

WSGI environment effects
------------------------

:class:Openid2Middleware parses the request and looks for an ``openid_identifier`` field. If no such field
is found, and it is not a return URL, the request is passed unmodified.

If the openid_identifier field is present, one of two cases may happen:

 1. Discovery on the ID fails. This may indicate that the ID entered actually is not an OpenID.
    The request is forwarded, with ``'openid2rp.notice'`` being set.

 2. The user is redirected to the provider. The return URL will be the same as the one in the request,
    except that the query parameters are completely rewritten, and include, in particular, ``openid_return``.

When the user returns from the provider, the response is validated, and either ``'openid2rp.identifier'``
or openid2rp.error are set (the latter to a string containing an error message).

If openid2rp.identifier is set, openid2rp.ax and openid2rp.sreg will also be set, namely to dictionary
containing the respective user information.