from django.contrib import admin
from .models import Advertisement, Document,Categories,DocType, InAppAds,Notification,FileUploads, NotifyAds, Wallet, WalletBalance

# Register your models here.

admin.site.register(Document)
admin.site.register(Categories)
admin.site.register(DocType)
admin.site.register(Notification)
admin.site.register(FileUploads)
admin.site.register(Wallet)
admin.site.register(WalletBalance)
admin.site.register(Advertisement)
admin.site.register(NotifyAds)
admin.site.register(InAppAds)