from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta
from obras.models import WorkProject, WorkProgress, WorkPhoto
from licitacao.models import Contract
from users.models import User


class Command(BaseCommand):
    help = 'Popula o banco com dados de exemplo de obras'

    def handle(self, *args, **options):
        self.stdout.write('Criando dados de exemplo para obras...')
        
        # Verificar se já existem projetos
        if WorkProject.objects.exists():
            self.stdout.write('Já existem projetos de obras. Pulando criação...')
            return
        
        # Criar projetos de exemplo
        projects_data = [
            {
                'name': 'Construção da Escola Municipal João da Silva',
                'address': 'Rua das Flores, 123 - Centro',
                'location_lat': Decimal('-23.5505'),
                'location_lng': Decimal('-46.6333'),
                'budget': Decimal('2500000.00'),
                'status': 'EXECUCAO',
                'start_date': date(2024, 1, 15),
                'expected_end_date': date(2024, 12, 30),
                'description': 'Construção de escola municipal com 12 salas de aula, biblioteca e quadra esportiva',
                'responsible': 'Eng. Carlos Mendes'
            },
            {
                'name': 'Reforma da Praça Central',
                'address': 'Praça da República, s/n - Centro',
                'location_lat': Decimal('-23.5510'),
                'location_lng': Decimal('-46.6340'),
                'budget': Decimal('800000.00'),
                'status': 'PLANEJAMENTO',
                'start_date': date(2024, 3, 1),
                'expected_end_date': date(2024, 8, 30),
                'description': 'Reforma completa da praça central com nova iluminação, paisagismo e mobiliário urbano',
                'responsible': 'Arq. Ana Paula Santos'
            },
            {
                'name': 'Pavimentação da Rua das Palmeiras',
                'address': 'Rua das Palmeiras - Bairro Jardim',
                'location_lat': Decimal('-23.5490'),
                'location_lng': Decimal('-46.6320'),
                'budget': Decimal('1200000.00'),
                'status': 'EXECUCAO',
                'start_date': date(2024, 2, 1),
                'expected_end_date': date(2024, 7, 30),
                'description': 'Pavimentação asfáltica de 2km de rua com drenagem e iluminação',
                'responsible': 'Eng. Roberto Almeida'
            },
            {
                'name': 'Construção do Posto de Saúde',
                'address': 'Av. Principal, 456 - Bairro São José',
                'location_lat': Decimal('-23.5480'),
                'location_lng': Decimal('-46.6310'),
                'budget': Decimal('1800000.00'),
                'status': 'LICITACAO',
                'start_date': date(2024, 6, 1),
                'expected_end_date': date(2025, 3, 30),
                'description': 'Construção de posto de saúde com 6 consultórios e sala de emergência',
                'responsible': 'Arq. Mariana Costa'
            },
            {
                'name': 'Reforma do Mercado Municipal',
                'address': 'Rua do Comércio, 789 - Centro',
                'location_lat': Decimal('-23.5520'),
                'location_lng': Decimal('-46.6350'),
                'budget': Decimal('950000.00'),
                'status': 'CONCLUIDA',
                'start_date': date(2023, 8, 1),
                'expected_end_date': date(2024, 1, 30),
                'actual_end_date': date(2024, 1, 15),
                'description': 'Reforma completa do mercado municipal com nova estrutura e modernização',
                'responsible': 'Eng. Fernando Lima'
            }
        ]
        
        projects = []
        for data in projects_data:
            project = WorkProject.objects.create(**data)
            projects.append(project)
            self.stdout.write(f'  - Criado projeto: {project.name}')
        
        # Criar progresso para projetos em execução
        progress_data = [
            # Escola Municipal
            {
                'project': projects[0],
                'ref_month': date(2024, 1, 1),
                'physical_pct': Decimal('25.00'),
                'financial_pct': Decimal('20.00'),
                'notes': 'Fundação concluída, iniciando estrutura'
            },
            {
                'project': projects[0],
                'ref_month': date(2024, 2, 1),
                'physical_pct': Decimal('45.00'),
                'financial_pct': Decimal('38.00'),
                'notes': 'Estrutura em andamento, alvenaria iniciada'
            },
            {
                'project': projects[0],
                'ref_month': date(2024, 3, 1),
                'physical_pct': Decimal('65.00'),
                'financial_pct': Decimal('55.00'),
                'notes': 'Alvenaria concluída, iniciando instalações'
            },
            # Rua das Palmeiras
            {
                'project': projects[2],
                'ref_month': date(2024, 2, 1),
                'physical_pct': Decimal('30.00'),
                'financial_pct': Decimal('25.00'),
                'notes': 'Terraplanagem concluída, iniciando base'
            },
            {
                'project': projects[2],
                'ref_month': date(2024, 3, 1),
                'physical_pct': Decimal('60.00'),
                'financial_pct': Decimal('50.00'),
                'notes': 'Base concluída, iniciando pavimentação'
            },
            # Mercado Municipal (concluído)
            {
                'project': projects[4],
                'ref_month': date(2023, 12, 1),
                'physical_pct': Decimal('95.00'),
                'financial_pct': Decimal('90.00'),
                'notes': 'Obra quase concluída, aguardando vistoria final'
            },
            {
                'project': projects[4],
                'ref_month': date(2024, 1, 1),
                'physical_pct': Decimal('100.00'),
                'financial_pct': Decimal('100.00'),
                'notes': 'Obra concluída e entregue'
            }
        ]
        
        for data in progress_data:
            progress = WorkProgress.objects.create(**data)
            self.stdout.write(f'  - Criado progresso: {progress.project.name} - {progress.ref_month.strftime("%m/%Y")}')
        
        # Criar algumas fotos de exemplo
        photos_data = [
            {
                'project': projects[0],
                'title': 'Fundação da Escola',
                'description': 'Fundação concluída da escola municipal',
                'taken_date': date(2024, 1, 20),
                'location': 'Canteiro de obras - Escola Municipal'
            },
            {
                'project': projects[0],
                'title': 'Estrutura em Andamento',
                'description': 'Estrutura metálica sendo montada',
                'taken_date': date(2024, 2, 15),
                'location': 'Canteiro de obras - Escola Municipal'
            },
            {
                'project': projects[2],
                'title': 'Terraplanagem',
                'description': 'Terraplanagem da rua das Palmeiras',
                'taken_date': date(2024, 2, 10),
                'location': 'Rua das Palmeiras - Bairro Jardim'
            },
            {
                'project': projects[4],
                'title': 'Mercado Reformado',
                'description': 'Mercado municipal após reforma',
                'taken_date': date(2024, 1, 20),
                'location': 'Mercado Municipal - Centro'
            }
        ]
        
        for data in photos_data:
            # Como não temos arquivos reais, vamos criar registros sem foto
            photo = WorkPhoto.objects.create(**data)
            self.stdout.write(f'  - Criada foto: {photo.title} - {photo.project.name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Dados de exemplo criados com sucesso!\n'
                f'- {len(projects)} projetos\n'
                f'- {len(progress_data)} registros de progresso\n'
                f'- {len(photos_data)} fotos'
            )
        )



