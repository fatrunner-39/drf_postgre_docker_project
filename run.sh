#!/bin/bash


echo "run makemigrations"
python3 manage.py makemigrations
sleep 5
echo "run migrate"
web python3 manage.py migrate

echo "start work"
python manage.py runserver 0.0.0.0:8000
