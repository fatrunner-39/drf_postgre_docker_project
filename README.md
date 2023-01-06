# drf_postgres_docker_project

# DESCRIPTION
Backend for running diary application. Include:
  - user's registration
  - creating, editing and removing running tasks by coaches
  - creating, editing and removing running reports manual or by loading GPX file 
  - view run reports and tasks

# SETUP 

1. git clone https://github.com/fatrunner-39/drf_postgres_docker_project.git
2. cd django_postgres_docker_project
3. source env/bin/activate
4. sudo docker-compose up --build
5. sudo docker-compose exec web python manage.py createsuperuser
6. sudo docker-compose exec web python manage.py loaddata users/fixtures/roles.json
7. sudo docker-compose exec web python manage.py loaddata tasks/fixtures/task_types.json
8. sudo docker-compose exec web python manage.py loaddata reports/fixtures/visibility.json

# DATABASE SCHEMA
![my_diary](https://user-images.githubusercontent.com/72695509/208481292-c14b6174-5e83-45b7-a726-23b33b029575.jpg)

# REQUESTS EXAMPLES

1. Registration. URL http://127.0.0.1:8000/api/v1/registration/
![image](https://user-images.githubusercontent.com/72695509/208469936-cd0d19d6-f06f-4bbf-b9c4-463972234b7f.png)

2. Get token. URL http://127.0.0.1:8000/api/v1/token/ 
![image](https://user-images.githubusercontent.com/72695509/208469384-f5b493fc-17ec-4eae-bf70-d02b309af22b.png)

3. Get running reports for user. URL http://127.0.0.1:8000/api/v1/reports
![image](https://user-images.githubusercontent.com/72695509/208470985-655eb28e-984a-4a78-9ab9-1ea3832958cd.png)
  - for runner
![image](https://user-images.githubusercontent.com/72695509/208471247-174200f0-da32-4da3-9165-fab9d28c82be.png)

4. Create running report by GPX URL http://127.0.0.1:8000/api/v1/loader/tracks/
![image](https://user-images.githubusercontent.com/72695509/208474115-eb9aad68-1049-452f-af13-7fd491087231.png)

5. Create running task URL http://127.0.0.1:8000/api/v1/tasks/
![image](https://user-images.githubusercontent.com/72695509/208475479-f2f20b25-e4ce-4676-9111-95eaecd3fc92.png)

6. Get coaches runner's group. URL http://127.0.0.1:8000/api/v1/groups
![image](https://user-images.githubusercontent.com/72695509/208479809-f5d31095-cff5-4c61-8f2d-ecd661ef357f.png)
