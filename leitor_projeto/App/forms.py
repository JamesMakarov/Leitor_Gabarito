from django import forms
from .models import Perfil, DadosImagem

class PerfilForm(forms.ModelForm):
    foto_arquivo = forms.ImageField(required=False, label="Foto de perfil")  # novo campo de upload

    class Meta:
        model = Perfil
        fields = ['nome_completo', 'bio', 'nascimento', 'foto_arquivo']

    def save(self, commit=True):
        instance = super().save(commit=False)

        if self.cleaned_data.get('foto_arquivo'):
            imagem = self.cleaned_data['foto_arquivo']
            instance.foto = imagem.read()  # lê como binário

        if commit:
            instance.save()

        return instance

class LeituraGabaritoForm(forms.ModelForm):
    class Meta:
        model = DadosImagem
        fields = ['id_prova', 'id_participante', 'leitura']

class DadosImagemForm(forms.ModelForm):
    class Meta:
        model = DadosImagem
        fields = ['id_prova', 'id_participante', 'leitura']
