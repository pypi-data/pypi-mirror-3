#!/usr/bin/env python
################ Test Server #################################
import BaseHTTPServer, cgi, socket, collections
from openid2rp import *
from time import time

# supported providers
providers = (
    ('Google', 'http://www.google.com/favicon.ico', 'https://www.google.com/accounts/o8/id'),
    ('Yahoo', 'http://www.yahoo.com/favicon.ico', 'http://yahoo.com/'),
    ('Verisign', 'http://pip.verisignlabs.com/favicon.ico', 'http://pip.verisignlabs.com'),
    ('myOpenID', 'https://www.myopenid.com/favicon.ico', 'https://www.myopenid.com/'),
    ('Launchpad', 'https://login.launchpad.net/favicon.ico', 'https://login.launchpad.net/')
    )
             

# Cache discovered information, for later validation
discovered = {}

# Mapping from OP Endpoint URL to association responses;
# most recent association is last
sessions = collections.defaultdict(list)
# Associations by assoc_handle
associations = {}

class _Expired(Exception):
    'Local exception class to indicate expired sessions.'
    pass

nonces = set()
def nonce_seen(nonce):
    if nonce in nonces:
        return True
    nonces.add(nonce)
    return False

class Handler(BaseHTTPServer.BaseHTTPRequestHandler):

    def write(self, payload, type):
        self.send_response(200)
        self.send_header("Content-type", type)
        self.send_header("Content-length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path == '/':
            return self.root()
        path = self.path
        i = path.rfind('?')
        if i >= 0:
            querystring = path[i+1:]
            query = cgi.parse_qs(querystring)
            path = path[:i]
        else:
            query = {}
        if path == '/':
            if 'provider' in query:
                prov = [p for p in providers if p[0]  == query['provider'][0]]
                if len(prov) != 1:
                    return self.not_found()
                prov = prov[0][2]
                services, url, op_local = discovered[prov] = discover(prov)

                # Get most recent association.  Establish association if it
                # expired, or if none exist
                now = time()
                try:
                    session, expire = sessions[url][-1]
                    if now > expire:
                        raise _Expired
                except (IndexError, _Expired):
                    try:
                        session = associate(services, url)
                    except ValueError, e:
                        return self.error(str(e))
                    sessions[url].append((session, now+int(session['expires_in'])))
                    associations[session['assoc_handle']] = session

                self.send_response(307) # temporary redirect - do not cache
                self.send_header("Location", request_authentication
                                 (services, url, session['assoc_handle'],
                                  self.base_url+"?returned=1"))
                self.end_headers()
                return
            if 'claimed' in query:
                kind, claimed = normalize_uri(query['claimed'][0])
                if kind == 'xri':
                    res = resolve_xri(claimed)
                    if res:
                        # A.5: XRI resolution requires to use canonical ID
                        # Original claimed ID may be preserved for display
                        # purposes
                        claimed = res[0]
                        res = res[1:]
                else:
                    res = discover(claimed)
                if res is None:
                    return self.error('Discovery failed')
                discovered[claimed] = res
                services, url, op_local = res

                # Get most recent association.  Establish association if it
                # expired, or if none exist
                now = time()
                try:
                    session, expire = sessions[url][-1]
                    if now > expire:
                        raise _Expired
                except (IndexError, _Expired):
                    try:
                        session = associate(services, url)
                    except ValueError, e:
                        return self.error(str(e))
                    sessions[url].append((session, now+int(session['expires_in'])))
                    associations[session['assoc_handle']] = session

                self.send_response(307)
                self.send_header("Location", request_authentication
                                 (services, url, session['assoc_handle'],
                                  self.base_url+"?returned=1",
                                  claimed, op_local))
                self.end_headers()
                return                
            if 'returned' in query:
                if 'openid.mode' not in query:
                    return self.rp_discovery()
                try:
                    signed, claimed_id = verify(query, discovered.get,
                                                associations.get, nonce_seen)
                except NotAuthenticated, e:
                    return self.write('Login failed: %s' % e, 'text/plain')
                    signed, = query['openid.signed']
                    signed = signed.split(',')
                payload = "Hello "+claimed_id+"\n"
                ax = get_ax(querystring, get_namespaces(querystring), signed)
                sreg = get_sreg(querystring, signed)
                email = get_email(querystring)
                if email:
                    payload += 'Your email is '+email+"\n"
                else:
                    payload += 'No email address is known\n'
                if 'nickname' in sreg:
                    username = sreg['nickname']
                elif "http://axschema.org/namePerson/first" in ax:
                    username = ax["http://axschema.org/namePerson/first"]
                    if "http://axschema.org/namePerson/last" in ax:
                        username += "." + ax["http://axschema.org/namePerson/last"]
                else:
                    username = None
                if username:
                    payload += 'Your nickname is '+username+'\n'
                else:
                    payload += 'No nickname is known\n'
                if isinstance(payload, unicode):
                    payload = payload.encode('utf-8')
                return self.write(payload, "text/plain")
                
        return self.not_found()

    

    def debug(self, value):
        payload = repr(value)
        if isinstance(payload, unicode):
            payload = payload.encode('utf-8')
        self.write(payload, "text/plain")

    def error(self, text):
        if isinstance(text, unicode):
            text = text.encode('utf-8')
        self.write(text, "text/plain")

    def root(self):
        payload = u"<html><head><title>OpenID login</title></head><body>\n"
        
        for name, icon, provider in providers:
            payload += u"<p><a href='%s?provider=%s'><img src='%s' alt='%s'></a></p>\n" % (
                self.base_url, name, icon, name)
        payload += u"<form>Type your OpenID:<input name='claimed'/><input type='submit'/></form>\n"
        payload += u"</body></html>"
        self.write(payload.encode('utf-8'), "text/html")

    def rp_discovery(self):
        payload = '''<xrds:XRDS  
                xmlns:xrds="xri://$xrds"  
                xmlns="xri://$xrd*($v*2.0)">  
                <XRD>  
                     <Service priority="1">  
                              <Type>http://specs.openid.net/auth/2.0/return_to</Type>  
                              <URI>%s</URI>  
                     </Service>  
                </XRD>  
                </xrds:XRDS>
        ''' % (self.base_url+"/?returned=1")
        self.write(payload, 'application/xrds+xml')

    def not_found(self):
        self.send_response(404)
        self.end_headers()

if hasattr(socket, 'IPV6_V6ONLY'):
    class HTTPServer(BaseHTTPServer.HTTPServer):
        def __init__(self, addr, handler):
            if not addr[0]:
                # use V6 here, set to wildcard below
                self.address_family = socket.AF_INET6
            BaseHTTPServer.HTTPServer.__init__(self, addr, handler)
        def server_bind(self):
            if self.address_family == socket.AF_INET6:
                self.socket.setsockopt(socket.IPPROTO_IPV6,
                                       socket.IPV6_V6ONLY,
                                       False)
            BaseHTTPServer.HTTPServer.server_bind(self)
else:
    HTTPServer = BaseHTTPServer.HTTPServer

        
# OpenID providers often attempt relying-party discovery
# This requires the test server to use a globally valid URL
# If Python cannot correctly determine the base URL, you
# can pass it as command line argument
def test_server():
    import socket, sys
    port = 8000
    if len(sys.argv) > 1:
        import urlparse
        base_url = sys.argv[1]
        netloc = urlparse.urlparse(base_url).netloc
        if ':' in netloc:
            host, port = netloc.split(':')
            port = int(port)
    else:
        base_url = "http://" + socket.getfqdn() + ":8000/"
    print "Listening on", base_url
    Handler.base_url = base_url
    httpd = HTTPServer(('', port), Handler)
    httpd.serve_forever()

if __name__ == '__main__':
    test_server()
