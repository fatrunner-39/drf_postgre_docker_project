# drf_postgre_docker_project

# DESCRIPTION
Backend for running diary application. Include:
  - user's registration
  - creating, editing and removing running tasks by coaches
  - creating, editing and removing running reports manual or by loading GPX file 
  - view run reports and tasks

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

# REQUESTS EXAMPLES

1. Registration. URL http://127.0.0.1:8000/api/v1/registration/
![image](https://user-images.githubusercontent.com/72695509/208469936-cd0d19d6-f06f-4bbf-b9c4-463972234b7f.png)



2. Get token. URL http://127.0.0.1:8000/api/v1/token/ 
![image](https://user-images.githubusercontent.com/72695509/208469384-f5b493fc-17ec-4eae-bf70-d02b309af22b.png)


