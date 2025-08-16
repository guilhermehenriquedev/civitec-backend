from rest_framework import serializers
from .models import Taxpayer, Invoice, Assessment, Billing


class TaxpayerSerializer(serializers.ModelSerializer):
    """Serializer para contribuintes"""
    
    class Meta:
        model = Taxpayer
        fields = '__all__'


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer para notas fiscais"""
    
    class Meta:
        model = Invoice
        fields = '__all__'


class AssessmentSerializer(serializers.ModelSerializer):
    """Serializer para avaliações/guias"""
    
    class Meta:
        model = Assessment
        fields = '__all__'


class BillingSerializer(serializers.ModelSerializer):
    """Serializer para cobranças"""
    
    class Meta:
        model = Billing
        fields = '__all__'
