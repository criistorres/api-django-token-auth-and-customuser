# accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo de usuário.
    """
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'phone', 'cpf')
        read_only_fields = ('id',)


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criação de novos usuários.
    """
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('email', 'password', 'password_confirm', 'first_name', 'last_name', 'role', 'phone', 'cpf')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        """
        Valida se as senhas digitadas coincidem.
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "As senhas não coincidem."})
        return attrs

    def create(self, validated_data):
        """
        Cria e retorna um novo usuário.
        """
        # Remover o campo password_confirm que não faz parte do modelo
        validated_data.pop('password_confirm')
        
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=validated_data.get('role', ''),
            phone=validated_data.get('phone', ''),
            cpf=validated_data.get('cpf', '')
        )
        
        return user


class AuthTokenSerializer(serializers.Serializer):
    """
    Serializer para autenticação do usuário.
    """
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """
        Valida e autentica o usuário.
        """
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,  # Django usa username como campo de autenticação
                password=password
            )

            if not user:
                msg = _('Não foi possível autenticar com as credenciais fornecidas.')
                raise serializers.ValidationError(msg, code='authentication')
        else:
            msg = _('Email e senha são obrigatórios.')
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        return attrs