from django.urls import path
from .views import AlunoLoginView

urlpatterns = [
    path('login/', AlunoLoginView.as_view(), name='aluno-login'),
]