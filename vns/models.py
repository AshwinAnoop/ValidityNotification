from django.db import models

# Create your models here.

class Document(models.Model):
    user_id = models.IntegerField()
    category = models.CharField(max_length = 50)
    sub_category = models.CharField(max_length = 50)
    doc_type = models.CharField(max_length = 50)
    start_date = models.DateField()
    end_date = models.DateField()
    last_day = models.BooleanField(default = True)
    last_week = models.BooleanField(default = True)
    last_month = models.BooleanField(default = True)
    no_of_files = models.IntegerField(default=0)
    feedback = models.TextField(null=True)

class Notification(models.Model):
    doc_id = models.IntegerField()
    notify_date = models.DateField()
    is_notified = models.BooleanField(default = False)

class Categories(models.Model):
    category = models.CharField(max_length=50)
    sub_category = models.CharField(max_length=50)

class DocType(models.Model):
    document_type = models.CharField(max_length=50)
