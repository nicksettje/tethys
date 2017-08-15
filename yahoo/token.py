import os
from yahoo_oauth import OAuth2

oauth = OAuth2(os.environ['YAHOO_CLIENT_ID'], os.environ['YAHOO_CLIENT_SECRET'])
