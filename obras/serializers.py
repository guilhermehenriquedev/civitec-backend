from rest_framework import serializers
from .models import WorkProject, WorkProgress, WorkPhoto


class WorkProjectSerializer(serializers.ModelSerializer):
    """Serializer para obras/projetos"""
    
    class Meta:
        model = WorkProject
        fields = '__all__'


class WorkProgressSerializer(serializers.ModelSerializer):
    """Serializer para progresso das obras"""
    
    class Meta:
        model = WorkProgress
        fields = '__all__'


class WorkPhotoSerializer(serializers.ModelSerializer):
    """Serializer para fotos das obras"""
    
    class Meta:
        model = WorkPhoto
        fields = '__all__'
