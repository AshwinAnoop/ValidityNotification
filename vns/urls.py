from django.urls import path

from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('register',views.register,name='register'),
    path('login',views.login,name='login'),
    path('home',views.home,name='home'),
    path('logout',views.logout,name='logout'),
    path('addDocs',views.addDocs,name='addDocs'),
    path('viewDocs',views.viewDocs,name='viewDocs'),
    path('showDetails/',views.showDetails, name='showDetails'),
    path('expiringDocs',views.expiringDocs,name='expiringDocs'),
    path('empHome',views.empHome,name='empHome'),
    path('addBusiness',views.addBusiness,name='addBusiness'),
    path('businessInfo',views.businessInfo,name='businessInfo'),
    path('businessHome',views.businessHome,name='businessHome'),
    path('advertiseHome',views.advertiseHome,name='advertiseHome'),
    path('addIad',views.addIad,name='addIad'),
    path('viewIad',views.viewIad,name='viewIad'),
    path('addNad',views.addNad,name='addNad'),
    path('viewNad',views.viewNad,name='viewNad'),
    path('wallet',views.wallet,name='wallet'),
    path('addMoney',views.addMoney,name='addMoney'),
    path('checkout',views.checkout, name='checkout'),
    path('marketHome',views.marketHome, name='marketHome'),
    path('iCategoryslots',views.iCategoryslots, name='iCategoryslots'),
    path('purchaseICslot1',views.purchaseICslot1, name='purchaseICslot1'),
    path('purchaseICslot2',views.purchaseICslot2, name='purchaseICslot2'),
    path('purchaseICslot3',views.purchaseICslot3, name='purchaseICslot3'),
    
]