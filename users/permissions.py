from rest_framework import permissions
from django.contrib.auth import get_user_model

User = get_user_model()


class IsSelfOrAdmin(permissions.BasePermission):
    """
    Permite que usuários acessem apenas seu próprio recurso, exceto admins.
    """

    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.role == 'ADMIN'


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permite operações de escrita apenas para administradores.
    Operações de leitura são permitidas para todos.
    """

    def has_permission(self, request, view):
        # Permite métodos seguros (GET, HEAD, OPTIONS) para todos
        if request.method in permissions.SAFE_METHODS:
            return True

        # Apenas admins podem fazer POST, PUT, PATCH, DELETE
        return request.user.is_authenticated and request.user.role == 'ADMIN'


class IsEditorOrReadOnly(permissions.BasePermission):
    """
    Permite que editores criem conteúdo, mas só editem seus próprios.
    Leitores podem apenas visualizar.
    """

    def has_permission(self, request, view):
        # Todos podem ver
        if request.method in permissions.SAFE_METHODS:
            return True

        # Apenas editores e admins podem criar
        return request.user.is_authenticated and (
                request.user.role in ['EDITOR', 'ADMIN']
        )

    def has_object_permission(self, request, view, obj):
        # Todos podem ver
        if request.method in permissions.SAFE_METHODS:
            return True

        # Apenas o autor (se for editor) ou admin podem editar/deletar
        if request.user.role == 'ADMIN':
            return True

        return obj.author == request.user and request.user.role == 'EDITOR'


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permite que apenas o dono do objeto faça operações de escrita.
    Todos podem ler.
    """

    def has_object_permission(self, request, view, obj):
        # Permite métodos seguros para todos
        if request.method in permissions.SAFE_METHODS:
            return True

        # Apenas o dono do objeto pode modificar
        return obj.author == request.user


class HasCategoryAccess(permissions.BasePermission):
    """
    Permite acesso apenas a notícias que pertencem a categorias
    associadas ao plano de assinatura do usuário.
    """

    def has_object_permission(self, request, view, obj):
        # Verifica se o usuário está autenticado e possui uma assinatura ativa
        if not request.user.is_authenticated or not hasattr(request.user, 'subscription'):
            return False

        # Obtém as categorias do plano de assinatura do usuário
        user_categories = request.user.subscription.plan.categories.all()

        # Verifica se a notícia pertence a uma das categorias do plano
        return obj.categories.filter(id__in=user_categories).exists()