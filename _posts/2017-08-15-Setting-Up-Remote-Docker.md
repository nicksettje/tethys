---
layout: post
---
## Running Docker on AWS
Before we get started gathering data for our roster, we need to set up a machine to host our data and run our calculations. I'll walk you through how to set up an AWS EC2 instance on the Free Tier using Docker Machine.

![Whale Backflip](/tethys/assets/whale-backflip-small.jpg "Whale Backflip")

## Why AWS?
We could host everything on a local Docker Machine. This saves us the extra work of maintaining and administering a remote server. However, a remote server will have several benefits.
### Non-Host IPs
We will be using this machine to gather data from various open APIs on the web. Each API call will return a small amount of data, so we will need to make many API calls in a short period of time. Using a remote host prevents your host IP from being banned and it keeps your Internet Service Provider happy.
### Uptime
Some of the data scraping scripts could potentially run for long periods of time. We are probably better off running these processes on a dedicated server rather than trying to find the time on a local machine (and trying to remember not to close a laptop).

## Why Docker?
Tethys uses Docker, Docker Compose, and Docker Machine to make sure that all system builds remain consistent and repeatable. In particular, Docker Compose makes it extremely easy to start and stop connected services in a short period of time while Docker Machine ensures that all related services stay isolated from other system processes. Together with AWS, it is easy to start, stop, and maintain running processes.

## Setting Up the Docker Environment on AWS
### Start an AWS EC2 Instance
See the [official AWS documentation for starting AWS EC2 instances](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/LaunchingAndUsingInstances.html). For the purposes of this experiment, I am using a t2.micro instance (1 virtual CPU, 1 GB memory).
### Create a New AWS User
See the [official AWS documentation for creating new users](http://docs.aws.amazon.com/IAM/latest/UserGuide/getting-started_create-admin-group.html). I created a new user called `tethys`. I also created a new access group called `ec2+s3` with the permissions `AmazonEC2FullAccess` and `AmazonS3FullAccess`. I added `tethys` to the group `ec2+s3`.
### Create a New Docker Machine with the amazonec2 Driver
See the [official Docker instructions for creating a Docker Machine with AWS](https://docs.docker.com/machine/examples/aws/#step-2-use-machine-to-create-the-instance).
I opted for the route where I store the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` as local variables on the host machine I use to connect to AWS. I am using the AWS API keys for the user `tethys` I created earlier. Make sure your follow the Docker link to find the VPC ID for the EC2 instance your just started. Then you can create the new remote Docker Machine:
```
#!/bin/bash
docker-machine create --driver amazonec2 --amazon-vpc-id $MY_AWS_VPC_ID aws-tethys
```
## Install Docker Compose on the AWS Docker Machine
See the [official Docker documentation for installing Docker Compose](https://docs.docker.com/compose/install/). Also, see the [official Digital Ocean documentation for installing Docker Compose](https://www.digitalocean.com/community/tutorials/how-to-install-docker-compose-on-ubuntu-16-04).
First, user Docker Machine to log into your AWS EC2 instance.
```
#!/bin/bash
docker-machine ssh aws-tethys
```
You are now logged into the remote Docker instance. Now, install Docker Compose on the remote machine.
```
#!/bin/bash
sudo curl -o /usr/local/bin/docker-compose -L "https://github.com/docker/compose/releases/download/1.15.0/docker-compose-$(uname -s)-$(uname -m)" && \
sudo chmod +x /usr/local/bin/docker-compose
```
Check the Docker Compose version to make sure that Docker Compose installed correctly.
```
#!/bin/bash
docker-compose -v
```
## Make a Project Directory
Last but not least, make a `tethys` project directory on the AWS host.
```
#!/bin/bash
mkdir -p /home/ubuntu/tethys
```

## Optional: Add Bash Aliases
The default AWS user for an Ubuntu EC2 instance is `ubuntu`, but only the `root` user can run Docker and Docker Compose commands. In order to make it more convenient to run Docker-related commands, consider adding the following lines to the top of your `/home/ubuntu/.bashrc` file.
```bash
#!/bin/bash
alias d='sudo docker'
alias di='sudo docker images'
alias de='sudo docker exec -i -t'
alias dc='sudo -E docker-compose'
alias dps='sudo docker ps'
```
These lines will add bash command line aliases for common Docker commands. Remember to source your `.bashrc` to activate them.
```
#!/bin/bash
. ~/.bashrc
```

That's it. Our Docker Machine is up and running, equipped with Docker Compose.
