from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from tributos.models import Taxpayer, Invoice, Assessment, Billing
import random


class Command(BaseCommand):
    help = 'Popula a base de dados com dados de demonstração para Tributos'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando população de dados de Tributos...'))

        # Criar contribuintes
        taxpayers_data = [
            {
                'name': 'João Silva',
                'doc': '123.456.789-00',
                'type': 'PF',
                'address': 'Rua das Flores, 123 - Centro',
                'phone': '(11) 98765-4321',
                'email': 'joao@email.com',
                'is_active': True
            },
            {
                'name': 'Maria Santos',
                'doc': '987.654.321-00',
                'type': 'PF',
                'address': 'Av. Principal, 456 - Jardim',
                'phone': '(11) 99876-5432',
                'email': 'maria@email.com',
                'is_active': True
            },
            {
                'name': 'Empresa ABC Ltda',
                'doc': '12.345.678/0001-90',
                'type': 'PJ',
                'address': 'Rua do Comércio, 789 - Centro',
                'phone': '(11) 3456-7890',
                'email': 'contato@empresaabc.com',
                'is_active': True
            },
            {
                'name': 'Tech Solutions ME',
                'doc': '98.765.432/0001-10',
                'type': 'PJ',
                'address': 'Av. Tecnologia, 321 - Distrito Industrial',
                'phone': '(11) 3789-0123',
                'email': 'info@techsolutions.com',
                'is_active': True
            },
            {
                'name': 'Carlos Oliveira',
                'doc': '456.789.123-00',
                'type': 'PF',
                'address': 'Rua da Paz, 654 - Vila Nova',
                'phone': '(11) 97654-3210',
                'email': 'carlos@email.com',
                'is_active': True
            }
        ]

        created_taxpayers = []
        for taxpayer_data in taxpayers_data:
            taxpayer, created = Taxpayer.objects.get_or_create(
                doc=taxpayer_data['doc'],
                defaults=taxpayer_data
            )
            if created:
                self.stdout.write(f'Contribuinte criado: {taxpayer.name}')
            created_taxpayers.append(taxpayer)

        # Criar notas fiscais
        service_codes = ['01.01.01', '01.02.01', '02.01.01', '03.03.01', '05.02.01']
        invoice_statuses = ['EMITIDA', 'CANCELADA', 'PAGA']

        for i in range(1, 16):  # 15 notas fiscais
            taxpayer = random.choice(created_taxpayers)
            invoice_data = {
                'taxpayer': taxpayer,
                'number': f'NF{i:03d}/2024',
                'issue_dt': timezone.now().date(),
                'service_code': random.choice(service_codes),
                'description': f'Prestação de serviços - Nota Fiscal {i:03d}',
                'amount': Decimal(random.randint(100, 5000)),
                'status': random.choice(invoice_statuses)
            }
            
            invoice, created = Invoice.objects.get_or_create(
                number=invoice_data['number'],
                defaults=invoice_data
            )
            if created:
                self.stdout.write(f'Nota Fiscal criada: {invoice.number}')

        # Criar avaliações
        tax_kinds = ['ISS', 'IPTU', 'ITBI', 'OUTROS']
        assessment_statuses = ['PENDENTE', 'EMITIDA', 'PAGA', 'VENCIDA']

        for i in range(1, 21):  # 20 avaliações
            taxpayer = random.choice(created_taxpayers)
            principal = Decimal(random.randint(50, 2000))
            multa = Decimal(random.randint(0, 200))
            juros = Decimal(random.randint(0, 100))
            
            assessment_data = {
                'taxpayer': taxpayer,
                'tax_kind': random.choice(tax_kinds),
                'competence': timezone.now().date(),
                'principal': principal,
                'multa': multa,
                'juros': juros,
                'total': principal + multa + juros,
                'status': random.choice(assessment_statuses)
            }
            
            assessment = Assessment.objects.create(**assessment_data)
            self.stdout.write(f'Avaliação criada: {assessment.tax_kind} - {assessment.taxpayer.name}')

            # Criar cobrança para algumas avaliações
            if random.choice([True, False]):
                billing_data = {
                    'assessment': assessment,
                    'due_dt': timezone.now().date(),
                    'barcode': f'DAM-{assessment.tax_kind}-{i:06d}',
                    'amount': assessment.total,
                    'status': random.choice(['PENDENTE', 'PAGO', 'VENCIDO'])
                }
                
                billing = Billing.objects.create(**billing_data)
                self.stdout.write(f'Cobrança criada: {billing.barcode}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Dados de demonstração criados com sucesso!\n'
                f'- Contribuintes: {len(created_taxpayers)}\n'
                f'- Notas Fiscais: 15\n'
                f'- Avaliações: 20\n'
            )
        )

