from django.shortcuts import render
from rest_framework import viewsets
from .models import Taxpayer, Invoice, Assessment, Billing
from .serializers import TaxpayerSerializer, InvoiceSerializer, AssessmentSerializer, BillingSerializer
from users.permissions import IsSectorAdmin, IsSectorOperator


# Create your views here.


class TaxpayerViewSet(viewsets.ModelViewSet):
    """ViewSet para contribuintes"""
    queryset = Taxpayer.objects.all()
    serializer_class = TaxpayerSerializer
    permission_classes = [IsSectorAdmin]
    sector = 'TRIBUTOS'


class InvoiceViewSet(viewsets.ModelViewSet):
    """ViewSet para notas fiscais"""
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsSectorAdmin]
    sector = 'TRIBUTOS'


class AssessmentViewSet(viewsets.ModelViewSet):
    """ViewSet para avaliações/guias"""
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    permission_classes = [IsSectorAdmin]
    sector = 'TRIBUTOS'


class BillingViewSet(viewsets.ModelViewSet):
    """ViewSet para cobranças"""
    queryset = Billing.objects.all()
    serializer_class = BillingSerializer
    permission_classes = [IsSectorAdmin]
    sector = 'TRIBUTOS'
