from django.db import models
from django.contrib.auth.models import User



class Aluno(models.Model):
    email = models.EmailField(max_length=254)
    username = models.CharField(max_length=100)
    senha = models.CharField(max_length=128)

    class Meta:
        verbose_name = 'aluno'
        verbose_name_plural = 'alunos'

    def __str__(self):
        return self.username
