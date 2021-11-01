#!/bin/bash
owner=dockerdaan
image=mountnsync

backuppath=$1
containername=$2

docker build -t $owner/$image:dev -f Dockerfile .
docker run -v /var/run/docker.sock:/var/run/docker.sock $owner/$image:dev --archive --backup all --destination $backuppath $containername

