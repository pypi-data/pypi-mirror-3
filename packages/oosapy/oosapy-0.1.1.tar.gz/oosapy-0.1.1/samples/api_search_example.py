from oosapy import AnonymousAuthentication, API

# keys
CONSUMER_KEY = 'd53da6f7bfdeafdfb32a7677c5cc9c22'

# initialization
oauth = AnonymousAuthentication(CONSUMER_KEY)
api = API(oauth)

# parameters
parameters = {"category": "restaurantes", 
              "as": "/es/castellon"}

# search and iteration
results = api.search(parameters)
for restaurant in results[:5]:
    print restaurant.name, restaurant.link
