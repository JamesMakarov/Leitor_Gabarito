from django.shortcuts import render
from django.http import JsonResponse
import ctypes
from pathlib import Path
import os


# Definir caminho absoluto da biblioteca
BASE_DIR = Path(__file__).resolve().parent.parent
LIBRARY_PATH = "/Projeto PET/Leitor_Gabarito/leitor_projeto/App/libs/biblioteca/libleitor.so"

# Tentar carregar a biblioteca, tratando erros
try:
    leitor_lib = ctypes.CDLL(LIBRARY_PATH)
except OSError as e:
    print(f"Erro ao carregar a biblioteca: {e}")
    leitor_lib = None  # Evita falhas se a biblioteca não estiver disponível

# Definir estrutura do retorno da biblioteca
class Reading(ctypes.Structure):
    _fields_ = [
        ("erro", ctypes.c_int),
        ("id_prova", ctypes.c_int),
        ("id_participante", ctypes.c_int),
        ("leitura", ctypes.c_char_p)
    ]

# Configurar a função para retornar um ponteiro para a estrutura Reading
if leitor_lib:
    leitor_lib.read_image_path.restype = ctypes.POINTER(Reading)

# Diretório de uploads
upload_dir = "/Projeto PET/uploads/"
if not os.path.exists(upload_dir):
    os.makedirs(upload_dir)

# Função para processar imagem enviada via formulário
def iniciar_leitura(request):
    if request.method == "POST" and request.FILES.get("imagem"):
        imagem = request.FILES["imagem"]
        path_imagem = os.path.join(upload_dir, request.FILES["imagem"].name)    

        print(f"Imagem recebida: {imagem.name}")  # Apenas para debug

        # Salvar a imagem no servidor
        with open(path_imagem, "wb+") as destino:
            for chunk in imagem.chunks():
                destino.write(chunk)

        # Verificar se a biblioteca foi carregada corretamente
        if not leitor_lib:
            return JsonResponse({"erro": -1, "mensagem": "Biblioteca não carregada"})

        # Verificar se o arquivo existe antes de chamar a biblioteca
        if not os.path.exists(path_imagem):
            return JsonResponse({"erro": -2, "mensagem": "Arquivo não encontrado"})

        # Chamar a biblioteca corretamente e acessar os dados retornados
        resultado_ptr = leitor_lib.read_image_path(path_imagem.encode("utf-8"))

        if resultado_ptr:  # Verificar se o ponteiro não é None
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