from django.shortcuts import render
from rest_framework import viewsets
from .models import Procurement, ProcPhase, Proposal, Award, Contract, ContractMilestone
from .serializers import (
    ProcurementSerializer, ProcPhaseSerializer, ProposalSerializer, 
    AwardSerializer, ContractSerializer, ContractMilestoneSerializer
)
from users.permissions import IsSectorAdmin, IsSectorOperator


# Create your views here.


class ProcurementViewSet(viewsets.ModelViewSet):
    """ViewSet para processos de licitação"""
    queryset = Procurement.objects.all()
    serializer_class = ProcurementSerializer
    permission_classes = [IsSectorAdmin]
    sector = 'LICITACAO'


class ProcPhaseViewSet(viewsets.ModelViewSet):
    """ViewSet para fases do processo"""
    queryset = ProcPhase.objects.all()
    serializer_class = ProcPhaseSerializer
    permission_classes = [IsSectorAdmin]
    sector = 'LICITACAO'


class ProposalViewSet(viewsets.ModelViewSet):
    """ViewSet para propostas"""
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer
    permission_classes = [IsSectorAdmin]
    sector = 'LICITACAO'


class AwardViewSet(viewsets.ModelViewSet):
    """ViewSet para adjudicações"""
    queryset = Award.objects.all()
    serializer_class = AwardSerializer
    permission_classes = [IsSectorAdmin]
    sector = 'LICITACAO'


class ContractViewSet(viewsets.ModelViewSet):
    """ViewSet para contratos"""
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    permission_classes = [IsSectorAdmin]
    sector = 'LICITACAO'


class ContractMilestoneViewSet(viewsets.ModelViewSet):
    """ViewSet para marcos do contrato"""
    queryset = ContractMilestone.objects.all()
    serializer_class = ContractMilestoneSerializer
    permission_classes = [IsSectorAdmin]
    sector = 'LICITACAO'
