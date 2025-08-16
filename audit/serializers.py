from rest_framework import serializers
from .models import AuditLog
from users.serializers import UserSerializer


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer para logs de auditoria"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'action', 'entity', 'entity_id', 'payload_json',
            'ip_address', 'user_agent', 'url', 'method', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
