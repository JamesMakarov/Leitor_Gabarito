from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nome_completo = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    nascimento = models.DateField(null=True, blank=True)
    foto = models.ImageField(upload_to='fotos_perfil/', null=True, blank=True)

    def __str__(self):
        return f"Perfil de {self.usuario.email}"

class ImagemUpload(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nome_arquivo = models.CharField(max_length=255)
    conteudo = models.BinaryField()
    criado_em = models.DateTimeField(auto_now_add=True)

class DadosImagem(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    imagem = models.OneToOneField('ImagemUpload', on_delete=models.CASCADE)  # ⬅ aqui está o segredo
    id_prova = models.IntegerField()
    id_participante = models.IntegerField()
    leitura = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)
