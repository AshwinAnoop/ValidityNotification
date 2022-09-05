from django.contrib import admin
from .models import Document,Categories,DocType,Notification,FileUploads

# Register your models here.

admin.site.register(Document)
admin.site.register(Categories)
admin.site.register(DocType)
admin.site.register(Notification)
admin.site.register(FileUploads)
