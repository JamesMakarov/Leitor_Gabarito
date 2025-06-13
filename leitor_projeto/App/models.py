from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nome_completo = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    nascimento = models.DateField(blank=True, null=True)
    foto = models.BinaryField(blank=True, null=True)


class ImagemUpload(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nome_arquivo = models.CharField(max_length=255)
    conteudo = models.BinaryField()
    criado_em = models.DateTimeField(auto_now_add=True)
    confirmada = models.BooleanField(default=False)

class DadosImagem(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    imagem = models.OneToOneField('ImagemUpload', on_delete=models.CASCADE)
    id_prova = models.IntegerField()
    id_participante = models.IntegerField()
    leitura = models.TextField()
    pontuacao = models.IntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True)
