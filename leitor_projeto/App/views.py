from django.shortcuts import render
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

BASE_DIR = Path(__file__).resolve().parent.parent

LIBRARY_PATH = BASE_DIR / "App" / "libs" / "biblioteca" / "libleitor.so"

try:
    leitor_lib = ctypes.CDLL(str(LIBRARY_PATH))
except OSError as e:
    print(f"Erro ao carregar a biblioteca: {e}")
    leitor_lib = None

class Reading(ctypes.Structure):
    _fields_ = [
        ("erro", ctypes.c_int),
        ("id_prova", ctypes.c_int),
        ("id_participante", ctypes.c_int),
        ("leitura", ctypes.c_char_p)
    ]

if leitor_lib:
    leitor_lib.read_image_path.restype = Reading
    leitor_lib.read_image_path.argtypes = [ctypes.c_char_p]

upload_dir = os.path.join(BASE_DIR, 'uploads')
if not os.path.exists(upload_dir):
    os.makedirs(upload_dir, exist_ok=True)


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

                os.remove(tmp_path)

                form = DadosImagemForm(initial={
                    'id_prova': resultado.id_prova,
                    'id_participante': resultado.id_participante,
                    'leitura': leitura_decodificada,
                })

                return render(request, 'revisar_leitura.html', {'form': form})

            except Exception as e:
                if 'tmp_path' in locals() and os.path.exists(tmp_path):
                    os.remove(tmp_path)
                return JsonResponse({"erro": -99, "mensagem": f"Erro inesperado: {str(e)}"})

        else:
            form = DadosImagemForm(request.POST)  
            if form.is_valid():
                leitura = form.save(commit=False)
                leitura.usuario = request.user
                leitura.save()
                messages.success(request, "Leitura confirmada e salva com sucesso!")
                return redirect('home')
            else:
                messages.error(request, "Erro ao salvar. Verifique os campos.")
                return render(request, 'revisar_leitura.html', {'form': form})
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
            Perfil.objects.create(usuario=user) 
            login(request, user)
            return redirect('home')
    return render(request, 'accounts/register.html')


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
def galeria_usuario(request):
    imagens = ImagemUpload.objects.filter(usuario=request.user).order_by('-data_envio')
    return render(request, 'galeria.html', {'imagens': imagens})
