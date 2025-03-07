# accounts/views.py
from rest_framework import status, generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token

from .serializers import UserSerializer, UserCreateSerializer, AuthTokenSerializer


class CreateUserView(generics.CreateAPIView):
    """
    View para criar um novo usuário.
    """
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        user = serializer.instance
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)


class LoginView(ObtainAuthToken):
    """
    View para autenticar usuários e retornar tokens.
    """
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'email': user.email
        })


class LogoutView(APIView):
    """
    View para logout do usuário e invalidar o token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Deletar o token do usuário, invalidando-o
        request.user.auth_token.delete()
        return Response({"message": "Logout realizado com sucesso."},
                        status=status.HTTP_200_OK)


class TestTokenView(APIView):
    """
    View para testar se o token do usuário é válido.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "message": "Token válido",
            "user": UserSerializer(request.user).data
        })