from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('error/<str:message>', views.error, name='error'),
    path('users/<str:username>/', views.tasks, name='tasks'),
    path('donetask/', views.donetask, name='donetask'),
    path('addtask/', views.addtask, name='addtask'),
    path('adduser/', views.adduser, name='adduser'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
]