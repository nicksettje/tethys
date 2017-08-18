import os
import json
from yahoo_oauth import OAuth2

def one_time_auth():
    # Check that auth dir exists, otherwise make it
    if not os.path.isdir('./auth'):
        os.makedirs('./auth')
    # Send API keys to Yahoo to request authorization token 
    oauth = OAuth2(os.environ['YAHOO_CLIENT_ID'], os.environ['YAHOO_CLIENT_SECRET'])
    # After copy-paste into browser, get verifier, and copy-paste into terminal
    # Yahoo authorization token will be stored in a file called 'secrets.json'.
    with open('./auth/secrets.json', 'r') as f:
        secrets = json.load(f)
    # Add Yahoo API keys to authorization key dictionary
    secrets['consumer_key'] = os.environ['YAHOO_CLIENT_ID']
    secrets['consumer_secret'] = os.environ['YAHOO_CLIENT_SECRET']
    # Write API keys and authorization token to file
    with open('./auth/oauth2_.json', 'w') as f:
        f.write(json.dumps(secrets))

if __name__ == '__main__':
    one_time_auth()
