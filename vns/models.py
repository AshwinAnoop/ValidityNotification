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
