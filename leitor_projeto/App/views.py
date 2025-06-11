from django.shortcuts import render
from django.http import JsonResponse
import ctypes
from pathlib import Path
import os
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import Perfil
from .forms import PerfilForm




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
    if request.method == "POST" and request.FILES.get("imagem"):
        imagem = request.FILES["imagem"]
        path_imagem = os.path.join(upload_dir, imagem.name)

        print(f"Imagem recebida: {imagem.name}")

        with open(path_imagem, "wb+") as destino:
            for chunk in imagem.chunks():
                destino.write(chunk)

        if not leitor_lib:
            return JsonResponse({"erro": -1, "mensagem": "Biblioteca não carregada"})

        if not os.path.exists(path_imagem):
            return JsonResponse({"erro": -2, "mensagem": "Arquivo não encontrado"})

        resultado = leitor_lib.read_image_path(path_imagem.encode("utf-8"))

        # Segurança: checar se leitura é válida antes de decodificar
        leitura = resultado.leitura
        leitura_decodificada = leitura.decode("utf-8") if leitura else ""

        return JsonResponse({
            "erro": resultado.erro,
            "id_prova": resultado.id_prova,
            "id_participante": resultado.id_participante,
            "leitura": leitura_decodificada
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
