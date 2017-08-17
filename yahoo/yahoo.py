import os
import sys
from time import sleep
from yahoo_oauth import OAuth2

LEAGUE_ID='871189'

def check_status(response, oauth, indx):
    status = response.status_code
    print status
    if str(status) == '200':
        data_file = './data/%s' % str(indx)
        with open(data_file, 'w') as fp:
            print 'writing %s' % data_file 
            fp.write(str(response._content))
    elif str(status) == '401':
        oauth = OAuth2(None, None, from_file='oauth2.json')
        response = oauth.session.get('https://fantasysports.yahooapis.com/fantasy/v2/league/nfl.l.%s/players;player_keys=nfl.p.%s' % (LEAGUE_ID, str(indx))
        check_status(response, oauth, indx)
    else:
        print response.content
        print 'no player at index: %s' % str(indx)
    return oauth

def mine():
    oauth = OAuth2(None, None, from_file='oauth2.json')
    for indx in xrange(1,100000):
        response = oauth.session.get('https://fantasysports.yahooapis.com/fantasy/v2/league/nfl.l.%s/players;player_keys=nfl.p.%s' % (LEAGUE_ID, str(indx))
        oauth = check_status(response, oauth, indx)
        sleep(0.5)

if __name__ == '__main__':
    mine()
