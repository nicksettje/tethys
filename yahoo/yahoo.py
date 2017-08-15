import os
import sys
from time import sleep
from yahoo_oauth import OAuth2


oauth = OAuth2(None, None, from_file='oauth2.json')
#for indx in xrange(1,100000):
for indx in xrange(1,100000):
    if not oauth.token_is_valid():
        oauth.refresh_access_token()
    response = oauth.session.get('https://fantasysports.yahooapis.com/fantasy/v2/league/nfl.l.871189/players;player_keys=nfl.p.%s' % str(indx))
    if str(response.status_code) == '200':
        data_file = './data/%s' % str(indx)
        with open(data_file, 'w') as fp:
            print 'writing %s' % data_file 
            fp.write(str(response._content))
    else:
        print 'no player at index: %s' % str(indx)
    sleep(1)
