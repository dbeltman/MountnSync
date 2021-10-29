#!/bin/bash

owner=dockerdaan
image=mountnsync
docker build -t $owner/$image:dev -f Dockerfile .
docker run -v /var/run/docker.sock:/var/run/docker.sock $owner/$image:dev
