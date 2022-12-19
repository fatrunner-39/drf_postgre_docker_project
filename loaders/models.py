from django.db import models
# from reports.models import Report


class FileLoader(models.Model):
    file = models.FileField(upload_to='tracks/%Y_%m_%d/')
