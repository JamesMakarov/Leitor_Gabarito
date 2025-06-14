from django.contrib import admin
from django.urls import path, include  
from App.views import redirecionar_para_login

urlpatterns = [
    path('', redirecionar_para_login),
    path('admin/', admin.site.urls),
    path('auth/', include('App.urls')), 
    
]
