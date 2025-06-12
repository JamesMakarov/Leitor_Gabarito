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
from .forms import PerfilForm, DadosImagemForm
from tempfile import NamedTemporaryFile
from .models import ImagemUpload
from django.core.files import File
from PIL import Image
from .biblioteca import leitor_lib
from django.http import HttpResponse, Http404
from .models import ImagemUpload, DadosImagem

@login_required
def iniciar_leitura(request):
    if request.method == "POST":
        if request.FILES.get("imagem"):
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

                # ⚠️ Salvar a imagem original no banco
                imagem_upload.seek(0)
                imagem_binaria = imagem_upload.read()
                imagem_obj = ImagemUpload.objects.create(
                    usuario=request.user,
                    nome_arquivo=imagem_upload.name,
                    conteudo=imagem_binaria
                )

                # Apagar imagem temporária
                os.remove(tmp_path)

                form = DadosImagemForm(initial={
                    'id_prova': resultado.id_prova,
                    'id_participante': resultado.id_participante,
                    'leitura': leitura_decodificada,
                })

                return render(request, 'revisar_leitura.html', {
                    'form': form,
                    'imagem_id': imagem_obj.id  # Passa o ID para o template
                })

            except Exception as e:
                if 'tmp_path' in locals() and os.path.exists(tmp_path):
                    os.remove(tmp_path)
                return JsonResponse({"erro": -99, "mensagem": f"Erro inesperado: {str(e)}"})

        else:
            # Submissão do formulário de revisão
            imagem_id = request.POST.get('imagem_id')
            imagem = get_object_or_404(ImagemUpload, pk=imagem_id, usuario=request.user)

            form = DadosImagemForm(request.POST)
            if form.is_valid():
                leitura = form.save(commit=False)
                leitura.usuario = request.user
                leitura.imagem = imagem  # ✅ associa a imagem corretamente
                leitura.save()
                messages.success(request, "Leitura confirmada e salva com sucesso!")
                return redirect('home')
            else:
                messages.error(request, "Erro ao salvar. Verifique os campos.")
                return render(request, 'revisar_leitura.html', {
                    'form': form,
                    'imagem_id': imagem_id  # reenviar no erro para manter estado
                })

    return render(request, "upload.html")



User = get_user_model()

def login_view(request):
    if request.method == "POST":
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
            return redirect('perfil')  # só redireciona se salvou
    else:
        form = PerfilForm(instance=perfil)

    # perfil está preenchido se nome_completo e bio foram salvos
    perfil_preenchido = all([
    perfil.nome_completo,
    perfil.bio,
    perfil.nascimento,
    perfil.foto
])

    context = {
        'form': form,
        'perfil': perfil,
        'mostrar_formulario': not perfil_preenchido,
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
        form = DadosImagemForm(request.POST, instance=dado)
        if form.is_valid():
            form.save()
            messages.success(request, "Dados atualizados com sucesso!")
            return redirect('dados_leituras')
    else:
        form = DadosImagemForm(instance=dado)

    return render(request, 'editar_dado.html', {'form': form})

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

