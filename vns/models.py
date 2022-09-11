from django.db import models

# Create your models here.

class Document(models.Model):
    user_id = models.IntegerField()
    doc_name = models.CharField(max_length = 50)
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

    def __str__(self):
        return "{} : {}".format(self.category, self.sub_category)

class DocType(models.Model):
    document_type = models.CharField(max_length=50)

    def __str__(self):
        return "{}".format(self.document_type)

class FileUploads(models.Model):
    docu_id = models.IntegerField()
    filepath = models.CharField(max_length=250) 

class Wallet(models.Model):
    user_id = models.IntegerField()
    amount = models.IntegerField()
    transactdate = models.DateTimeField()

class Advertisement(models.Model):
    user_id = models.IntegerField()
    ad_name = models.CharField(max_length=50)
    ad_title = models.CharField(max_length=50)
    ad_content = models.CharField(max_length=100)
    ad_link = models.CharField(max_length=100)
    ad_type = models.CharField(max_length=50)
    noOfClicks = models.IntegerField(default=0)
    publish_count = models.IntegerField(default=0)
    amount_spend = models.IntegerField(default=0)

class InAppAds(models.Model):
    doc_id = models.IntegerField()
    category = models.CharField(max_length=50)
    sub_category = models.CharField(max_length=50)
    doc_type = models.CharField(max_length=50,null=True)
    ad_id1 = models.IntegerField(default=0)
    ad_id2 = models.IntegerField(default=0)
    ad_id3 = models.IntegerField(default=0)

class NotifyAds(models.Model):
    doc_id = models.IntegerField()
    category = models.CharField(max_length=50)
    sub_category = models.CharField(max_length=50)
    doc_type = models.CharField(max_length=50,null=True)
    ad_id1 = models.IntegerField(default=0)
    ad_id2 = models.IntegerField(default=0)
    ad_id3 = models.IntegerField(default=0)

class WalletBalance(models.Model):
    user_id = models.IntegerField()
    balance = models.IntegerField()
    total_ads = models.IntegerField(default=0)
    total_spend = models.IntegerField(default=0)