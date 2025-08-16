from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import AuditLog
from .serializers import AuditLogSerializer
from users.permissions import IsMasterAdmin


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para logs de auditoria (somente leitura)"""
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsMasterAdmin]  # Apenas MASTER_ADMIN pode ver logs
    
    def get_queryset(self):
        """Filtrar logs baseado nos parâmetros da requisição"""
        queryset = AuditLog.objects.all()
        
        # Filtros opcionais
        user_id = self.request.query_params.get('user_id', None)
        action_type = self.request.query_params.get('action', None)
        entity = self.request.query_params.get('entity', None)
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        if action_type:
            queryset = queryset.filter(action=action_type)
        
        if entity:
            queryset = queryset.filter(entity=entity)
        
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
        
        return queryset.order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Resumo dos logs de auditoria"""
        if not request.user.is_master_admin:
            return Response({'error': 'Acesso negado'}, status=403)
        
        from django.db.models import Count
        from django.utils import timezone
        from datetime import timedelta
        
        # Estatísticas dos últimos 30 dias
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        summary_data = {
            'total_logs': AuditLog.objects.count(),
            'logs_last_30_days': AuditLog.objects.filter(created_at__gte=thirty_days_ago).count(),
            'actions_summary': AuditLog.objects.values('action').annotate(count=Count('action')).order_by('-count'),
            'entities_summary': AuditLog.objects.values('entity').annotate(count=Count('entity')).order_by('-count'),
            'users_summary': AuditLog.objects.values('user__email').annotate(count=Count('user')).order_by('-count')[:10],
        }
        
        return Response(summary_data)
    
    @action(detail=False, methods=['get'])
    def user_activity(self, request):
        """Atividade de um usuário específico"""
        if not request.user.is_master_admin:
            return Response({'error': 'Acesso negado'}, status=403)
        
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': 'user_id é obrigatório'}, status=400)
        
        user_logs = AuditLog.objects.filter(user_id=user_id).order_by('-created_at')[:100]
        serializer = self.get_serializer(user_logs, many=True)
        
        return Response({
            'user_id': user_id,
            'total_actions': AuditLog.objects.filter(user_id=user_id).count(),
            'recent_actions': serializer.data,
        })
