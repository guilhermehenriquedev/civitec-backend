from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Popula o banco de dados com dados de demonstração para o CiviTec'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando seed do banco de dados...')
        
        # Criar usuários de demonstração
        self.create_demo_users()
        
        # Criar dados de RH
        self.create_rh_data()
        
        # Criar dados de Tributos
        self.create_tributos_data()
        
        # Criar dados de Licitação
        self.create_licitacao_data()
        
        # Criar dados de Obras
        self.create_obras_data()
        
        self.stdout.write(
            self.style.SUCCESS('Seed concluído com sucesso!')
        )
        self.stdout.write('Usuários criados:')
        self.stdout.write('- master@civitec.local (senha: master123) - MASTER_ADMIN')
        self.stdout.write('- admin.rh@civitec.local (senha: admin123) - SECTOR_ADMIN RH')
        self.stdout.write('- operator.rh@civitec.local (senha: operator123) - SECTOR_OPERATOR RH')
        self.stdout.write('- admin.tributos@civitec.local (senha: admin123) - SECTOR_ADMIN TRIBUTOS')
        self.stdout.write('- operator.tributos@civitec.local (senha: operator123) - SECTOR_OPERATOR TRIBUTOS')
        self.stdout.write('- admin.licitacao@civitec.local (senha: admin123) - SECTOR_ADMIN LICITACAO')
        self.stdout.write('- operator.licitacao@civitec.local (senha: operator123) - SECTOR_OPERATOR LICITACAO')
        self.stdout.write('- admin.obras@civitec.local (senha: admin123) - SECTOR_ADMIN OBRAS')
        self.stdout.write('- operator.obras@civitec.local (senha: operator123) - SECTOR_OPERATOR OBRAS')
        self.stdout.write('- funcionario@civitec.local (senha: funcionario123) - EMPLOYEE')

    def create_demo_users(self):
        """Cria usuários de demonstração com diferentes roles"""
        self.stdout.write('Criando usuários de demonstração...')
        
        # Usuário MASTER_ADMIN
        master_user, created = User.objects.get_or_create(
            email='master@civitec.local',
            defaults={
                'username': 'master',
                'first_name': 'Administrador',
                'last_name': 'Master',
                'role': User.RoleChoices.MASTER_ADMIN,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            master_user.set_password('master123')
            master_user.save()
            self.stdout.write('✓ Usuário MASTER criado')
        
        # Usuários SECTOR_ADMIN
        sector_admins = [
            ('admin.rh@civitec.local', 'Admin RH', 'RH'),
            ('admin.tributos@civitec.local', 'Admin Tributos', 'TRIBUTOS'),
            ('admin.licitacao@civitec.local', 'Admin Licitação', 'LICITACAO'),
            ('admin.obras@civitec.local', 'Admin Obras', 'OBRAS'),
        ]
        
        for email, name, sector in sector_admins:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email.split('@')[0],
                    'first_name': name,
                    'last_name': '',
                    'role': User.RoleChoices.SECTOR_ADMIN,
                    'sector': sector,
                    'is_staff': True,
                }
            )
            if created:
                user.set_password('admin123')
                user.save()
                self.stdout.write(f'✓ Usuário {name} criado')
        
        # Usuários SECTOR_OPERATOR
        sector_operators = [
            ('operator.rh@civitec.local', 'Operator RH', 'RH'),
            ('operator.tributos@civitec.local', 'Operator Tributos', 'TRIBUTOS'),
            ('operator.licitacao@civitec.local', 'Operator Licitação', 'LICITACAO'),
            ('operator.obras@civitec.local', 'Operator Obras', 'OBRAS'),
        ]
        
        for email, name, sector in sector_operators:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email.split('@')[0],
                    'first_name': name,
                    'last_name': '',
                    'role': User.RoleChoices.SECTOR_OPERATOR,
                    'sector': sector,
                }
            )
            if created:
                user.set_password('operator123')
                user.save()
                self.stdout.write(f'✓ Usuário {name} criado')
        
        # Usuário EMPLOYEE
        employee_user, created = User.objects.get_or_create(
            email='funcionario@civitec.local',
            defaults={
                'username': 'funcionario',
                'first_name': 'João',
                'last_name': 'Silva',
                'role': User.RoleChoices.EMPLOYEE,
                'sector': 'RH',
            }
        )
        if created:
            employee_user.set_password('funcionario123')
            employee_user.save()
            self.stdout.write('✓ Usuário EMPLOYEE criado')

    def create_rh_data(self):
        """Cria dados de demonstração para RH"""
        self.stdout.write('Criando dados de RH...')
        
        try:
            from rh.models import Employee, VacationRequest, Payslip
            
            # Criar funcionário
            employee_user = User.objects.get(email='funcionario@civitec.local')
            employee, created = Employee.objects.get_or_create(
                user=employee_user,
                defaults={
                    'matricula': 'EMP001',
                    'cargo': 'Analista Administrativo',
                    'lotacao': 'Secretaria de Administração',
                    'regime': Employee.RegimeChoices.CLT,
                    'admissao_dt': date(2023, 1, 15),
                    'status': Employee.StatusChoices.ATIVO,
                }
            )
            if created:
                self.stdout.write('✓ Funcionário criado')
            
            # Criar solicitação de férias
            vacation_request, created = VacationRequest.objects.get_or_create(
                employee=employee,
                period_start=date(2024, 7, 1),
                defaults={
                    'period_end': date(2024, 7, 15),
                    'days_requested': 15,
                    'reason': 'Férias anuais',
                    'status': VacationRequest.StatusChoices.PENDING,
                }
            )
            if created:
                self.stdout.write('✓ Solicitação de férias criada')
            
            # Criar contracheques
            for month in range(1, 13):
                competencia = date(2024, month, 1)
                payslip, created = Payslip.objects.get_or_create(
                    employee=employee,
                    competencia=competencia,
                    defaults={
                        'bruto': Decimal('3500.00'),
                        'descontos': Decimal('500.00'),
                        'liquido': Decimal('3000.00'),
                    }
                )
                if created:
                    self.stdout.write(f'✓ Contracheque {month}/2024 criado')
                    
        except ImportError:
            self.stdout.write('⚠ Módulo RH não disponível')

    def create_tributos_data(self):
        """Cria dados de demonstração para Tributos"""
        self.stdout.write('Criando dados de Tributos...')
        
        try:
            from tributos.models import Taxpayer, Invoice, Assessment, Billing
            
            # Criar contribuintes
            taxpayers_data = [
                ('João da Silva', '123.456.789-00', 'PF', 'Rua A, 123 - Centro'),
                ('Empresa ABC Ltda', '12.345.678/0001-90', 'PJ', 'Av. B, 456 - Jardim'),
                ('Maria Santos', '987.654.321-00', 'PF', 'Rua C, 789 - Vila'),
            ]
            
            for name, doc, type_, address in taxpayers_data:
                taxpayer, created = Taxpayer.objects.get_or_create(
                    doc=doc,
                    defaults={
                        'name': name,
                        'type': type_,
                        'address': address,
                        'phone': '(11) 99999-9999',
                        'email': f'{name.lower().replace(" ", ".")}@email.com',
                    }
                )
                if created:
                    self.stdout.write(f'✓ Contribuinte {name} criado')
            
            # Criar notas fiscais
            for i, taxpayer in enumerate(Taxpayer.objects.all()[:2]):
                invoice, created = Invoice.objects.get_or_create(
                    number=f'NF{i+1:03d}',
                    defaults={
                        'taxpayer': taxpayer,
                        'issue_dt': date(2024, random.randint(1, 12), random.randint(1, 28)),
                        'service_code': f'SVC{i+1:03d}',
                        'description': f'Serviço de consultoria {i+1}',
                        'amount': Decimal(f'{random.randint(100, 1000)}.00'),
                        'status': Invoice.StatusChoices.EMITIDA,
                    }
                )
                if created:
                    self.stdout.write(f'✓ Nota fiscal {invoice.number} criada')
            
            # Criar avaliações
            for taxpayer in Taxpayer.objects.all():
                for tax_kind in ['ISS', 'IPTU']:
                    assessment, created = Assessment.objects.get_or_create(
                        taxpayer=taxpayer,
                        tax_kind=tax_kind,
                        competence=date(2024, 12, 1),
                        defaults={
                            'principal': Decimal(f'{random.randint(50, 200)}.00'),
                            'multa': Decimal('0.00'),
                            'juros': Decimal('0.00'),
                            'status': Assessment.StatusChoices.PENDENTE,
                        }
                    )
                    if created:
                        self.stdout.write(f'✓ Avaliação {tax_kind} para {taxpayer.name} criada')
                        
        except ImportError:
            self.stdout.write('⚠ Módulo Tributos não disponível')

    def create_licitacao_data(self):
        """Cria dados de demonstração para Licitação"""
        self.stdout.write('Criando dados de Licitação...')
        
        try:
            from licitacao.models import Procurement, ProcPhase, Proposal, Award, Contract
            
            # Criar processo de licitação
            procurement, created = Procurement.objects.get_or_create(
                numero_processo='LIC001/2024',
                defaults={
                    'modalidade': Procurement.ModalidadeChoices.PREGAO,
                    'objeto': 'Aquisição de equipamentos de informática',
                    'valor_estimado': Decimal('50000.00'),
                    'status': Procurement.StatusChoices.ABERTA,
                    'data_abertura': date(2024, 6, 1),
                    'data_encerramento': date(2024, 8, 1),
                }
            )
            if created:
                self.stdout.write('✓ Processo de licitação criado')
            
            # Criar fases
            phases_data = [
                ('PUBLICACAO', date(2024, 6, 1), date(2024, 6, 15)),
                ('INSCRICAO', date(2024, 6, 16), date(2024, 7, 15)),
                ('PROPOSTAS', date(2024, 7, 16), date(2024, 7, 31)),
            ]
            
            for fase, start_dt, end_dt in phases_data:
                phase, created = ProcPhase.objects.get_or_create(
                    procurement=procurement,
                    fase=fase,
                    defaults={
                        'start_dt': timezone.make_aware(timezone.datetime.combine(start_dt, timezone.datetime.min.time())),
                        'end_dt': timezone.make_aware(timezone.datetime.combine(end_dt, timezone.datetime.min.time())),
                        'status': ProcPhase.StatusChoices.CONCLUIDA if fase != 'PROPOSTAS' else ProcPhase.StatusChoices.EM_ANDAMENTO,
                    }
                )
                if created:
                    self.stdout.write(f'✓ Fase {fase} criada')
            
            # Criar propostas
            suppliers = [
                ('Tech Solutions Ltda', '12.345.678/0001-91'),
                ('Inovação Digital SA', '98.765.432/0001-10'),
                ('Sistemas Avançados', '11.222.333/0001-44'),
            ]
            
            for i, (name, doc) in enumerate(suppliers):
                proposal, created = Proposal.objects.get_or_create(
                    procurement=procurement,
                    supplier_doc=doc,
                    defaults={
                        'supplier_name': name,
                        'valor': Decimal(f'{random.randint(45000, 55000)}.00'),
                        'classificacao': i + 1,
                        'status': Proposal.StatusChoices.CLASSIFICADA,
                    }
                )
                if created:
                    self.stdout.write(f'✓ Proposta de {name} criada')
            
            # Criar adjudicação
            winning_proposal = Proposal.objects.filter(procurement=procurement).first()
            if winning_proposal:
                award, created = Award.objects.get_or_create(
                    procurement=procurement,
                    defaults={
                        'supplier': winning_proposal,
                        'valor_adjudicado': winning_proposal.valor,
                        'homolog_dt': timezone.now(),
                    }
                )
                if created:
                    self.stdout.write('✓ Adjudicação criada')
                    
        except ImportError:
            self.stdout.write('⚠ Módulo Licitação não disponível')

    def create_obras_data(self):
        """Cria dados de demonstração para Obras"""
        self.stdout.write('Criando dados de Obras...')
        
        try:
            from obras.models import WorkProject, WorkProgress
            
            # Criar obras
            obras_data = [
                ('Reforma da Praça Central', 'Reforma completa da praça central da cidade', Decimal('150000.00'), -23.5505, -46.6333),
                ('Construção de Escola', 'Nova escola municipal com 10 salas de aula', Decimal('800000.00'), -23.5600, -46.6400),
                ('Asfaltamento de Rua', 'Asfaltamento de 2km de rua residencial', Decimal('300000.00'), -23.5400, -46.6200),
            ]
            
            for name, description, budget, lat, lng in obras_data:
                project, created = WorkProject.objects.get_or_create(
                    name=name,
                    defaults={
                        'description': description,
                        'budget': budget,
                        'status': WorkProject.StatusChoices.EXECUCAO,
                        'start_date': date(2024, 3, 1),
                        'expected_end_date': date(2024, 12, 31),
                        'responsible': 'Eng. Carlos Silva',
                        'address': 'Endereço da obra',
                        'location_lat': lat,
                        'location_lng': lng,
                    }
                )
                if created:
                    self.stdout.write(f'✓ Obra {name} criada')
                
                # Criar progressos mensais
                for month in range(3, 13):
                    ref_month = date(2024, month, 1)
                    progress, created = WorkProgress.objects.get_or_create(
                        project=project,
                        ref_month=ref_month,
                        defaults={
                            'physical_pct': Decimal(f'{min(90, (month - 2) * 10)}.00'),
                            'financial_pct': Decimal(f'{min(85, (month - 2) * 9)}.00'),
                            'notes': f'Progresso do mês {month}/2024',
                        }
                    )
                    if created:
                        self.stdout.write(f'✓ Progresso {month}/2024 para {name} criado')
                        
        except ImportError:
            self.stdout.write('⚠ Módulo Obras não disponível')
