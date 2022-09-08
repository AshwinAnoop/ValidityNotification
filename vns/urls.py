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
]