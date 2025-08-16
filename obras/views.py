from django.shortcuts import render
from rest_framework import viewsets
from .models import WorkProject, WorkProgress, WorkPhoto
from .serializers import WorkProjectSerializer, WorkProgressSerializer, WorkPhotoSerializer
from users.permissions import IsSectorAdmin, IsSectorOperator


# Create your views here.


class WorkProjectViewSet(viewsets.ModelViewSet):
    """ViewSet para obras/projetos"""
    queryset = WorkProject.objects.all()
    serializer_class = WorkProjectSerializer
    permission_classes = [IsSectorAdmin]
    sector = 'OBRAS'


class WorkProgressViewSet(viewsets.ModelViewSet):
    """ViewSet para progresso das obras"""
    queryset = WorkProgress.objects.all()
    serializer_class = WorkProgressSerializer
    permission_classes = [IsSectorAdmin]
    sector = 'OBRAS'


class WorkPhotoViewSet(viewsets.ModelViewSet):
    """ViewSet para fotos das obras"""
    queryset = WorkPhoto.objects.all()
    serializer_class = WorkPhotoSerializer
    permission_classes = [IsSectorAdmin]
    sector = 'OBRAS'
