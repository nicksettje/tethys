---
layout: post
---
With our Docker Machine set up, we can start gathering data for our roster. We will use the [Yahoo Fantasy Sports API](https://developer.yahoo.com/fantasysports/) to retrieve a list of all of the players available to draft. This API is somewhat outdated and undocumented, so we will use a few hacks to get the data we need.

## Issues with the Yahoo Fantasy Sports API
This API is [notoriously hard to work with](https://www.reddit.com/r/fantasyfootball/comments/54m9xx/yahoo_fantasy_api_anybody_use_this/). To begin with, Yahoo uses three-legged authentication for API calls, so authorization is complicated from the start. Moreover, the [official documentation](https://developer.yahoo.com/fantasysports/guide/) seems to have ended in 2012, but the API still responds to calls in 2017. Many of these calls are therefore undocumented. For example, [this API call](https://developer.yahoo.com/yql/console/?_uiFocus=fantasysports&q=select%20*%20from%20fantasysports.games%20where%20game_key%3D%22238%22#h=select+*+from+fantasysports.games+where+game_key%3D%22371%22) returns valid information but appears nowhere in the documentation. To add to this confusion, the API exposes two different methods to access the same data. One method uses Yahoo Query Language (YQL), which is Yahoo's proprietary SQL-like API language. [Other users have covered using the YQL API to access fantasy football data](http://tech.thejoestory.com/2014/12/yahoo-fantasy-football-api-using-python.html). The second method uses a REST API. We will use this method because it is somewhat cleaner and less verbose than the YQL method, though we will see that it still has some ...interesting... features.
 
## Connecting to the Yahoo Fantasy Sports API
### Creating a Yahoo OAuth API Key
Visit the [Yahoo Developer site for registering new applications](https://developer.yahoo.com/apps/create/). Choose the `Installed Application` radio button. You now only need to supply an `Application Name` and `API Permissions`. Check the `Fantasy Sports` box at the bottom of the page. Click `Create App`. Yahoo will now create your app and show you the two API keys you need to access Yahoo API data. One of the keys is the `Client ID` or the `Consumer Key`. The other key is the `Client Secret` or the `Consumer Secret`. 

Save these API keys as bash environment variables on your AWS Docker Machine host.
```
#!/bin/bash
echo "export YAHOO_CLIENT_ID=type-your-client-id-here" >> ~/.bashrc && echo "export YAHOO_CLIENT_SECRET=type-your-client-secret-here" >> ~/.bashrc && . ~/.bashrc
``` 

### Build and Run a Yahoo Docker Container


### Generating a Yahoo Authorization Token
We already have Yahoo API keys, but this only allows us to request a token from Yahoo that we will use as further proof of authorization. In order to get the authorization token, I wrote a small python script to perform the first handshake. This script uses the [yahooo-oauth](https://github.com/josuebrunel/yahoo-oauth/tree/master/yahoo_oauth) library available through pip.
```python
#!/usr/local/bin/python
# token.py
import os
from yahoo_oauth import OAuth2
oauth = OAuth2(os.environ['YAHOO_CLIENT_ID'], os.environ['YAHOO_CLIENT_SECRET'])
```
