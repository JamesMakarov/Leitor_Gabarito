from django.shortcuts import render
from django.http import JsonResponse
import ctypes
from pathlib import Path
import os

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
    leitor_lib.read_image_path.restype = ctypes.POINTER(Reading)

upload_dir = os.path.join(BASE_DIR, 'uploads')
if not os.path.exists(upload_dir):
    os.makedirs(upload_dir, exist_ok=True)

def iniciar_leitura(request):
    if request.method == "POST" and request.FILES.get("imagem"):
        imagem = request.FILES["imagem"]
        path_imagem = os.path.join(upload_dir, request.FILES["imagem"].name)    

        print(f"Imagem recebida: {imagem.name}")

        with open(path_imagem, "wb+") as destino:
            for chunk in imagem.chunks():
                destino.write(chunk)
        if not leitor_lib:
            return JsonResponse({"erro": -1, "mensagem": "Biblioteca não carregada"})
        if not os.path.exists(path_imagem):
            return JsonResponse({"erro": -2, "mensagem": "Arquivo não encontrado"})

        resultado_ptr = leitor_lib.read_image_path(path_imagem.encode("utf-8"))

        if resultado_ptr:
            resultado = resultado_ptr.contents
            return JsonResponse({
                "erro": resultado.erro,
                "id_prova": resultado.id_prova,
                "id_participante": resultado.id_participante,
                "leitura": resultado.leitura.decode("utf-8")
            })
        else:
            return JsonResponse({"erro": -3, "mensagem": "Erro ao processar a imagem"})

    return render(request, "upload.html")