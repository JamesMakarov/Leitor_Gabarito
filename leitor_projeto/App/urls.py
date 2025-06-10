from django.urls import path
from .views import iniciar_leitura 

urlpatterns = [
    path('upload/', iniciar_leitura, name="upload"),  
]