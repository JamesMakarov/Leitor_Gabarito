from django import forms
from .models import Perfil, DadosImagem

class PerfilForm(forms.ModelForm):
    foto_arquivo = forms.ImageField(required=False, label="Foto de perfil")

    class Meta:
        model = Perfil
        fields = ['nome_completo', 'bio', 'nascimento', 'foto_arquivo']

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get('foto_arquivo'):
            imagem = self.cleaned_data['foto_arquivo']
            instance.foto = imagem.read()
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

OPCOES = [
    ('a', 'A'),
    ('b', 'B'),
    ('c', 'C'),
    ('d', 'D'),
    ('e', 'E'),
    ('0', 'Branco'),
    ('?', 'Mais de uma'),
]

class RevisaoGabaritoForm(forms.Form):
    id_prova = forms.IntegerField(label="ID da Prova")
    id_participante = forms.IntegerField(label="ID do Participante")

    def __init__(self, *args, leitura=None, **kwargs):
        super().__init__(*args, **kwargs)
        for i in range(20):
            letra = leitura[i] if leitura and i < len(leitura) else ''
            self.fields[f'questao_{i+1}'] = forms.ChoiceField(
                label=f"Questão {i+1}",
                choices=[('', '---')] + OPCOES,
                required=False,
                initial=letra if letra in dict(OPCOES) else '',
                widget=forms.RadioSelect
            )

