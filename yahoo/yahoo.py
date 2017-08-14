import os
from time import sleep
from yahoo_oauth import OAuth2
#oauth = OAuth2(consumer_key=os.environ['YAHOO_CLIENT_ID'], consumer_secret=os.environ['YAHOO_CLIENT_SECRET'])
oauth = OAuth2(None, None, from_file='oauth2.json')
for indx in xrange(1,100):
    if not oauth.token_is_valid():
        oauth.refresh_access_token()
    response = oauth.session.get('https://fantasysports.yahooapis.com/fantasy/v2/league/nfl.l.871189/players;player_keys=nfl.p.%s' % str(indx))
    sleep(5)
    print response._content
    print response.status_code
