import os
import sys
from time import sleep
from yahoo_oauth import OAuth2

# Unique identifier for your Yahoo fantasy league
LEAGUE_ID='871189'

# Checks API call response code to determine whether to
# route data, ignore error, or re-authenticate
def check_status(response, oauth, indx):
    # HTTP response code of the request
    status = response.status_code
    print status
    # If response succeeds, write to file
    if str(status) == '200':
        data_file = '/data/yahoo/raw/%s' % str(indx)
        with open(data_file, 'w') as fp:
            print 'writing %s' % data_file 
            fp.write(str(response._content))
    # If no longer authenticated, re-authenticate
    # then make API call again
    elif str(status) == '401':
        oauth = OAuth2(None, None, from_file='oauth2.json')
        response = oauth.session.get('https://fantasysports.yahooapis.com/fantasy/v2/league/nfl.l.%s/players;player_keys=nfl.p.%s' % (LEAGUE_ID, str(indx))
        check_status(response, oauth, indx)
    # If any other errors occur, log and ignore
    else:
        print response.content
        print 'no player at index: %s' % str(indx)
    # Return authorization object
    # If no reauthorization occurred, this is the same oauth as input
    # If reauthorization occurred, this is a new, valid oauth
    return oauth

# Scrapes Yahoo Fantasy Sports API using brute force 
def scrape():
    # Check that data dir exists, otherwise make it
    if not os.path.isdir('/data/yahoo/raw'):
        os.makedirs('/data/yahoo/raw')
    # Perform initial authentication
    oauth = OAuth2(None, None, from_file='oauth2.json')
    # Loop over a large range of player IDs
    for indx in xrange(1,100000):
        # Make the API call for the player ID for your league
        response = oauth.session.get('https://fantasysports.yahooapis.com/fantasy/v2/league/nfl.l.%s/players;player_keys=nfl.p.%s' % (LEAGUE_ID, str(indx))
        # Check the HTTP response and determine whether to re-authenticate
        oauth = check_status(response, oauth, indx)
        # Wait between calls to stay within rate limit
        sleep(0.5)

if __name__ == '__main__':
    scrape()
