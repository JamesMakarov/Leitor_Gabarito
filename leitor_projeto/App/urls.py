from django.urls import path
from .views import iniciar_leitura  # Certifique-se de que essa view existe!

urlpatterns = [
    path('upload/', iniciar_leitura, name="upload"),  # Endpoint correto para o envio de imagem
]