from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Count, Sum, Q
from django.utils import timezone
from datetime import datetime
from .models import WorkProject, WorkProgress, WorkPhoto
from .serializers import (
    WorkProjectSerializer, WorkProjectCreateUpdateSerializer,
    WorkProgressSerializer, WorkProgressCreateUpdateSerializer,
    WorkPhotoSerializer, WorkPhotoCreateUpdateSerializer,
    ObrasDashboardSerializer
)
from users.permissions import IsSectorAdmin, IsSectorOperator
from audit.models import AuditLog


# Create your views here.


class WorkProjectViewSet(viewsets.ModelViewSet):
    """ViewSet para obras/projetos"""
    queryset = WorkProject.objects.all()
    serializer_class = WorkProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    sector = 'OBRAS'
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return WorkProjectCreateUpdateSerializer
        return WorkProjectSerializer
    
    def get_queryset(self):
        """Filtrar por setor baseado no usuário"""
        user = self.request.user
        
        # MASTER_ADMIN vê tudo
        if user.is_master_admin:
            return WorkProject.objects.all()
        
        # SECTOR_ADMIN e SECTOR_OPERATOR vêem apenas do seu setor
        if user.is_sector_admin or user.is_sector_operator:
            if user.sector == 'OBRAS':
                return WorkProject.objects.all()
            return WorkProject.objects.none()
        
        # EMPLOYEE vê apenas projetos ativos
        if user.is_employee:
            return WorkProject.objects.filter(status__in=['PLANEJAMENTO', 'EXECUCAO'])
        
        return WorkProject.objects.none()
    
    def perform_create(self, serializer):
        """Criar projeto e registrar auditoria"""
        project = serializer.save()
        
        # Registrar auditoria
        AuditLog.log_action(
            user=self.request.user,
            action='CREATE',
            obj=project,
            payload={'action': 'create_project'},
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT'),
            url=self.request.path,
            method=self.request.method
        )
    
    def perform_update(self, serializer):
        """Atualizar projeto e registrar auditoria"""
        project = serializer.save()
        
        # Registrar auditoria
        AuditLog.log_action(
            user=self.request.user,
            action='UPDATE',
            obj=project,
            payload={'action': 'update_project'},
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT'),
            url=self.request.path,
            method=self.request.method
        )
    
    def perform_destroy(self, instance):
        """Exclusão lógica e auditoria"""
        # Marcar como cancelado em vez de deletar
        instance.status = 'CANCELADA'
        instance.save()
        
        # Registrar auditoria
        AuditLog.log_action(
            user=self.request.user,
            action='DELETE',
            obj=instance,
            payload={'action': 'delete_project', 'status_changed_to': 'CANCELADA'},
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT'),
            url=self.request.path,
            method=self.request.method
        )
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Endpoint para dashboard de obras"""
        user = request.user
        
        # Verificar permissões
        if not (user.is_master_admin or 
                (user.is_sector_admin and user.sector == 'OBRAS') or
                (user.is_sector_operator and user.sector == 'OBRAS') or
                user.is_employee):
            return Response({'error': 'Acesso negado'}, status=status.HTTP_403_FORBIDDEN)
        
        # Calcular estatísticas
        queryset = self.get_queryset()
        
        total_projects = queryset.count()
        projects_in_execution = queryset.filter(status='EXECUCAO').count()
        
        # Calcular progresso médio
        progress_avg = queryset.aggregate(
            avg_progress=Avg('progress_set__physical_pct')
        )['avg_progress'] or 0
        
        # Calcular orçamento total
        total_budget = queryset.aggregate(
            total=Sum('budget')
        )['total'] or 0
        
        # Contar projetos por status
        projects_by_status = queryset.values('status').annotate(
            count=Count('id')
        ).order_by('status')
        
        status_dict = {}
        for item in projects_by_status:
            status_dict[item['status']] = item['count']
        
        # Progresso recente (últimos 3 meses)
        recent_progress = WorkProgress.objects.filter(
            project__in=queryset
        ).order_by('-ref_month')[:10]
        
        dashboard_data = {
            'total_projects': total_projects,
            'projects_in_execution': projects_in_execution,
            'average_progress': round(float(progress_avg), 2),
            'total_budget': total_budget,
            'projects_by_status': status_dict,
            'recent_progress': WorkProgressSerializer(recent_progress, many=True).data
        }
        
        serializer = ObrasDashboardSerializer(dashboard_data)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        """Obter progresso de um projeto específico"""
        project = self.get_object()
        progress_list = project.progress_set.all().order_by('-ref_month')
        serializer = WorkProgressSerializer(progress_list, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def photos(self, request, pk=None):
        """Obter fotos de um projeto específico"""
        project = self.get_object()
        photos = project.photos.all().order_by('-taken_date')
        serializer = WorkPhotoSerializer(photos, many=True)
        return Response(serializer.data)


class WorkProgressViewSet(viewsets.ModelViewSet):
    """ViewSet para progresso das obras"""
    queryset = WorkProgress.objects.all()
    serializer_class = WorkProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    sector = 'OBRAS'
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return WorkProgressCreateUpdateSerializer
        return WorkProgressSerializer
    
    def get_queryset(self):
        """Filtrar por setor baseado no usuário"""
        user = self.request.user
        
        # MASTER_ADMIN vê tudo
        if user.is_master_admin:
            return WorkProgress.objects.all()
        
        # SECTOR_ADMIN e SECTOR_OPERATOR vêem apenas do seu setor
        if user.is_sector_admin or user.is_sector_operator:
            if user.sector == 'OBRAS':
                return WorkProgress.objects.all()
            return WorkProgress.objects.none()
        
        # EMPLOYEE vê apenas progresso de projetos ativos
        if user.is_employee:
            return WorkProgress.objects.filter(
                project__status__in=['PLANEJAMENTO', 'EXECUCAO']
            )
        
        return WorkProgress.objects.none()
    
    def perform_create(self, serializer):
        """Criar progresso e registrar auditoria"""
        progress = serializer.save()
        
        # Registrar auditoria
        AuditLog.log_action(
            user=self.request.user,
            action='CREATE',
            obj=progress,
            payload={'action': 'create_progress', 'project_id': progress.project.id},
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT'),
            url=self.request.path,
            method=self.request.method
        )
    
    def perform_update(self, serializer):
        """Atualizar progresso e registrar auditoria"""
        progress = serializer.save()
        
        # Registrar auditoria
        AuditLog.log_action(
            user=self.request.user,
            action='UPDATE',
            obj=progress,
            payload={'action': 'update_progress', 'project_id': progress.project.id},
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT'),
            url=self.request.path,
            method=self.request.method
        )
    
    def perform_destroy(self, instance):
        """Deletar progresso e registrar auditoria"""
        project_id = instance.project.id
        
        # Registrar auditoria antes de deletar
        AuditLog.log_action(
            user=self.request.user,
            action='DELETE',
            obj=instance,
            payload={'action': 'delete_progress', 'project_id': project_id},
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT'),
            url=self.request.path,
            method=self.request.method
        )
        
        instance.delete()


class WorkPhotoViewSet(viewsets.ModelViewSet):
    """ViewSet para fotos das obras"""
    queryset = WorkPhoto.objects.all()
    serializer_class = WorkPhotoSerializer
    permission_classes = [permissions.IsAuthenticated]
    sector = 'OBRAS'
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return WorkPhotoCreateUpdateSerializer
        return WorkPhotoSerializer
    
    def get_queryset(self):
        """Filtrar por setor baseado no usuário"""
        user = self.request.user
        
        # MASTER_ADMIN vê tudo
        if user.is_master_admin:
            return WorkPhoto.objects.all()
        
        # SECTOR_ADMIN e SECTOR_OPERATOR vêem apenas do seu setor
        if user.is_sector_admin or user.is_sector_operator:
            if user.sector == 'OBRAS':
                return WorkPhoto.objects.all()
            return WorkPhoto.objects.none()
        
        # EMPLOYEE vê apenas fotos de projetos ativos
        if user.is_employee:
            return WorkPhoto.objects.filter(
                project__status__in=['PLANEJAMENTO', 'EXECUCAO']
            )
        
        return WorkPhoto.objects.none()
    
    def perform_create(self, serializer):
        """Criar foto e registrar auditoria"""
        photo = serializer.save()
        
        # Registrar auditoria
        AuditLog.log_action(
            user=self.request.user,
            action='UPLOAD',
            obj=photo,
            payload={'action': 'upload_photo', 'project_id': photo.project.id},
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT'),
            url=self.request.path,
            method=self.request.method
        )
    
    def perform_update(self, serializer):
        """Atualizar foto e registrar auditoria"""
        photo = serializer.save()
        
        # Registrar auditoria
        AuditLog.log_action(
            user=self.request.user,
            action='UPDATE',
            obj=photo,
            payload={'action': 'update_photo', 'project_id': photo.project.id},
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT'),
            url=self.request.path,
            method=self.request.method
        )
    
    def perform_destroy(self, instance):
        """Deletar foto e registrar auditoria"""
        project_id = instance.project.id
        
        # Registrar auditoria antes de deletar
        AuditLog.log_action(
            user=self.request.user,
            action='DELETE',
            obj=instance,
            payload={'action': 'delete_photo', 'project_id': project_id},
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT'),
            url=self.request.path,
            method=self.request.method
        )
        
        instance.delete()
