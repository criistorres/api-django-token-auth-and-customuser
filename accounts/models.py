# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    """
    Gerenciador de modelo customizado para o modelo CustomUser com email como identificador único.
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Cria e salva um usuário com o email e senha fornecidos.
        """
        if not email:
            raise ValueError('O campo Email é obrigatório')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Cria e salva um superusuário com o email e senha fornecidos.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser deve ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser deve ter is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Modelo de usuário customizado que usa email como campo de username.
    """
    email = models.EmailField('Endereço de email', unique=True)
    first_name = models.CharField('Nome', max_length=30, blank=True)
    last_name = models.CharField('Sobrenome', max_length=30, blank=True)
    is_active = models.BooleanField('Ativo', default=False)
    is_staff = models.BooleanField('Staff', default=False)
    date_joined = models.DateTimeField('Data de registro', default=timezone.now)
    ROLE_CHOICES = [
        ('motorista', 'Motorista'),
        ('logistica', 'Logística'),
    ]
    role = models.CharField('Função', max_length=30, choices=ROLE_CHOICES, blank=True)
    phone = models.CharField('Telefone', max_length=15, blank=True)
    cpf = models.CharField('CPF', max_length=11, blank=True, unique=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.email

    def get_full_name(self):
        """
        Retorna o nome completo do usuário.
        """
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    def get_short_name(self):
        """
        Retorna o primeiro nome do usuário.
        """
        return self.first_name
    
    def is_logistica(self):
        return self.role == 'logistica'