import cPickle, webob, time, random, calendar
import openid2rp, memstore

class Openid2Middleware(object):
    def __init__(self, app, store = None):
        self.app = app
        if not store:
            store = memstore.InMemoryStore()
        self.store = store
        # not yet used
        self.return_to = None

    def __call__(self, environ, start_response):
        request = webob.Request(environ)

        if 'openid_identifier' in request.params:
            return self.login(request, start_response)

        if 'openid_return' in request.params:
            return self.returned(request, start_response)

        return self.app(environ, start_response)

    def login(self, req, start_response):
        kind, claimed_id = openid2rp.normalize_uri(req.params['openid_identifier'])
        if kind == 'xri':
            # XRIs are not supported. Report this to the application as an error
            return self.error(req.environ, start_response, 'XRIs are not supported')
        res = openid2rp.discover(claimed_id)
        if not res:
            # not an OpenID
            req.environ['openid2rp.notice'] = 'discovery failed'
            return self.app(req.environ, start_response)
        services, op_endpoint, op_local = res

        assoc = self.store.get_association(claimed_id)
        if not assoc:
            now = int(time.time())
            # XXX error handling
            assoc = openid2rp.associate(services, op_endpoint)
            assoc_handle = assoc['assoc_handle']
            expires = now + int(assoc['expires_in'])
            mac_key = assoc['mac_key']
            saved_assoc = cPickle.dumps((assoc_handle, mac_key))
            self.store.add_association(claimed_id, expires, saved_assoc)
            self.store.add_association(assoc_handle, expires, saved_assoc)
        else:
            assoc_handle, mac_key = cPickle.loads(assoc)

        session = str(random.getrandbits(40))
        self.store.start_login(session, cPickle.dumps((claimed_id, assoc_handle)))

        if self.return_to:
            return_to = self.return_to
            if '?' not in return_to:
                return_to += '?openid_return='+session
            else:
                return_to += '&openid_return='+session
        else:
            return_to = req.path_url+'?openid_return='+session
        redirect = openid2rp.request_authentication(
            services, op_endpoint, assoc_handle, return_to, 
            claimed=claimed_id, op_local=op_local)

        start_response('303 Go to OpenID provider', [('Location', redirect)])
        return []

    def returned(self, req, start_response):
        session = req.params.get('openid_return')
        dump = self.store.get_login(session)
        if not dump:
            req.environ['openid2rp.error'] = 'login session not found'
            return self.app(req.environ, start_response)
        claimed_id, assoc_handle = cPickle.loads(dump)
        self.store.end_login(session)
        
        qs = req.environ.get('QUERY_STRING')
        # XXX error handling
        assoc = self.store.get_association(assoc_handle)
        assoc_handle, mac_key = cPickle.loads(assoc)
        try:
            signed = openid2rp.authenticate({'assoc_handle':assoc_handle, 'mac_key':mac_key}, qs)
        except Exception, e:
            return self.error(req.environ, start_response, str(e))

        # Check for replay attacks
        nonce = req.params['openid.response_nonce']
        utc = calendar.timegm(openid2rp.parse_nonce(nonce).utctimetuple())
        if time.time()+self.store.nonce_lifetime < utc or self.store.has_nonce(nonce):
            return self.error(req.environ, start_response, 'replay attack detected')
        self.store.add_nonce(nonce)

        req.environ['openid2rp.identifier'] = claimed_id
        namespaces = openid2rp.get_namespaces(qs)
        req.environ['openid2rp.ax'] = openid2rp.get_ax(qs, namespaces, signed)
        req.environ['openid2rp.sreg'] = openid2rp.get_sreg(qs, signed)
        return self.app(req.environ, start_response)

    def error(self, environ, start_response, msg):
        environ['openid2rp.error'] = msg
        return self.app(environ, start_response)
