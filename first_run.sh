#!/bin/bash

echo "run containers"
docker-compose up -d --build

echo "run makemigrations"
docker-compose exec web python3 manage.py makemigrations
sleep 5
echo "run migrate"
docker-compose exec web python3 manage.py migrate

echo "load fixtures"
docker-compose exec web python manage.py loaddata users/fixtures/roles.json
docker-compose exec web python manage.py loaddata reports/fixtures/visibility.json
docker-compose exec web python manage.py loaddata tasks/fixtures/task_types.json

echo "start work"
docker-compose up