from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('test',views.test),
    path('upload',views.upload),
]
