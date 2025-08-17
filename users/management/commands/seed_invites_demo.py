"""
Comando para criar convites de demonstração
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from users.models import UserInvite

User = get_user_model()


class Command(BaseCommand):
    help = 'Cria convites de demonstração para o sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=2,
            help='Número de convites a serem criados'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        try:
            with transaction.atomic():
                # Verificar se existe usuário master
                master_user = User.objects.filter(role=User.RoleChoices.MASTER_ADMIN).first()
                if not master_user:
                    self.stdout.write(
                        self.style.ERROR(
                            'Usuário master não encontrado. Execute primeiro: python manage.py seed_master'
                        )
                    )
                    return
                
                # Dados de demonstração
                demo_data = [
                    {
                        'email': 'rh@civitec.local',
                        'full_name': 'João Silva',
                        'role_code': User.RoleChoices.SECTOR_ADMIN,
                        'sector_code': User.SectorChoices.RH
                    },
                    {
                        'email': 'tributos@civitec.local',
                        'full_name': 'Maria Santos',
                        'role_code': User.RoleChoices.SECTOR_OPERATOR,
                        'sector_code': User.SectorChoices.TRIBUTOS
                    },
                    {
                        'email': 'licitacao@civitec.local',
                        'full_name': 'Pedro Oliveira',
                        'role_code': User.RoleChoices.SECTOR_OPERATOR,
                        'sector_code': User.SectorChoices.LICITACAO
                    },
                    {
                        'email': 'obras@civitec.local',
                        'full_name': 'Ana Costa',
                        'role_code': User.RoleChoices.EMPLOYEE,
                        'sector_code': User.SectorChoices.OBRAS
                    }
                ]
                
                # Criar convites
                invites_created = 0
                for data in demo_data[:count]:
                    # Verificar se já existe convite ativo
                    if UserInvite.objects.filter(
                        email=data['email'],
                        status=UserInvite.StatusChoices.PENDING
                    ).exists():
                        self.stdout.write(
                            self.style.WARNING(
                                f'Convite já existe para {data["email"]}'
                            )
                        )
                        continue
                    
                    # Verificar se usuário já existe
                    if User.objects.filter(email=data['email'], is_active=True).exists():
                        self.stdout.write(
                            self.style.WARNING(
                                f'Usuário já existe para {data["email"]}'
                            )
                        )
                        continue
                    
                    # Criar convite
                    invite = UserInvite.objects.create(
                        email=data['email'],
                        full_name=data['full_name'],
                        role_code=data['role_code'],
                        sector_code=data['sector_code'],
                        created_by=master_user
                    )
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Convite criado para {data["full_name"]} ({data["email"]})\n'
                            f'Código: {invite.security_code}\n'
                            f'Token: {invite.token[:20]}...\n'
                            f'URL: {invite.get_invite_url()}'
                        )
                    )
                    
                    invites_created += 1
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\nTotal de convites criados: {invites_created}'
                    )
                )
                
                if invites_created > 0:
                    self.stdout.write(
                        self.style.WARNING(
                            '\nIMPORTANTE: Em desenvolvimento, os e-mails são exibidos no console do Django.'
                        )
                    )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao criar convites: {str(e)}')
            )
