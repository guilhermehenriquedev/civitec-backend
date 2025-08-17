from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from .serializers import (
    UserSerializer, UserCreateSerializer, InviteCreateSerializer,
    InviteListSerializer, InvitePublicValidateSerializer, InviteAcceptSerializer
)
from .permissions import IsMasterAdmin, IsSectorAdmin, IsSectorOperator, IsEmployeeSelf
from .models import UserInvite
from .services import send_invite_email, send_welcome_email
from audit.models import AuditLog

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
        """Retorna informações do usuário logado com roles e permissões"""
        user = request.user
        data = UserSerializer(user).data
        
        # Adicionar informações de roles e permissões
        data['role'] = user.role
        data['sector'] = user.sector
        data['permissions'] = user.get_permissions()
        data['is_master_admin'] = user.is_master_admin
        data['is_sector_admin'] = user.is_sector_admin
        data['is_sector_operator'] = user.is_sector_operator
        data['is_employee'] = user.is_employee
        
        # Log de auditoria para debug
        try:
            AuditLog.log_user_action(
                user=user,
                action='READ',
                entity='User',
                entity_id=user.id,
                payload={'endpoint': 'me', 'user_id': user.id},
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                url=request.path,
                method=request.method
            )
        except Exception as e:
            print(f"Erro ao criar log de auditoria: {e}")
        
        return Response(data)
    
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
        
        old_role = user.role
        user.role = new_role
        user.save()
        
        # Log de auditoria
        AuditLog.log_user_action(
            user=request.user,
            action='UPDATE',
            entity='User',
            entity_id=user.id,
            payload={'old_role': old_role, 'new_role': new_role},
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            url=request.path,
            method=request.method
        )
        
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
        
        old_sector = user.sector
        user.sector = new_sector
        user.save()
        
        # Log de auditoria
        AuditLog.log_user_action(
            user=request.user,
            action='UPDATE',
            entity='User',
            entity_id=user.id,
            payload={'old_sector': old_sector, 'new_sector': new_sector},
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            url=request.path,
            method=request.method
        )
        
        serializer = self.get_serializer(user)
        return Response(serializer.data)
    
    def list(self, request, *args, **kwargs):
        """Lista todos os usuários com suas permissões"""
        users = User.objects.all()
        
        user_data = []
        for user in users:
            user_data.append({
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_active': user.is_active,
                'date_joined': user.date_joined,
                'last_login': user.last_login,
                'role': user.role,
                'sector': user.sector,
            })
        
        return Response(user_data)
    
    def update(self, request, *args, **kwargs):
        """Atualiza permissões do usuário"""
        user = self.get_object()
        data = request.data
        
        try:
            with transaction.atomic():
                # Atualizar status do usuário
                if 'is_active' in data:
                    user.is_active = data['is_active']
                    user.save()
                
                # Atualizar roles e setores
                if 'role' in data:
                    user.role = data['role']
                if 'sector' in data:
                    user.sector = data['sector']
                
                user.save()
                
                # Log de auditoria
                AuditLog.log_action(
                    user=request.user,
                    action='UPDATE',
                    obj=user,
                    payload={'updated_fields': list(data.keys())},
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT'),
                    url=request.path,
                    method=request.method
                )
                
                return Response({
                    'message': 'Usuário atualizado com sucesso',
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'is_active': user.is_active,
                    }
                })
                
        except Exception as e:
            return Response(
                {'error': f'Erro ao atualizar usuário: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class InviteViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciamento de convites"""
    queryset = UserInvite.objects.all()
    serializer_class = InviteListSerializer
    permission_classes = [IsMasterAdmin]
    pagination_class = None  # Desabilitar paginação para convites
    
    def get_serializer_class(self):
        if self.action == 'create':
            return InviteCreateSerializer
        return InviteListSerializer
    
    def list(self, request, *args, **kwargs):
        """Lista todos os convites"""
        return super().list(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        """Cria um novo convite e envia e-mail"""
        print("🔍 DEBUG: InviteViewSet.create chamado")
        print(f"🔍 DEBUG: Usuário: {request.user.email}")
        print(f"🔍 DEBUG: Dados recebidos: {request.data}")
        print(f"🔍 DEBUG: Headers: {dict(request.headers)}")
        print(f"🔍 DEBUG: Content-Type: {request.content_type}")
        
        serializer = self.get_serializer(data=request.data)
        print(f"🔍 DEBUG: Serializer criado: {serializer.__class__.__name__}")
        
        # Validar dados
        if not serializer.is_valid():
            print(f"❌ DEBUG: Serializer inválido - Erros: {serializer.errors}")
            return Response(
                {'error': 'Dados inválidos', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        print(f"✅ DEBUG: Serializer válido - Dados: {serializer.validated_data}")
        
        with transaction.atomic():
            try:
                invite = serializer.save()
                print(f"✅ DEBUG: Convite criado com ID: {invite.id}")
                
                # Enviar e-mail de convite
                try:
                    print("🔍 DEBUG: Tentando enviar e-mail...")
                    send_invite_email(invite)
                    print("✅ DEBUG: E-mail enviado com sucesso")
                    
                    # Log de auditoria
                    AuditLog.log_action(
                        user=request.user,
                        action='CREATE',
                        obj=invite,
                        payload={'email': invite.email, 'full_name': invite.full_name},
                        ip_address=request.META.get('REMOTE_ADDR'),
                        user_agent=request.META.get('HTTP_USER_AGENT'),
                        url=request.path,
                        method=request.method
                    )
                    print("✅ DEBUG: Log de auditoria criado")
                    
                    return Response(
                        {
                            'message': 'Convite enviado com sucesso!',
                            'invite': InviteListSerializer(invite).data
                        },
                        status=status.HTTP_201_CREATED
                    )
                    
                except Exception as e:
                    print(f"❌ DEBUG: Erro ao enviar e-mail: {e}")
                    # Se falhar ao enviar e-mail, deletar o convite
                    invite.delete()
                    return Response(
                        {'error': f'Erro ao enviar e-mail: {str(e)}'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                    
            except Exception as e:
                print(f"❌ DEBUG: Erro ao salvar convite: {e}")
                import traceback
                traceback.print_exc()
                return Response(
                    {'error': f'Erro interno: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
    
    @action(detail=True, methods=['patch'], permission_classes=[IsMasterAdmin])
    def cancel(self, request, pk=None):
        """Cancela um convite"""
        invite = self.get_object()
        
        if invite.status != UserInvite.StatusChoices.PENDING:
            return Response(
                {'error': 'Apenas convites pendentes podem ser cancelados'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        invite.cancel()
        
        # Log de auditoria
        AuditLog.log_action(
            user=request.user,
            action='UPDATE',
            obj=invite,
            payload={'status': 'CANCELLED'},
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            url=request.path,
            method=request.method
        )
        
        return Response({'message': 'Convite cancelado com sucesso'})
    
    @action(detail=False, methods=['get'], permission_classes=[IsMasterAdmin])
    def pending(self, request):
        """Lista apenas convites pendentes"""
        queryset = self.queryset.filter(status=UserInvite.StatusChoices.PENDING)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PublicInviteViewSet(viewsets.ViewSet):
    """ViewSet público para validação e aceitação de convites"""
    permission_classes = []  # Sem autenticação
    
    @action(detail=False, methods=['post'])
    def validate(self, request):
        """Valida um convite público"""
        print("🔍 DEBUG: PublicInviteViewSet.validate chamado")
        print(f"🔍 DEBUG: Dados recebidos: {request.data}")
        print(f"🔍 DEBUG: Headers: {dict(request.headers)}")
        
        serializer = InvitePublicValidateSerializer(data=request.data)
        print(f"🔍 DEBUG: Serializer criado: {serializer.__class__.__name__}")
        
        if not serializer.is_valid():
            print(f"❌ DEBUG: Serializer inválido - Erros: {serializer.errors}")
            return Response(
                {'error': 'Dados inválidos', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        print(f"✅ DEBUG: Serializer válido - Dados: {serializer.validated_data}")
        
        invite = serializer.validated_data['invite']
        print(f"✅ DEBUG: Convite encontrado: {invite.id} - {invite.email}")
        
        # Retornar informações mascaradas do convite
        email_parts = invite.email.split('@')
        masked_email = f"{email_parts[0][:2]}***@{email_parts[1]}"
        
        response_data = {
            'valid': True,
            'full_name': invite.full_name,
            'email_masked': masked_email,
            'role_display': invite.get_role_code_display(),
            'sector_display': invite.get_sector_code_display() if invite.sector_code else 'Não definido',
            'security_code': invite.security_code  # Incluir o código para uso posterior
        }
        
        print(f"✅ DEBUG: Resposta enviada: {response_data}")
        return Response(response_data)
    
    @action(detail=False, methods=['post'])
    def accept(self, request):
        """Aceita um convite e cria a senha do usuário"""
        serializer = InviteAcceptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            user = serializer.save()
            
            # Enviar e-mail de boas-vindas
            try:
                send_welcome_email(user)
            except Exception:
                # Não falhar se o e-mail de boas-vindas falhar
                pass
            
            # Log de auditoria
            AuditLog.log_action(
                user=user,
                action='CREATE',
                obj=user,
                payload={'invite_accepted': True, 'email': user.email},
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                url=request.path,
                method=request.method
            )
            
            return Response({
                'message': 'Conta criada com sucesso! Agora você pode fazer login.',
                'user_id': user.id,
                'email': user.email
            })


class CustomTokenObtainPairView(TokenObtainPairView):
    """View customizada para login JWT com auditoria"""
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Adicionar informações do usuário na resposta
            user = User.objects.get(email=request.data['email'])
            user_data = UserSerializer(user).data
            
            # Adicionar informações de roles e permissões
            user_data['roles'] = [user.role]
            user_data['sectors'] = [user.sector] if user.sector else []
            user_data['permissions'] = user.get_permissions()
            user_data['is_master_admin'] = user.is_master_admin
            user_data['is_sector_admin'] = user.is_sector_admin
            user_data['is_sector_operator'] = user.is_sector_operator
            user_data['is_employee'] = user.is_employee
            
            response.data['user'] = user_data
            
            # Log de auditoria de login bem-sucedido
            AuditLog.log_user_action(
                user=user,
                action='LOGIN',
                entity='User',
                entity_id=user.id,
                payload={'login_success': True},
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                url=request.path,
                method=request.method
            )
        else:
            # Log de auditoria de login falhado
            email = request.data.get('email', 'unknown')
            AuditLog.log_user_action(
                user=None,
                action='LOGIN',
                entity='User',
                entity_id=0,
                payload={'login_failed': True, 'email': email},
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                url=request.path,
                method=request.method
            )
        
        return response
