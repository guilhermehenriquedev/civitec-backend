from rest_framework import serializers
from django.utils import timezone
from .models import Taxpayer, Invoice, Assessment, Billing
import re


class TaxpayerSerializer(serializers.ModelSerializer):
    """Serializer para contribuintes"""
    
    class Meta:
        model = Taxpayer
        fields = '__all__'
    
    def validate_doc(self, value):
        """Valida CPF/CNPJ"""
        # Remove caracteres especiais
        doc = re.sub(r'[^\d]', '', value)
        
        if len(doc) == 11:  # CPF
            if not self._validate_cpf(doc):
                raise serializers.ValidationError("CPF inválido")
        elif len(doc) == 14:  # CNPJ
            if not self._validate_cnpj(doc):
                raise serializers.ValidationError("CNPJ inválido")
        else:
            raise serializers.ValidationError("Documento deve ter 11 (CPF) ou 14 (CNPJ) dígitos")
        
        return value
    
    def _validate_cpf(self, cpf):
        """Valida CPF"""
        if len(set(cpf)) == 1:
            return False
        
        # Validação dos dígitos verificadores
        for i in range(9, 11):
            value = sum((int(cpf[num]) * ((i + 1) - num) for num in range(0, i)))
            digit = ((value * 10) % 11) % 10
            if int(cpf[i]) != digit:
                return False
        return True
    
    def _validate_cnpj(self, cnpj):
        """Valida CNPJ"""
        if len(set(cnpj)) == 1:
            return False
        
        # Validação dos dígitos verificadores
        for i in range(12, 14):
            value = sum((int(cnpj[num]) * (2 if (i + 1 - num) % 2 == 0 else 1) for num in range(0, i)))
            digit = ((value * 10) % 11) % 10
            if int(cnpj[i]) != digit:
                return False
        return True
    
    def validate(self, attrs):
        """Validações customizadas"""
        doc_type = attrs.get('type')
        doc = attrs.get('doc')
        
        if doc and doc_type:
            doc_clean = re.sub(r'[^\d]', '', doc)
            if doc_type == 'PF' and len(doc_clean) != 11:
                raise serializers.ValidationError("Pessoa Física deve ter CPF com 11 dígitos")
            elif doc_type == 'PJ' and len(doc_clean) != 14:
                raise serializers.ValidationError("Pessoa Jurídica deve ter CNPJ com 14 dígitos")
        
        return attrs


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer para notas fiscais"""
    taxpayer_name = serializers.CharField(source='taxpayer.name', read_only=True)
    taxpayer_doc = serializers.CharField(source='taxpayer.doc', read_only=True)
    
    class Meta:
        model = Invoice
        fields = '__all__'
    
    def validate_amount(self, value):
        """Valida valor da nota fiscal"""
        if value <= 0:
            raise serializers.ValidationError("Valor deve ser maior que zero")
        return value
    
    def validate_number(self, value):
        """Valida número da nota fiscal"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Número da nota fiscal é obrigatório")
        return value.strip()
    
    def validate(self, attrs):
        """Validações customizadas"""
        issue_dt = attrs.get('issue_dt')
        if issue_dt and issue_dt > timezone.now().date():
            raise serializers.ValidationError("Data de emissão não pode ser futura")
        
        return attrs


class AssessmentSerializer(serializers.ModelSerializer):
    """Serializer para avaliações/guias"""
    taxpayer_name = serializers.CharField(source='taxpayer.name', read_only=True)
    taxpayer_doc = serializers.CharField(source='taxpayer.doc', read_only=True)
    
    class Meta:
        model = Assessment
        fields = '__all__'
    
    def validate_principal(self, value):
        """Valida valor principal"""
        if value <= 0:
            raise serializers.ValidationError("Valor principal deve ser maior que zero")
        return value
    
    def validate_multa(self, value):
        """Valida multa"""
        if value < 0:
            raise serializers.ValidationError("Multa não pode ser negativa")
        return value
    
    def validate_juros(self, value):
        """Valida juros"""
        if value < 0:
            raise serializers.ValidationError("Juros não podem ser negativos")
        return value
    
    def validate(self, attrs):
        """Validações customizadas"""
        competence = attrs.get('competence')
        if competence and competence > timezone.now().date():
            raise serializers.ValidationError("Competência não pode ser futura")
        
        return attrs


class BillingSerializer(serializers.ModelSerializer):
    """Serializer para cobranças"""
    
    class Meta:
        model = Billing
        fields = '__all__'
