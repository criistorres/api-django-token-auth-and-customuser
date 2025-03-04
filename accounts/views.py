# accounts/views.py
from rest_framework import status, generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token

from checkins.permissions import IsLogistica
from .models import CustomUser

from .serializers import UserAdminSerializer, UserSerializer, UserCreateSerializer, AuthTokenSerializer


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
            'email': user.email,
            'name': user.first_name + ' ' + user.last_name,
            'role': user.role
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
    
class ListUsersView(generics.ListAPIView):
    """
    View para listar usuários.
    """
    
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class ActivateUserView(APIView):
    """
    View para ativar o usuário (is_active = True).
    """
    permission_classes = [IsAuthenticated, IsLogistica]

    def post(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
            user.is_active = True
            user.save()
            return Response({"message": "Usuário ativado com sucesso."}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"error": "Usuário não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        
class DesactivateUserView(APIView):
    """
    View para desativar o usuário (is_active = False).
    """
    permission_classes = [IsAuthenticated, IsLogistica]

    def post(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
            user.is_active = False
            user.save()
            return Response({"message": "Usuário desativado com sucesso."}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"error": "Usuário não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        
class UserDetailView(APIView):
    """
    View para retornar os dados de um usuário pelo id.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
            return Response(UserSerializer(user).data)
        except CustomUser.DoesNotExist:
            return Response({"error": "Usuário não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        
class UserEditAdminView(APIView):
    """
    View para editar os dados de um usuário.
    """
    
    senha_admin = 'Beauty807*'
    permission_classes = [AllowAny]

    def post(self, request, user_id):
        try:
            senha_admin = request.data['senha_admin']
            if senha_admin != self.senha_admin:
                return Response({"error": "Senha de administração incorreta."}, status=status.HTTP_401_UNAUTHORIZED)
            user = CustomUser.objects.get(id=user_id)
            user.first_name = request.data['first_name']
            user.last_name = request.data['last_name']
            user.email = request.data['email']
            user.role = request.data['role']
            user.is_active = request.data['is_active']
            user.is_staff = request.data['is_staff']
            user.phone = request.data['phone']
            user.cpf = request.data['cpf']
            user.save()
            return Response(UserAdminSerializer(user).data)
        except CustomUser.DoesNotExist:
            return Response({"error": "Usuário não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        
class UserEditView(APIView):
    """
    View para editar os dados do usuário logado.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user.first_name = request.data['first_name']
        user.last_name = request.data['last_name']
        user.email = request.data['email']
        user.phone = request.data['phone']
        user.cpf = request.data['cpf']
        user.save()
        return Response(UserSerializer(user).data)