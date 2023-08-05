# Demo WSGI application using the openid2rp middleware.
import cgi

# This is the actual application. It displays a login box,
# and displays information about the user when login completes.
def application(environ, start_response):
    if 'openid2rp.error' in environ:
        start_response('401 Permission Denied', [('Content-type','text/plain')])
        return ['Something went wrong: '+environ['openid2rp.error']]
    if 'openid2rp.identifier' not in environ:
        # Display login box
        start_response('200 Ok', [('Content-type','text/html')])
        notice = environ.get('openid2rp.notice', '')
        if notice:
            notice = '<em>%s</em><br/>' % notice
        google = '/?openid_identifier=%s' % cgi.escape('https://www.google.com/accounts/o8/id')
        return ['<html><head><title>Login</title></head>'
                '<body>', notice, 'Login with OpenID:'
                '<form method="POST">'
                '<input name="openid_identifier" size="60"/>'
                '</form></body>',
                'Alternatively, log in directly with <a href="', google, '">Google</a>.',
                '</html>']
    # Display authentication results
    start_response('200 Ok', [('Content-type', 'text/html; charset=utf-8')])
    print environ['openid2rp.sreg'].items()
    return (['<html><head><title>Hello ',
             environ['openid2rp.identifier'].encode('utf-8'),
             '</title></head><body>'
             'We know the following information about you:<ul>']+
            ['<li>%s %s</li>' % (k, v) for k,v in environ['openid2rp.ax'].items()]+
            ['<li>%s %s</li>' % (k, v) for k,v in environ['openid2rp.sreg'].items()]+
            ['</ul></body></html>'])

# Wrap the application with the openid2rp middleware
# Web frameworks may offer to perform this wrapping by means of configuration,
# instead of code
from openid2rp.wsgi import Openid2Middleware
application = Openid2Middleware(application)

# Put this into a web container
# We use wsgiref here to keep the dependencies of this package low
from wsgiref.simple_server import make_server
server = make_server('', 6543, application)
print 'Running on http://localhost:6543/'
server.serve_forever()
