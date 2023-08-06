"""short program to make authorized requests to the API

python command_line_test.py url [method] [body] [content-type]
"""

import sys, os

from oosapy import OAuthAuthentication

# keys
CONSUMER_KEY = 'd53da6f7bfdeafdfb32a7677c5cc9c22'
CONSUMER_SECRET = 'd44ef815b6560e3140e0906218059122'

ACCESS_TOKEN = 'a90a9573c4b472dd89795f143a0b7772'
TOKEN_SECRET = '45c3598868bf1b616a5607c2c1a8f5ba'

# defaults
url = "http://11870.com/api/v2/service"
method = "GET"
body = ""
content_type = "application/atom+xml"

# "parsing"
params = len(sys.argv)
if params == 1:
    print "python command_line_test.py url [method] [body] [content-type]"
    sys.exit(1)

url = sys.argv[1]
if params > 2:
    method = sys.argv[2]
    if params > 3:
        if os.path.isfile(sys.argv[3]):
            body = open(sys.argv[3]).read()
        else:
            body = sys.argv[3]
        if params > 4:
            content_type = sys.argv[4]

# execution
oauth = OAuthAuthentication(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, TOKEN_SECRET)
resp = oauth.get_response(url, method, body, headers={'Content-Type': content_type})
print resp[1]
