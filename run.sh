#!/bin/bash

echo "run containers"
docker-compose up -d --build

echo "run makemigrations"
docker-compose exec web python3 manage.py makemigrations
sleep 5
echo "run migrate"
docker-compose exec web python3 manage.py migrate

echo "start work"
docker-compose up
