#Some Sample code for how Trove Client APIs work

from troveclient import TroveAPI

# You need a consumer.  Make one in the db. Consumers have call back URLs, which are not overridable (a-la Twitter and Fb)  
c = { 
	client_id: 'some_key_here',
	secret: 'sssh, it\'s a secret!',
	redirect_uri: 'http://redirecturl.dev/callback'
}
# Initialize the TroveAPI with the consumer's key and secret
api = TroveAPI(client_id, secret, redirect_uri)

url = api.get_authenticate_url() 
print url
raw_input()

# Returns back the URL to redirect the user  (Looks like 'http://brooklyn.vlku.com:8000/multi/login?next=/oauth/2authorize/%3Foauth_token%3DdtKaXn5JXRWNndTa')

# callback URL includes a "code" that is passed in via the code parameter.  We use that to get an access_token.

at = api.get_access_token(code)  
# This returns back the access_token (at) as an OAuthToken.  You want to save this somewhere for reuse later
# access_token also conveniently makes this the access_token for the instantiated API

# so you can call this easily right away with no setup
results = api.get_photos()


# but if you have to initialize a fresh TroveAPI (say for another hit with the token from the DB:)
api = TroveAPI(c.key, c.secret, ['photo'], access_token=at)
results = api.get_photos()

