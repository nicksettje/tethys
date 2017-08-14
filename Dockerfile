FROM python:2.7
RUN git config --global user.email "nicksettje@gmail.com" &&\
    git config --global user.name "nicksettje"
WORKDIR /tethys
