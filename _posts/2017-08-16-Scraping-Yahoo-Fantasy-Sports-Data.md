---
layout: post
---
With our Docker Machine set up, we can start gathering data for our roster. We will use the [Yahoo Fantasy Sports API](https://developer.yahoo.com/fantasysports/) to retrieve a list of all of the players available to draft. This API is somewhat outdated and undocumented, so we will use a few hacks to get the data we need.

![Yahoo Cow](/tethys/assets/yahoo-cow-small.jpg "Yahoo Cow")

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

### Build and Run a Yahoo Scraping Docker Container
Throughout this experiment, we will use Docker Compose to set up separate environments for gathering, analyzing, and visualizing data. To start, we need to get some data. In order to begin scraping data from the Yahoo API, we will create a Docker Compose container.

#### Setting the Roadmap: Docker Compose Configuration
---
Start by creating the Docker Compose configuration in the file `/home/ubuntu/tethys/docker-compose.yml`. This file will give us a roadmap for how to set up the Yahoo scraping code.
```yaml
# docker-compose.yml
version: '2'
services:
    yahoo:
        build: ./yahoo
        environment:
        - YAHOO_CLIENT_ID=$YAHOO_CLIENT_ID
        - YAHOO_CLIENT_SECRET=$YAHOO_CLIENT_SECRET
        volumes:
        - nfl_data:/data
        - "./yahoo:/yahoo"
        command: python -u yahoo.py
volumes:
    nfl_data: {}
``` 
Let's walk through this configuration file to understand what it means.
```
version: '2'
```
just means that we are using the `docker-compose.yml` version 2 syntax. We could also use [version 3 syntax](https://docs.docker.com/compose/compose-file/), but we'll stick to version 2 for now.
```
services:
```
defines all of the named services that Tethys will use. For the time being, we define a single service called `yahoo`.
```
   yahoo:
        build: ./yahoo
        environment:
        - YAHOO_CLIENT_ID=$YAHOO_CLIENT_ID
        - YAHOO_CLIENT_SECRET=$YAHOO_CLIENT_SECRET
        volumes:
        - nfl_data:/data
        - "./yahoo:/yahoo"
        command: python -u yahoo.py
```
is the meat and potatoes block of this configuration. 

Here we define the `yahoo` service. To begin, this service tries to build a Docker image using files found in the `./yahoo` folder, which should be the `/home/ubuntu/tethys/yahoo` folder on our AWS host. What does it mean to build a Docker image? In simple terms, Docker Compose will look in the `./yahoo` folder for a file called `Dockerfile` that defines build instructions for the image. We will cover how to structure this file shortly. 

Next, the `yahoo` service defines two environment variables. The `environment` lines just mean that the `yahoo` service should start running with the environment variables `YAHOO_CLIENT_ID` and `YAHOO_CLIENT_SECRET`. We set these variables equal to the variables of the same name on the host. We denote host variables using a `$`. These are the variables you added to your `.bashrc` before.

Next, we define shared volumes. [Docker volumes](https://docs.docker.com/engine/admin/volumes/volumes/) have confused a number of people in the past. In simple terms, these are just persistent containers for data, files, code, or any other information. You make a persistent volume so you can share it among your host and your various containers running services. In our case, we share the folder `./yahoo` on our host machine (which is really `/home/ubuntu/tethys/yahoo`) with our `yahoo` service. Within our `yahoo` service, the shared volume can be found at `/yahoo`. We will see why this is important when we structure the `yahoo` service `Dockerfile` shortly. Additionally, we link our named volume `nfl_data` to the folder `/data` inside of the `yahoo` service. We store all of our data in the `/data` folder in the `yahoo` service and then use the `nfl_data` named volume to pass that data to the containers we make in the future.

Lastly, the `yahoo` service runs the command `python -u yahoo.py`. This means that as soon as the service starts, it tries to run a Python script called `yahoo.py`. The `-u` flag means that Python runs in [unbuffered mode](https://docs.python.org/2/using/cmdline.html). For our purposes, this means that Python will write all information to `stdout` as soon as possible without internal buffering, so we see the data almost as soon as it is received from the Yahoo API.

```
volumes:
    nfl_data: {}
```
This block creates a named data volume called `nfl_data`. We will use this volume to pass data around between the different containers we use throughout our data pipeline. We will pipe our first data into the `nfl_data` volume using the `yahoo` service.

This `docker-compose.yml` is just our roadmap for setting up our project directories, build scripts, and scraping code. Let's see how to follow this roadmap to a working Yahoo scraping service.


#### Following the Roadmap: Dockerfile and Yahoo Scraping Script
---
Our `docker-compose.yml` roadmap defines a `yahoo` service with the following requirements:

- `./yahoo` directory
- `./yahoo/yahoo.py` script
- Build instructions somewhere in `./yahoo`. In our case, this will be `./yahoo/Dockerfile`

Let's follow the roadmap. First, create the `./yahoo` directory.
```
#!/bin/bash
mkdir -p /home/ubuntu/tethys/yahoo
```
Now we need to decide whether to write `./yahoo/yahoo.py`  or `./yahoo/Dockerfile` first. In this case, I would recommend writing the Python script first. This is because the script will define the requirements of our Docker image, so the `Dockerfile` will rely heavily on the contents of the Python script. We will soon see why this is the case.

Let's start with the Yahoo scraping script. This script needs to do to the following:

- Authenticate the Yahoo API call.
- Make the API call.
- Handle the API response. If the API does not return relevant data, log the error and ignore. If the API does return data, save it to a file for the time being.

We'll figure out authentication first. We already have Yahoo API keys, but this only allows us to request a token from Yahoo that we will use as further proof of authorization. In order to get the access token, I wrote a small python script called `token.py` to perform the first handshake and receive the access token. This script uses the [yahoo-oauth](https://github.com/josuebrunel/yahoo-oauth/tree/master/yahoo_oauth) library.

```python
#!/usr/local/bin/python
# token.py
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
    with open('./auth/oauth2.json', 'w') as f:
        f.write(json.dumps(secrets))

if __name__ == '__main__':
    one_time_auth()
```

This script sends our Yahoo API keys to the API, then receives a prompt asking the user to copy and paste a URL into a browser, click `Agree`, and then copy and paste the verifier code back into the terminal. Once the user hits enter to submit the verifier, the script writes the verifier and the API keys to a file called `./yahoo/auth/oauth2.json`. This JSON file now contains valid credentials for accessing the API. We should never need to run the `token.py` script again as long as we have the `oauth2.json` file. This covers the authentication step.

<center>
<br/>
<img align="center" src="/tethys/assets/yahoo-fantasy-agree-small.jpg" alt="Yahoo Agree">
<br/>Yahoo API Access Agreement Dialogue
<br/>
<br/>
<img align="center" src="/tethys/assets/yahoo-verifier-small.jpg" alt="Yahoo Verifier">
<br/>Yahoo API Access Verifier Screen
<br/>
</center>

In order to handle the API call and the subsequent handling of data, we will now look at the `yahoo.py` script that our `yahoo` Docker Compose service will run.

```python
#!/usr/local/bin/python
# yahoo.py
import os
import sys
from time import sleep
from yahoo_oauth import OAuth2

# Unique identifier for your Yahoo fantasy league
LEAGUE_ID='YOUR LEAGUE ID GOES HERE'

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

 # Scrapes Yahoo Fantasy Sports API using (polite) brute force 
def scrape():
    # Check that data dir exists, otherwise make it
    if not os.path.isdir('/data/yahoo/raw'):
        os.makedirs('/data/yahoo/raw')
    # Perform initial authentication
    oauth = OAuth2(None, None, from_file='./auth/oauth2.json')
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
```

There is a lot to digest in this script, so let's look at it piece by piece. 

To start, you need to find your Yahoo Fantasy Sports league ID. The easiest way to do this is to log into your Yahoo Fantasy Sports account and click on the `League` menu and navigate the the `Overview` tab. You should then be on a website with a URL of the form `https://football.fantasysports.yahoo.com/f1/LEAGUEID` where `LEAGUEID` will be the numeric ID of your specific league.

Next, we will cover the `scrape` function.

This function performs initial OAuth authorization from the `./auth/oauth2.json` file we wrote using the `token.py` script.

After authorization, we loop over unique player IDs, calling the player endpoint for our league on the Yahoo API. We use the player endpoint for our league in order only to find players that we can draft for our specific league. In general, the API endpoint for players in a league is of the form `https://fantasysports.yahooapis.com/fantasy/v2/league/nfl.l.$LEAGUE_ID/players;player_keys=nfl.p.$PLAYER_ID` where `$LEAGUE_ID` is the league ID we found before and `$PLAYER_ID` is the numeric identifier for active, draftable players. However, there is a major catch here. As far as I have been able to tell, Yahoo does not publish a single list of all of the player IDs that correspond to draftable players. You could go to the `Player List` on the website for your league, but this gives you a shortlist that you have to refresh by hand. You can find the range of numbers used in player IDs by looking at pages for individual players. For example, [Jordan Howard](https://sports.yahoo.com/nfl/players/29384/) has player ID `29384` because his player page has the URL `https://sports.yahoo.com/nfl/players/29384/`. After some poking around on this list, you'll notice that the highest player IDs are somewhere in the thirty-thousands. This leaves us with one realistic option: **brute force**. 

In order to brute force the API calls, we loop from `1` to `100,000` just to be sure that we scrape all relevant information. After each call, we wait `0.5` seconds, so we make `2` API calls per second. This means that we should make roughly `7,200` calls per hour. This is well within [Yahoo API rate limits](https://developer.yahoo.com/yql/guide/usage_info_limits.html).

After each API call within the loop, we need to check the HTTP response and decide how to handle any relevant data. We achieve all of this using the `check_status` function. This function takes an HTTP response, an oauth object, and a player ID as arguments. If the API call succeeded, then we write the HTTP response content to a file called `/data/yahoo/raw/$PLAYERID` where `$PLAYER_ID` is the player ID for that player. If the API call returned an authorization error, then we re-authorize and issue the same API call again. If the API call returned any other error, we log it and move on. In the end, we return the latest oauth object for use in subsequent calls. 

Notice that logging here all happens through `print` statements in Python as opposed to complicated `logging` objects and streams. We can use `print` because we will rely on Docker for all of our logging.

At this point, we have all our Python scripts set up, so all this is left is to specify how to build the environment in which our `yahoo` service will run. This means that we need to write the `yahoo` service `Dockerfile`. This `Dockerfile` is relatively simple.
```
 # /home/ubuntu/tethys/yahoo/Dockerfile
 # Use the Python 2.7.13 base image
FROM python:2.7
 # Install yahoo_auth using pip
RUN pip install yahoo_oauth
 # When the yahoo service starts, cd to /yahoo before running any commands
WORKDIR /yahoo
```

This `Dockerfile` tells Docker to download the [Debian-based Python 2.7 Docker image](https://hub.docker.com/_/python/) from the [Docker Hub](https://hub.docker.com/). Next, we install our one Python lbirary requirement, which is yahoo_oauth. Finally, we make sure that all commands run from the `/yahoo` directory.

Now that we have `token.py`, `yahoo.py`, and our `Dockerfile`, we can build and run our `yahoo` service to scrape the Yahoo API

#### Scraping the Yahoo API
First, we need to build the `yahoo` service Docker image. We can do this in one line.
```bash
#!/bin/bash
cd /home/ubuntu/tethys && sudo docker-compose build yahoo
```

The first build may take some time because Docker needs to download and install the Python image. After the first build, subsequent builds will be much faster because Docker caches images.

Next, we need to run the `token.py` script to generate our one-time access token for the Yahoo API.

```bash
#!/bin/bash
cd /home/ubuntu/tethys && sudo docker-compose run yahoo python token.py
```

Copy and paste the `Authorization URL` into a browser. Follow the steps, then copy and paste the `verifier` into the terminal and hit enter.

Finally, run the Yahoo scraping script.
```bash
#!/bin/bash
cd /home/ubuntu/tethys && sudo docker-compose up -d yahoo
```

You can monitor the progress of the scraping script by following the Docker logs for the `yahoo` service.
```bash
#!/bin/bash
cd /home/ubuntu/tethys && sudo docker logs -f tethys_yahoo_1
```

Notice that our running service is actually called `tethys_yahoo_1`. When you start a service with Docker Compose, Docker prepends the directory of the `docker-compose.yml` file and then appends an index corresponding to how many instances of that service are currently running.

You can see the scraped data files by looking in the `/home/ubuntu/tethys/yahoo/data/` folder.

Now, all that's left is to wait for the scrape run to finish. Since we are scraping `100,000` player IDs at a rate of `7,200` player IDs per hour, the run should take roughly `14` hours.

Once the scrape run finishes, we will see how to mine this data for relevant player information. We will then use this information to query another API of historical game statistics to start building our numerical data sets for model training.
