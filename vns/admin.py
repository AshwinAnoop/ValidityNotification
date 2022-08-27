from django.contrib import admin
from .models import Document,Categories,DocType,Notification

# Register your models here.

admin.site.register(Document)
admin.site.register(Categories)
admin.site.register(DocType)
admin.site.register(Notification)
