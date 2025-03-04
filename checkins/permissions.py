from rest_framework import permissions


class IsMotorista(permissions.BasePermission):
    """
    Permite acesso apenas a usuários com role 'motorista'
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.role == 'motorista'


class IsLogistica(permissions.BasePermission):
    """
    Permite acesso apenas a usuários com role 'logistica'
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.role == 'logistica'