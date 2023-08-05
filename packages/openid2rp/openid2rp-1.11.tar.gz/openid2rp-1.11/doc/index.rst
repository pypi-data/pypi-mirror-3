Welcome to openid2rp!
=====================

.. module:: openid2rp

This is a library to implement OpenID 2.0 Relying Parties (RP). The RP
itself will be a web application, and needs to implement all user
interface, as well as to provide storage for certain persistent data.
The assumption is that the web application has its own management of
user accounts already, so OpenID will merely provide convenience for
end users who wish to use their OpenID with the web application.

The following three scenarios need to be considered:

- an existing user logs in with an OpenID already known to the
  application.

- an existing user wants to add an OpenID to his account. The
  recommended procedure is to let the user first log in regularly,
  then claim the OpenID.

- a new user logs in with a yet-unknown OpenID, and needs to be
  registered.

This library will implement the protocol between the application and
the OpenID provider, as well as produce redirects to be sent to the
user's browser, and process incoming redirects from the provider.

The openid2rp package includes a stand-alone server, as an example
and a test; run this as ``python -m openid2rp.testapp``.

The openid2rp package also provides a Django authentication backend, which is described separately:

.. toctree::

   django
   wsgi

Terminology
-----------

A *user* tries to authenticate to a *Relying Party (RP)*, referring to
an OpenID *Provider (OP)* for verification. The objective is to assert
that the user owns his *claimed identifier*. He can either type in
that claimed identifier during login, or select a *OP identifier*
instead (in which case the provider will identify the user first, and
report the claimed identifier to the RP).

For any identifier entered by the user, *normalization* must be
performed. This will add an http: prefix, missing slashes,
etc. Identity comparison should always use normalized identifiers.

The relying party first performs *discovery*, determining whether the
user-entered identifier is a claimed identifier or a provider
identifier, where the provider is located, and what *op_local
identifier* the provider may actually be able to validate. Discovery
gives users the opportunity to switch providers without changing
claimed identifiers.

After discovery, the RP creates an *association* with the provider
which produces an *association handle* and a *mac key* (MAC = Message
Authenticity Code). As information is also transmitted through the
user's browser, this assocation guarantees that the user won't be able
to fill in fake data.


Authentication Functions
------------------------

The application can use the following API:

.. function:: normalize_uri(uri) -> kind, url

  Returns either 'xri' or 'uri' as kind. Applications should always
  normalize URIs claimed by the end user, and perform identity
  comparisons on the normalized URIs only.

.. function:: discover(url) -> (services, op_endpoint, op_local)

  Perform OpenID discovery on the URL. Return the list of services
  discovered (which should include either the signon or the server, in
  either version 1.0 or 2.0), the provider endpoint to be used for
  communication, and the provider-local identifier that the provider
  will validate. Applications need to remember the claimed identifier,
  and only identify the user by that string; the op_identifier is then
  not further relevant to the application.

.. function:: resolve_xri(xri, proxy='xri.net') -> (canonical_id, services, op_endpoint, op_local)

  Perform OpenID discovery for XRI identifiers, i.e. XRI resolution.
  This has the same result as discover, but also returns the canonical
  identifier of the user, which is the one that must be used to identify
  an account. Users may desire that the original XRI identifier is also
  displayed. Optionally, a XRI proxy resolver may be specified; the
  proxy resolution uses HTTP.

.. function:: associate(services, url) -> dict

  Setup an association between the service and the provider. services
  must be the list of services that was returned from discovery; url
  is the provider endpoint URL. The resulting dictionary must be
  preserved atleast until authentication is completed, and can be
  reused at most until the 'expires_in' amount of seconds has passed.

.. function:: request_authentication(services, url, assoc_handle, return_to, claimed=None, op_local=None, realm=None, sreg=(('nickname', 'email'), ()), ax = ((ax.email, ax.first, ax.last), ())) -> url

  Create an authentication request; return the URL that the user
  should be redirected to. services and url are the same parameters as
  in associate; assoc_handle is the 'assoc_handle' field of the
  association and return_to is the URL on which the application will
  receive incoming provider redirects.  If the user had claimed an
  identifier, this one and op_local from the discovery should be
  passed. Passing the realm allows the RP to receive the same
  identification information for multiple return_to URLs; for this to
  work, the return_to URL must match the realm (see 9.2. of the OpenID
  spec how matching is defined).

  sreg is a pair of required and optional SREG (simple registration)
  fields. Applications should declare those fields required that they
  absolutely need to complete user registration; i.e. failure to provide
  some of the required values will cause user interaction to let the
  user fill in the missing values.

  ax is a pair of required and "if available" AX (attribute exchange)
  attribute types. The provider should use these lists as a guidance
  what attributes to send back; the specification allows it to
  interpret this request in any way it pleases. Values must be URL,
  the AX object provides a shortcut notation for common attributes.

.. function:: verify(response, discovery_cache, find_association, nonce_seen) -> signed, claimed_id

  Process an authentication response. *response* is the query string as
  given in the original URL (i.e. as the CGI variable QUERY_STRING).

  *discovery_cache* is a function taking an URI and returning the
  same result as discover would; applications should use it to cache
  the discovery result between the start of the login process until
  the user completes the login. If no cache information is found,
  None shall be returned.

  *find_association* is a function taking an assoc_handle, and returning
  a session dictionary or None. The dictionary must minimally contain
  the assoc_handle and the mac_key.

  *nonce_seen* is a function taking a nonce, returning a boolean that 
  indicates whether the nonce has been seen. It may also store the
  nonce as a side-effect; alternatively, the application can
  separately store it when it successfully processed the
  authentication request. Nonces older than one hour can be deleted
  from the storage.

.. function:: authenticate(session, response) -> None

  Process an authentication response.  session must be the established
  session (minimally including assoc_handle and mac_key), response is
  the query string as given in the original URL (i.e. as the CGI
  variable QUERY_STRING).  If authentication succeeds, return the
  list of signed fields.  If the user was not authenticated,
  NotAuthenticated is raised.  If the HTTP request is invalid (missing
  parameters, failure to validate signature), different exceptions
  will be raised, typically ValueError.

  Callers must check openid.response_nonce for replay attacks.

  .. deprecated:: 1.11
     Use :func:`verify` instead.


Discovery Utility Functions
---------------------------

.. function:: is_op_endpoint(services) -> bool

   Determine whether the discovered identifier is an OP identifier or
   a claimed identifier. XXX this should be called is_op_identifier.

Response Utility Functions
--------------------------

.. function:: parse_nonce(nonce) -> timestamp


   Extract the datetme.datetime timestamp from a response_nonce value.
   Applications should set a reasonable
   conservative timeout (e.g. one hour) for the transmission of a
   nonce from the provider to the RP. Nonces older than now()-timeout
   can be discarded as replays right away. Younger nonces should be
   checked against the replay cache. Cache entries older than the
   timeout can be discarded.

.. function:: get_namespaces(response) -> dict

   Return a dictionary of namespace : prefix mappings, to be used
   for additional attributes.

.. function:: get_ax(response, ns, validated) -> dict

   Return a dictionary of attribute exchange (AX) properties,
   in the type-url : value format.

.. function:: get_sreg(response, validated) -> dict

   Return the dictionary of simple registration parameters in resp,
   with the openid.sreg. prefix stripped.

.. function:: get_email(response) -> str

   Return the user's proposed email address. It first tries the simple
   registration attribute (SREG), and then the axschema AX attribute.
   Return None if neither is available.

Response Fields
---------------

Applications might be interested in the following response
fields. Before trusting a specific field, they should verify that the
field value was signed.

* openid.mode: should be "id_res", and not "cancel"; this is checked
  by authenticate.

* openid.claimed_id: Claimed identifier as returned from the
  provider. If the original user-supplied identifier entered by the
  user was an OP identifier, then this is the value identifying the
  user. If it was a claimed identifier, then the provider is generally
  not able to verify the claim for this identifier. The RP should
  create a separate session for each such identifier, and verify that
  the session is associated with the same identifier as returned in
  claimed_id.

* openid.identity: OP-local identifier as returned from the
  provider. This shouldn't be used for identification of the user.

* openid.response_nonce: Nonce to prevent replay attacks. Applications
  should establish a replay cache, detecting when the same nonce is
  provided twice by the user's browser.

* openid.signed: list of signed fields; converted into a Python list
  by authenticate.

* openid.sreg.*: simple registration (SREG) properties returned by the
  OP. This library requests as required parameters nickname and email,
  and no optional parameters. Possible keys are:

  * nickname
  * email
  * fullname
  * dob (date of birth)
  * gender (M or F)
  * postcode
  * country
  * language
  * timezone

* AX attributes, as processed by
  get_ax. http://www.axschema.org/types/ is a registry for attribute types.

AX Mapping
----------

To simplify usage of AX, shortcut names of the form openid2rp.AX.NAME
are provided. These can be used for lookup in the get_ax result, and
for specifying required and "if available" attributes for
request_authentication.

========  ============================================
Name      URL
========  ============================================
nickname  http://axschema.org/namePerson/friendly
email     http://axschema.org/contact/email
fullname  http://axschema.org/namePerson
dob       http://axschema.org/birthDate
gender    http://axschema.org/person/gender
postcode  http://axschema.org/contact/postalCode/home
country   http://axschema.org/contact/country/home
language  http://axschema.org/pref/language
timezone  http://axschema.org/pref/timezone
first     http://axschema.org/namePerson/first
last      http://axschema.org/namePerson/last
========  ============================================


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

