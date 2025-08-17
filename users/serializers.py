from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import UserInvite

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer para usuários"""
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'cpf',
            'role', 'sector', 'is_active', 'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de usuários"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 'cpf',
            'role', 'sector', 'password', 'password_confirm'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("As senhas não coincidem.")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer para atualização de usuários"""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'cpf', 'role', 'sector', 'is_active'
        ]
    
    def validate_role(self, value):
        user = self.context['request'].user
        
        # Apenas MASTER_ADMIN pode alterar roles
        if not user.is_master_admin:
            raise serializers.ValidationError("Apenas administradores master podem alterar roles.")
        
        return value
    
    def validate_sector(self, value):
        user = self.context['request'].user
        
        # Apenas MASTER_ADMIN pode alterar setores
        if not user.is_master_admin:
            raise serializers.ValidationError("Apenas administradores master podem alterar setores.")
        
        return value


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer para alteração de senha"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("As novas senhas não coincidem.")
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Senha atual incorreta.")
        return value


# Serializers para o sistema de convites
class InviteCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de convites"""
    
    class Meta:
        model = UserInvite
        fields = ['email', 'full_name', 'role_code', 'sector_code']
    
    def validate_email(self, value):
        print(f"🔍 DEBUG: Validando e-mail: {value}")
        
        # Verificar se já existe um convite ativo para este e-mail
        if UserInvite.objects.filter(
            email=value,
            status=UserInvite.StatusChoices.PENDING
        ).exists():
            print(f"❌ DEBUG: E-mail {value} já tem convite ativo")
            raise serializers.ValidationError("Já existe um convite ativo para este e-mail.")
        
        # Verificar se o usuário já existe
        if User.objects.filter(email=value, is_active=True).exists():
            print(f"❌ DEBUG: E-mail {value} já tem usuário ativo")
            raise serializers.ValidationError("Já existe um usuário ativo com este e-mail.")
        
        print(f"✅ DEBUG: E-mail {value} válido")
        return value
    
    def create(self, validated_data):
        print(f"🔍 DEBUG: Serializer.create chamado com dados: {validated_data}")
        validated_data['created_by'] = self.context['request'].user
        print(f"🔍 DEBUG: Usuário criador: {validated_data['created_by'].email}")
        
        try:
            invite = super().create(validated_data)
            print(f"✅ DEBUG: Convite criado com sucesso: {invite.id}")
            return invite
        except Exception as e:
            print(f"❌ DEBUG: Erro ao criar convite: {e}")
            import traceback
            traceback.print_exc()
            raise


class InviteListSerializer(serializers.ModelSerializer):
    """Serializer para listagem de convites"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    role_display = serializers.CharField(source='get_role_code_display', read_only=True)
    sector_display = serializers.CharField(source='get_sector_code_display', read_only=True)
    
    class Meta:
        model = UserInvite
        fields = [
            'id', 'email', 'full_name', 'role_code', 'sector_code',
            'status', 'status_display', 'role_display', 'sector_display',
            'created_at', 'expires_at', 'accepted_at', 'created_by_name'
        ]


class InvitePublicValidateSerializer(serializers.Serializer):
    """Serializer para validação pública de convites"""
    token = serializers.CharField(max_length=64)
    security_code = serializers.CharField(max_length=8)
    
    def validate(self, attrs):
        print(f"🔍 DEBUG: InvitePublicValidateSerializer.validate chamado")
        print(f"🔍 DEBUG: Dados recebidos: {attrs}")
        
        token = attrs['token']
        security_code = attrs['security_code']
        
        print(f"🔍 DEBUG: Token: {token}")
        print(f"🔍 DEBUG: Security code: {security_code}")
        
        try:
            invite = UserInvite.objects.get(token=token)
            print(f"✅ DEBUG: Convite encontrado: {invite.id} - {invite.email}")
            print(f"🔍 DEBUG: Status: {invite.status}")
            print(f"🔍 DEBUG: Expira em: {invite.expires_at}")
            print(f"🔍 DEBUG: É expirado: {invite.is_expired}")
        except UserInvite.DoesNotExist:
            print(f"❌ DEBUG: Token não encontrado: {token}")
            raise serializers.ValidationError("Token de convite inválido.")
        
        if invite.status != UserInvite.StatusChoices.PENDING:
            print(f"❌ DEBUG: Status inválido: {invite.status}")
            raise serializers.ValidationError("Este convite não está mais válido.")
        
        if invite.is_expired:
            print(f"❌ DEBUG: Convite expirado")
            invite.expire()  # Marcar como expirado
            raise serializers.ValidationError("Este convite expirou.")
        
        if invite.security_code != security_code:
            print(f"❌ DEBUG: Código de segurança incorreto")
            print(f"🔍 DEBUG: Esperado: {invite.security_code}, Recebido: {security_code}")
            raise serializers.ValidationError("Código de segurança incorreto.")
        
        print(f"✅ DEBUG: Validação bem-sucedida")
        attrs['invite'] = invite
        return attrs


class InviteAcceptSerializer(serializers.Serializer):
    """Serializer para aceitar convite e criar senha"""
    token = serializers.CharField(max_length=64)
    security_code = serializers.CharField(max_length=8)
    password = serializers.CharField(min_length=8, validators=[validate_password])
    password_confirm = serializers.CharField(min_length=8)
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("As senhas não coincidem.")
        
        # Validar o convite
        try:
            invite = UserInvite.objects.get(token=attrs['token'])
        except UserInvite.DoesNotExist:
            raise serializers.ValidationError("Token de convite inválido.")
        
        if invite.status != UserInvite.StatusChoices.PENDING:
            raise serializers.ValidationError("Este convite não está mais válido.")
        
        if invite.is_expired:
            invite.expire()
            raise serializers.ValidationError("Este convite expirou.")
        
        if invite.security_code != attrs['security_code']:
            raise serializers.ValidationError("Código de segurança incorreto.")
        
        attrs['invite'] = invite
        return attrs
    
    def save(self):
        invite = self.validated_data['invite']
        password = self.validated_data['password']
        
        # Criar ou ativar usuário
        user, created = User.objects.get_or_create(
            email=invite.email,
            defaults={
                'username': invite.email.split('@')[0],
                'first_name': invite.full_name.split()[0],
                'last_name': ' '.join(invite.full_name.split()[1:]) if len(invite.full_name.split()) > 1 else '',
                'role': invite.role_code,
                'sector': invite.sector_code,
                'is_active': True,
            }
        )
        
        if not created:
            # Usuário já existe, atualizar dados
            user.first_name = invite.full_name.split()[0]
            user.last_name = ' '.join(invite.full_name.split()[1:]) if len(invite.full_name.split()) > 1 else ''
            user.role = invite.role_code
            user.sector = invite.sector_code
            user.is_active = True
        
        # Definir senha
        user.set_password(password)
        user.save()
        
        # Marcar convite como aceito
        invite.accept()
        
        return user
