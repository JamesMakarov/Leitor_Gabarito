from django.shortcuts import render
from django.contrib.auth import authenticate, login

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Aluno
from .serializer import AlunoSerializer

class AlunoLoginView(APIView):
    def get(self, request, *args, **kwargs):
        return render(request, 'login.html')

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'error': 'Por favor, forneça o usuário e a senha.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        aluno = authenticate(username=username, password=password)

        if aluno is not None:
            login(request, aluno)
            serializer = AlunoSerializer(aluno)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Credenciais inválidas. Tente novamente.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
