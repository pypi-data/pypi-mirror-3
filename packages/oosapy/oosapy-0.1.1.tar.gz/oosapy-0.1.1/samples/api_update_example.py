from oosapy import OAuthAuthentication, API

# keys
CONSUMER_KEY = 'd53da6f7bfdeafdfb32a7677c5cc9c22'
CONSUMER_SECRET = 'd44ef815b6560e3140e0906218059122'

ACCESS_TOKEN = 'a90a9573c4b472dd89795f143a0b7772'
TOKEN_SECRET = '45c3598868bf1b616a5607c2c1a8f5ba'

# initialization
oauth = OAuthAuthentication(CONSUMER_KEY, CONSUMER_SECRET,
                            ACCESS_TOKEN, TOKEN_SECRET)
api = API(oauth)

# change my nick
me = api.get_me()
me.nick = 'new nick'
me.update()
