from rest_framework import serializers
from .models import Procurement, ProcPhase, Proposal, Award, Contract, ContractMilestone


class ProcurementSerializer(serializers.ModelSerializer):
    """Serializer para processos de licitação"""
    
    class Meta:
        model = Procurement
        fields = '__all__'


class ProcPhaseSerializer(serializers.ModelSerializer):
    """Serializer para fases do processo"""
    
    class Meta:
        model = ProcPhase
        fields = '__all__'


class ProposalSerializer(serializers.ModelSerializer):
    """Serializer para propostas"""
    
    class Meta:
        model = Proposal
        fields = '__all__'


class AwardSerializer(serializers.ModelSerializer):
    """Serializer para adjudicações"""
    
    class Meta:
        model = Award
        fields = '__all__'


class ContractSerializer(serializers.ModelSerializer):
    """Serializer para contratos"""
    
    class Meta:
        model = Contract
        fields = '__all__'


class ContractMilestoneSerializer(serializers.ModelSerializer):
    """Serializer para marcos do contrato"""
    
    class Meta:
        model = ContractMilestone
        fields = '__all__'
