# drf_postgre_docker_project

# SETUP 

1. git clone https://github.com/fatrunner-39/drf_postgres_docker_project.git
2. cd django_postgres_docker_project
3. source env/bin/activate (for windows env\Scripts\activate) 
4. sudo sh ./first_run.sh
5. sudo docker-compose exec web python manage.py loaddata reports/fixtures/visibility.json
6. sudo docker-compose exec web python manage.py loaddata tasks/fixtures/task_types.json
7. sudo docker-compose exec web python manage.py loaddata users/fixtures/roles.json
8. sudo docker-compose exec web python manage.py createsuperuser

# USING
sudo sh ./run.sh
