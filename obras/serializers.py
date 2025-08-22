from rest_framework import serializers
from .models import WorkProject, WorkProgress, WorkPhoto
from licitacao.serializers import ContractSerializer


class WorkPhotoSerializer(serializers.ModelSerializer):
    """Serializer para fotos das obras"""
    
    class Meta:
        model = WorkPhoto
        fields = ['id', 'title', 'description', 'photo', 'taken_date', 'location', 'created_at']


class WorkProgressSerializer(serializers.ModelSerializer):
    """Serializer para progresso das obras"""
    
    class Meta:
        model = WorkProgress
        fields = ['id', 'ref_month', 'physical_pct', 'financial_pct', 'notes', 'created_at', 'updated_at']


class WorkProjectSerializer(serializers.ModelSerializer):
    """Serializer para obras/projetos"""
    
    contract_details = ContractSerializer(source='contract', read_only=True)
    progress_set = WorkProgressSerializer(many=True, read_only=True)
    photos = WorkPhotoSerializer(many=True, read_only=True)
    progress_physical = serializers.ReadOnlyField()
    progress_financial = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = WorkProject
        fields = [
            'id', 'name', 'contract', 'contract_details', 'location_lat', 'location_lng', 
            'address', 'budget', 'status', 'status_display', 'start_date', 'expected_end_date',
            'actual_end_date', 'description', 'responsible', 'progress_set', 'photos',
            'progress_physical', 'progress_financial', 'created_at', 'updated_at'
        ]


class WorkProjectCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para criação e atualização de obras/projetos"""
    
    class Meta:
        model = WorkProject
        fields = [
            'name', 'contract', 'location_lat', 'location_lng', 'address', 'budget',
            'status', 'start_date', 'expected_end_date', 'actual_end_date', 'description', 'responsible'
        ]


class WorkProgressCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para criação e atualização de progresso"""
    
    class Meta:
        model = WorkProgress
        fields = ['project', 'ref_month', 'physical_pct', 'financial_pct', 'notes']


class WorkPhotoCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para criação e atualização de fotos"""
    
    class Meta:
        model = WorkPhoto
        fields = ['project', 'title', 'description', 'photo', 'taken_date', 'location']


class ObrasDashboardSerializer(serializers.Serializer):
    """Serializer para dashboard de obras"""
    
    total_projects = serializers.IntegerField()
    projects_in_execution = serializers.IntegerField()
    average_progress = serializers.DecimalField(max_digits=5, decimal_places=2)
    total_budget = serializers.DecimalField(max_digits=15, decimal_places=2)
    projects_by_status = serializers.DictField()
    recent_progress = serializers.ListField()
