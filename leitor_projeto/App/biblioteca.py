import os
import ctypes
from pathlib import Path
from django.conf import settings


# Caminho para a biblioteca
LIBRARY_PATH = settings.BASE_DIR / "App" / "libs" / "biblioteca" / "libleitor.so"

# Carrega a biblioteca externa
try:
    leitor_lib = ctypes.CDLL(str(LIBRARY_PATH))
except OSError as e:
    print(f"Erro ao carregar a biblioteca: {e}")
    leitor_lib = None

# Define o struct retornado pela biblioteca
class Reading(ctypes.Structure):
    _fields_ = [
        ("erro", ctypes.c_int),
        ("id_prova", ctypes.c_int),
        ("id_participante", ctypes.c_int),
        ("leitura", ctypes.c_char_p),
    ]

# Define os tipos de argumentos e retorno da função
if leitor_lib:
    leitor_lib.read_image_path.restype = Reading
    leitor_lib.read_image_path.argtypes = [ctypes.c_char_p]

    leitor_lib.read_image_data.restype = Reading
    leitor_lib.read_image_data.argtypes = [
        ctypes.c_char_p,
        ctypes.POINTER(ctypes.c_ubyte),
        ctypes.c_int
    ]

# Cria diretório de uploads se necessário
UPLOAD_DIR = settings.BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
