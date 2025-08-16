from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, UserCreateSerializer
from .permissions import IsMasterAdmin, IsSectorAdmin, IsSectorOperator, IsEmployeeSelf

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciamento de usuários"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsMasterAdmin]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Retorna informações do usuário logado"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsMasterAdmin])
    def change_role(self, request, pk=None):
        """Altera o role de um usuário (apenas MASTER_ADMIN)"""
        user = self.get_object()
        new_role = request.data.get('role')
        
        if new_role not in dict(User.RoleChoices.choices):
            return Response(
                {'error': 'Role inválido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.role = new_role
        user.save()
        
        serializer = self.get_serializer(user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsMasterAdmin])
    def change_sector(self, request, pk=None):
        """Altera o setor de um usuário (apenas MASTER_ADMIN)"""
        user = self.get_object()
        new_sector = request.data.get('sector')
        
        if new_sector and new_sector not in dict(User.SectorChoices.choices):
            return Response(
                {'error': 'Setor inválido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.sector = new_sector
        user.save()
        
        serializer = self.get_serializer(user)
        return Response(serializer.data)


class CustomTokenObtainPairView(TokenObtainPairView):
    """View customizada para login JWT"""
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Adicionar informações do usuário na resposta
            # Como USERNAME_FIELD é 'email', usamos o email para buscar
            user = User.objects.get(email=request.data['email'])
            user_data = UserSerializer(user).data
            response.data['user'] = user_data
        
        return response
