#!/bin/bash

docker build -t mi-app:test .
docker run -d --name mi-app-test -p 5000:5000 mi-app:test
sleep 5
curl -f http://localhost:5000/health && echo "✅ Health OK"
curl -f http://localhost:5000/ && echo "✅ App OK"
docker stop mi-app-test && docker rm mi-app-test
