---
layout: post
---
We will use the [Yahoo Fantasy Sports API](https://developer.yahoo.com/fantasysports/) to retrieve a list of all of the players available to draft. This API is somewhat outdated and undocumented, so we will use a few hacks to get the data we need.

## Issues with the Yahoo Fantasy Sports API
This API is [notoriously hard to work with](https://www.reddit.com/r/fantasyfootball/comments/54m9xx/yahoo_fantasy_api_anybody_use_this/). To begin with, Yahoo uses three-legged authentication for API calls, so authorization is complicated from the start. Moreover, the [official documentation](https://developer.yahoo.com/fantasysports/guide/)seems to have ended in 2012, but the API still responds to calls in 2017. Many of these calls are therefore undocumented. For example, [this API call](https://developer.yahoo.com/yql/console/?_uiFocus=fantasysports&q=select%20*%20from%20fantasysports.games%20where%20game_key%3D%22238%22#h=select+*+from+fantasysports.games+where+game_key%3D%22371%22) returns valid information but appears nowhere in the documentation. To add to this confusion, the API exposes two different methods to access the same data. One method uses Yahoo Query Language (YQL), which is Yahoo's proprietary SQL-like API language. [Other users have covered using the YQL API to access fantasy football data](http://tech.thejoestory.com/2014/12/yahoo-fantasy-football-api-using-python.html). The second method uses a REST API. We will use this method because it is somewhat cleaner and less verbose than the YQL method, though we will see that it still has some ...interesting... features.
 
# Getting a Yahoo OAuth API Key
Read instructions [here]

Register new application [here](https://developer.yahoo.com/apps/create/)
