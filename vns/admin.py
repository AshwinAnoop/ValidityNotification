from .models import Advertisement, Document,Categories,DocType, InAppAds,Notification,FileUploads, NotifyAds, Wallet, WalletBalance
from django.contrib.admin import ModelAdmin,register
from rangefilter.filters import DateRangeFilter
from admin_numeric_filter.admin import RangeNumericFilter

# Register your models here.


@register(Document)
class DocumentAdmin(ModelAdmin):
    icon_name = 'work'
    list_display = ('id','doc_name','user_id','category','sub_category','doc_type','start_date','end_date' )
    list_filter = ('user_id','category','sub_category','doc_type','end_date',('end_date',DateRangeFilter),)
    # def get_doc_name(self, obj):
    #     return obj.doc_name
    # get_doc_name.short_description = 'User Name'

@register(Categories)
class CategoriesAdmin(ModelAdmin):
    icon_name = 'extension'
    list_display = ('category','sub_category')
    list_filter = ('category',)

@register(DocType)
class DocTypeAdmin(ModelAdmin):
    icon_name = 'extension'

@register(Notification)
class NotificationAdmin(ModelAdmin):
    icon_name = 'circle_notifications'
    list_display = ('id','doc_id','notify_date','is_notified')
    list_filter = ('doc_id','notify_date','is_notified',('notify_date',DateRangeFilter),)

@register(FileUploads)
class FileUploadsAdmin(ModelAdmin):
    icon_name = 'file_upload'
    list_display = ('docu_id','filepath')
    list_filter = ('docu_id',)
@register(Wallet)
class WalletAdmin(ModelAdmin):
    icon_name = 'attach_money'
    list_display = ('user_id','amount','transactdate')
    list_filter = ('user_id','transactdate')

@register(WalletBalance)
class WalletBalanceAdmin(ModelAdmin):
    icon_name = 'account_balance_wallet'
    list_display = ('user_id','balance','total_ads','total_spend')
    list_filter = ('user_id',)

@register(Advertisement)
class AdvertisementAdmin(ModelAdmin):
    icon_name = 'access_alarm'
    list_display = ('id','user_id','ad_name','ad_type','publish_count','amount_spend' )
    list_filter = ('user_id','ad_type',('publish_count', RangeNumericFilter),('amount_spend', RangeNumericFilter),)
@register(NotifyAds)
class NotifyAdsAdmin(ModelAdmin):
    icon_name = 'add_alert'
    list_display = ('id','doc_id','category','sub_category','ad_id1','ad_id2','ad_id3')
    list_filter = ('doc_id','category','sub_category','ad_id1','ad_id2','ad_id3')

@register(InAppAds)
class InAppAdsAdmin(ModelAdmin):
    icon_name = 'add_alert'
    list_display = ('id','doc_id','category','sub_category','ad_id1','ad_id2','ad_id3')
    list_filter = ('doc_id','category','sub_category','ad_id1','ad_id2','ad_id3')
