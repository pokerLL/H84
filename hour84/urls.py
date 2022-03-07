from django.urls import path
from . import views
app_name =  "hour84"

urlpatterns = [
    path('',views.index,name='index')
    
]
