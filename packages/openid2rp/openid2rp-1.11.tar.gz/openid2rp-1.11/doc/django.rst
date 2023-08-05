Django Authentication Module
============================

.. module:: openid2rp.django

This is the implementation of a `Django
<http://www.djangoproject.com/>`_ authentication backend for OpenID,
based on the openid2rp package. It is automatically installed together
with openid2rp.

In contrast to most (all ?) other Django OpenID authentication
packages, this one does not try to cover any view aspects. All error
cases are reported by exceptions, which you can render in whatever way
you prefer.

Using the authentication backend
********************************
It is assumed that you have a working Django app with standard login functionality.

Add ``openid2rp.django`` to ``INSTALLED_APPS``. Example::

	INSTALLED_APPS = (
		'django.contrib.auth',
		'django.contrib.contenttypes',
		'django.contrib.sessions',
		'django.contrib.sites',
		'django.contrib.admin',
		'openid2rp.django',
		'<yourapp>.front' )

Add ``openid2rp.django.auth.Backend`` to ``AUTHENTICATION_BACKENDS``.Example::

	AUTHENTICATION_BACKENDS = (
		'django.contrib.auth.backends.ModelBackend',
		'openid2rp.django.auth.Backend' )

Do once a ``python manage.py syncdb`` to create the relevant tables.

The next step is to modify your existing login view. You need accept
an OpenID URI as alternative to username / password. There are
JavaScript support libraries available to help you with the URIs for
the different providers and their logos.

Add a second view, which will receive the answer from the OpenID
authentication provider.

In your original login view code, call
``openid2rp_django.auth.preAuthenticate`` instead of Django's
``authenticate`` if you want to perform an OpenID
authentication. Input parameters are the user-provided OpenID URI, and
the (absolute !) URL of the newly created view. The result of this
call is an ``HttpResponse`` object you must return as view result.

After authentication, the provider will send the users browser back to
your newly created second login view. Call Django's ``authenticate``
in there with one keyword arguments ``openidrequest`` for the request object.
The result is a Django ``User`` object
(if a user record in the database has this claim attached), a Django
``AnonymousUser`` object (if the claim could not be found, but OpenID
authentication was ok), or an Exception if anything went wrong. In the
second case, you might offer some user registration facility. You can
use ``openid2rp_django.auth.linkOpenID`` to assign claims to Django
user objects, so that ``authenticate`` is successfull the next time.

Functions
*********

The Django application can use the following API:

.. function:: openid2rp_django.auth.preAuthenticate(uri, answer_url, sreg = (('nickname', 'email'), ()), ax = ((openid2rp.AX.email, openid2rp.AX.first, openid2rp.AX.last), ()),reuse_session = True) -> response

``uri`` is the OpenID URI input from the user. ``answer_url`` is the
absolute address of the view that will later call
``authenticate()``. You can realize this view in whatever way you
prefer, for example also by using the original login view with another
GET parameter. ``sreg`` resp. ``ax`` allow you to request a set of
information attributes from the authentication provider. Check the
openid2rp and OpenID documentation for details.

``reuse_session`` is intended as possibility for the application to
work around broken OpenID providers. It disables the re-using of
OpenID sessions for the given claim. If your provider sends an
'openid.invalidate_handle' parameter in the returning request,
and the OpenID authentication ends with a session error,
try to set this to 'False'. Normally, you don't need to touch
this parameter.

The result is the ``HttpResponse`` object you should directly
return from the view code after calling ``preAuthenticate``. It
contains a 307 redirection to the authentication provider URL, so that
the user's browser goes forward to the actual provider authentication
screen. 

If something goes wrong, one of the following errors is raised:
	
* ``IncorrectURIError``: The provided URI couldn't be normalized. 
* ``IncorrectClaimError``: The OpenID discovery step for this claim
  failed. This might be a typo, but can also be reasoned by an
  unavailable provider.

.. function:: django.contrib.auth.authenticate(openidrequest=None) -> user

In the handling of the providers redirection back to your site, you
need to call Django's ``authenticate`` function with a keyword
parameter. ``request`` is the ``HttpRequest`` input object for your
view code. The authentication provider fetches all relevant
information from it. 

The result of this call is either:

* A Django ``User`` object. In this case, the OpenID claim was
  successfully authenticated, and the backend found a user in the
  database with this claim attached. The object as additional
  attributes:
	
	* ``openid_claim``: The claim that was finally
          authenticated. Depending on the OpenID provider, this might
          or might not be the original input. In a later call
          to ``linkOpenID``, use this one.
	* ``openid_ax``: A dictionary of received AX values. The
          ``django.contrib.auth.AX`` dictionary contains a list of
          standardized key names. Check the openid2rp documentation
          for more information.
	* ``openid_sreg``: A dictionary of received SREG values.	
		
* A Django ``AnonymousUser`` object. In this case, the claim could not
  be related to any user in the database, but the OpenID
  authentication was ok. The object has the same additional attributes
  as above. In this situation, you should normally proceed with some
  new user registration functionality. You can use the AX / SREG data
  to pre-fill some registration form.

* One of the following exceptions:
	
	* ``MissingSessionError``: There is no stored session for this
          result. This typically means that you forgot to start with
          ``preAuthenticate``.
	* ``AuthenticationError``: Something went wrong in the OpenID
          authentication process. The exception message contains more
          information.
	* ``IncompleteAnswerError``: This is normally the providers fault.
	* ``MultipleClaimUsageError``: The authenticated claim was
          linked to multiple users, which is not valid. You need to
          correct your database.
	* ``ReplayAttackError``: The nonce checking mechanisms
          identified an answer that was already given before.
	* ``TookTooLongError``: The authentication at the provider
          side took too long. You can override the default value (5
          min) in your settings file with the parameter
          ``OPENID2RP_MAXLOGINDELAY``.
	
.. function:: openid2rp_django.auth.getOpenIDs(user) -> ids

Returns a string list of stored OpenID claim URIs for this Django user
object. This is intended for your user settings view.
	
.. function:: openid2rp_django.auth.linkOpenID(user, claim) -> 

Links the given Django user object to the given OpenID claim.

.. function:: openid2rp_django.auth.unlinkOpenID(user, claim) -> 

Unlinks the given Django user object from the given OpenID claim. This
is intended for your user settings view.

Time, clocks, and the ordering of events
****************************************

For the different timestamp checks, the authentication backend allows
a maximum derivation of authentication provider clock and relaying
party clock of 5 min. You can override this default value in your
Django settings file with the parameter ``OPENID2RP_MAXTIMESHIFT``.
