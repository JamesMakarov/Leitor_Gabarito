from django.urls import path
from .views import iniciar_leitura, login_view, register_view, logout_view, home_view, perfil_view

urlpatterns = [
    path('upload/', iniciar_leitura, name="upload"), 
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('home/', home_view, name='home'),
    path('perfil/', perfil_view, name='perfil'),
]
