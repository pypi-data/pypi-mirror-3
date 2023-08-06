from oosapy import OAuthAuthentication

# keys
CONSUMER_KEY = 'd53da6f7bfdeafdfb32a7677c5cc9c22'
CONSUMER_SECRET = 'd44ef815b6560e3140e0906218059122'

# user authorization process
auth_handler = OAuthAuthentication(CONSUMER_KEY, CONSUMER_SECRET)
auth_url = auth_handler.get_authorization_url(True)
print 'Please authorize: ' + auth_url
verifier = raw_input('Verifier: ').strip()
auth_handler.get_access_token(verifier)
print "ACCESS_TOKEN = '%s'" % auth_handler.access_token.key
print "TOKEN_SECRET = '%s'" % auth_handler.access_token.secret
