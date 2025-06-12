from django import forms
from .models import Perfil, DadosImagem

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['nome_completo', 'bio', 'nascimento', 'foto']

class LeituraGabaritoForm(forms.ModelForm):
    class Meta:
        model = DadosImagem
        fields = ['id_prova', 'id_participante', 'leitura']

class DadosImagemForm(forms.ModelForm):
    class Meta:
        model = DadosImagem
        fields = ['id_prova', 'id_participante', 'leitura']
