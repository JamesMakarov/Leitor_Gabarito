from django.contrib import admin
from django.urls import path, include  # Correção da importação

urlpatterns = [
    path('admin/', admin.site.urls),
    path('App/', include('App.urls')),  # Certifique-se de que "App" é o nome correto do app
]
