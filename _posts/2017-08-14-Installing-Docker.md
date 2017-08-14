---
layout: post
---
## Prerequisites
This tutorial assumes that you are using some flavor of Linux that has access to a bash shell. For those of you on other OSes, I recommend an [AWS EC2 instance on the Free Tier](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html).

## Why Docker?
TetHys uses Docker, Docker Compose, and Docker Machine to make sure that all system builds remain consistent and repeatable. In particular, Docker Compose makes it extremely easy to start and stop connected services in a short period of time while Docker Machine ensures that all related services stay isolated from other system processes.

## How to Install
### Docker
Follow the instructions from the official Docker site: [Install Docker](https://docs.docker.com/engine/installation/)
### Docker Compose
Follow the instructions from the official Docker site: [Install Docker Compose](https://docs.docker.com/compose/install/)
### Docker Machine
Follow the instructions from the official Docker site: [Install Docker Machine](https://docs.docker.com/machine/install-machine)

## Setting Up the Docker Environment
### Create a New Docker Machine
Whenever I start a new project, I usually create a new Docker Machine to make sure that all of my containers and processes remain separate from my other Docker instances and my host.

To create a new Docker Machine:
```
#!/bin/bash
# Creates a Docker Machine with 4GB of memory
docker-machine create --driver virtualbox --virtualbox-memory 4096 tethys 
```

### Connect to the New Docker Machine
To connect, evaluate the bash environment for the new Docker Machine:
```
#!/bin/bash
eval $(dm env tethys)
```
