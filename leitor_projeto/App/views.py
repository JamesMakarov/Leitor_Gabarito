from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
import ctypes
from pathlib import Path
import os, io
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import Perfil
from .forms import PerfilForm, RevisaoGabaritoForm, DadosImagemForm
from tempfile import NamedTemporaryFile
from .models import ImagemUpload
from django.core.files import File
from PIL import Image
from .biblioteca import leitor_lib
from django.http import HttpResponse, Http404
from .models import ImagemUpload, DadosImagem
from .utils import GABARITOS, calcular_pontuacao

@login_required
def iniciar_leitura(request):
    if request.method == "POST":
        if request.FILES.get("imagem"):
            ImagemUpload.objects.filter(usuario=request.user, confirmada=False).delete()

            imagem_upload = request.FILES["imagem"]

            if not leitor_lib:
                return JsonResponse({"erro": -1, "mensagem": "Biblioteca não carregada"})

            try:
                imagem = Image.open(imagem_upload)
                buffer = io.BytesIO()
                imagem.save(buffer, format="PNG")
                buffer.seek(0)

                with NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    tmp.write(buffer.read())
                    tmp_path = tmp.name

                resultado = leitor_lib.read_image_path(tmp_path.encode("utf-8"))
                leitura = resultado.leitura
                leitura_decodificada = leitura.decode("utf-8") if leitura else ""

                imagem_upload.seek(0)
                imagem_binaria = imagem_upload.read()
                imagem_obj = ImagemUpload.objects.create(
                    usuario=request.user,
                    nome_arquivo=imagem_upload.name,
                    conteudo=imagem_binaria,
                    confirmada=False
                )

                os.remove(tmp_path)

                form = RevisaoGabaritoForm(
                    leitura=leitura_decodificada,
                    initial={
                        'id_prova': resultado.id_prova,
                        'id_participante': resultado.id_participante
                    }
                )

                return render(request, 'revisar_leitura.html', {
                    'form': form,
                    'imagem_id': imagem_obj.id
                })

            except Exception as e:
                if 'tmp_path' in locals() and os.path.exists(tmp_path):
                    os.remove(tmp_path)
                return JsonResponse({"erro": -99, "mensagem": f"Erro inesperado: {str(e)}"})

        else:
            imagem_id = request.POST.get('imagem_id')
            imagem = get_object_or_404(ImagemUpload, pk=imagem_id, usuario=request.user)

            form = RevisaoGabaritoForm(request.POST)
            if form.is_valid():
                respostas = []
                for i in range(20):
                    valor = form.cleaned_data.get(f'questao_{i+1}', '')
                    respostas.append(valor if valor else 'x')

                leitura_str = ''.join(respostas)

                id_prova = form.cleaned_data['id_prova']
                gabarito = GABARITOS.get(id_prova)
                pontuacao = calcular_pontuacao(leitura_str, gabarito)

                DadosImagem.objects.create(
                    usuario=request.user,
                    imagem=imagem,
                    id_prova=id_prova,
                    id_participante=form.cleaned_data['id_participante'],
                    leitura=leitura_str,
                    pontuacao=pontuacao
                )

                imagem.confirmada = True
                imagem.save()

                messages.success(request, f"Leitura confirmada! Pontuação: {pontuacao}/20")
                return redirect('home')
            else:
                messages.error(request, "Erro ao salvar. Verifique os campos.")
                return render(request, 'revisar_leitura.html', {
                    'form': form,
                    'imagem_id': imagem_id
                })

    # <-- Aqui está a limpeza final -->
    ImagemUpload.objects.filter(usuario=request.user, confirmada=False).delete()
    return render(request, "upload.html")



User = get_user_model()

def login_view(request):
    if request.user.is_authenticated:
        messages.success(request, "Você já está logado!")
        return redirect('home')
    elif request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Credenciais inválidas.")
    return render(request, 'accounts/login.html')

def register_view(request):
    if request.user.is_authenticated:
        messages.success(request, "Você já está logado!")
        return redirect('home')
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        if User.objects.filter(email=email).exists():
            messages.error(request, "Este email já está em uso.")
        else:
            user = User.objects.create_user(
            username=email,
            email=email,
            password=password
            )
            Perfil.objects.create(user=user) 
            login(request, user)
            return redirect('home')
    return render(request, 'accounts/register.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def home_view(request):
    return render(request, 'accounts/home.html')

@login_required
def perfil_view(request):
    perfil = request.user.perfil

    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            return redirect('perfil')
    else:
        form = PerfilForm(instance=perfil)

    context = {
        'form': form,
        'perfil': perfil,
        'mostrar_formulario': True  # mostrar sempre
    }
    return render(request, 'accounts/perfil.html', context)


@login_required
def imagem_binaria(request, imagem_id):
    try:
        imagem = ImagemUpload.objects.get(pk=imagem_id, usuario=request.user)
        return HttpResponse(imagem.conteudo, content_type="image/png")  # ou "image/jpeg" conforme necessário
    except ImagemUpload.DoesNotExist:
        raise Http404("Imagem não encontrada")

@login_required
def galeria_usuario(request):
    ImagemUpload.objects.filter(usuario=request.user, confirmada=False).delete()
    imagens = ImagemUpload.objects.filter(usuario=request.user).order_by('-criado_em')
    
    return render(request, 'galeria.html', {'imagens': imagens})

@login_required
def dados_leituras(request):
    dados = DadosImagem.objects.filter(usuario=request.user).order_by('-criado_em')
    return render(request, 'dados.html', {'dados':dados})

@login_required
def editar_dado(request, dado_id):
    dado = get_object_or_404(DadosImagem, pk=dado_id, usuario=request.user)

    if request.method == 'POST':
        form = RevisaoGabaritoForm(request.POST)
        if form.is_valid():
            respostas = []
            for i in range(20):
                valor = form.cleaned_data.get(f'questao_{i+1}', '')
                respostas.append(valor if valor else 'x')
            leitura_str = ''.join(respostas)

            id_prova = form.cleaned_data['id_prova']
            gabarito = GABARITOS.get(id_prova)
            pontuacao = calcular_pontuacao(leitura_str, gabarito)

            # Atualiza os dados
            dado.id_prova = id_prova
            dado.id_participante = form.cleaned_data['id_participante']
            dado.leitura = leitura_str
            dado.pontuacao = pontuacao
            dado.save()

            messages.success(request, f"Dados atualizados com sucesso! Nova pontuação: {pontuacao}/20")
            return redirect('dados_leituras')
    else:
        leitura_str = dado.leitura or ""
        form = RevisaoGabaritoForm(
            leitura=leitura_str,
            initial={
                'id_prova': dado.id_prova,
                'id_participante': dado.id_participante
            }
        )

    return render(request, 'editar_dado.html', {'form': form, 'dado': dado})


@login_required
def deletar_dado(request, dado_id):
    dado = get_object_or_404(DadosImagem, pk=dado_id, usuario=request.user)

    if request.method == 'POST':
        if dado.imagem:
            dado.imagem.delete()  # deleta a imagem associada primeiro
        dado.delete()             # depois deleta o dado
        messages.success(request, "Dado e imagem deletados com sucesso.")
        return redirect('dados_leituras')

    return render(request, 'confirmar_delete.html', {'dado': dado})

