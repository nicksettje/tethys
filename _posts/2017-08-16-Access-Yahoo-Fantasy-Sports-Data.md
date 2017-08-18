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
        - "./yahoo:/yahoo"
        command: python -u yahoo.py
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
        - "./yahoo:/yahoo"
        command: python -u yahoo.py
```
is the meat and potatoes block of this configuration. 

Here we define the `yahoo` service. To begin, this service tries to build a Docker image using files found in the `./yahoo` folder, which should be the `/home/ubuntu/tethys/yahoo` folder on our AWS host. What does it mean to build a Docker image? In simple terms, Docker Compose will look in the `./yahoo` folder for a file called `Dockerfile` that defines build instructions for the image. We will cover how to structure this file shortly. 

Next, the `yahoo` service defines two environment variables. The `environment` lines just mean that the `yahoo` service should start running with the environment variables `YAHOO_CLIENT_ID` and `YAHOO_CLIENT_SECRET`. We set these variables equal to the variables of the same name on the host. We denote host variables using a `$`. These are the variables you added to your `.bashrc` before.

Next, we define a shared volume. [Docker volumes](https://docs.docker.com/engine/admin/volumes/volumes/) have confused a number of people in the past. In simple terms, these are just persistent containers for data, files, code, or any other information. You make a persistent volume so you can share it among your host and your various containers running services. In our case, we share the folder `./yahoo` on our host machine (which is really `/home/ubuntu/tethys/yahoo`) with our `yahoo` service. Within our `yahoo` service, the shared volume can be found at `/yahoo`. We will see why this is important when we structure the `yahoo` service `Dockerfile` shortly.

Lastly, the `yahoo` service runs the command `python -u yahoo.py`. This means that as soon as the service starts, it tries to run a Python script called `yahoo.py`. The `-u` flag means that Python runs in [unbuffered mode](https://docs.python.org/2/using/cmdline.html). For our purposes, this means that Python will write all information to `stdout` as soon as possible without internal buffering, so we see the data almost as soon as it is received from the Yahoo API.

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
![Yahoo Agree](/tethys/assets/yahoo-fantasy-agree-small.jpg)
<br/><br/>*Yahoo API Access Agreement Dialogue*

![Yahoo Verifier](/tethys/assets/yahoo-verifier-small.jpg)
<br/><br/>*Yahoo API Access Verifier Screen*
</center>

In order to handle the API call and the subsequent handling of data, we will now look at the `yahoo.py` script that our `yahoo` Docker Compose service will run.
