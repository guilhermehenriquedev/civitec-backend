"""
Comando para criar usuário master inicial
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = 'Cria usuário master inicial para o sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default='master@civitec.local',
            help='E-mail do usuário master'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='master123',
            help='Senha do usuário master'
        )
        parser.add_argument(
            '--name',
            type=str,
            default='Administrador Master',
            help='Nome completo do usuário master'
        )

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        name = options['name']
        
        try:
            with transaction.atomic():
                # Verificar se já existe um usuário master
                if User.objects.filter(role=User.RoleChoices.MASTER_ADMIN).exists():
                    self.stdout.write(
                        self.style.WARNING(
                            'Usuário master já existe no sistema.'
                        )
                    )
                    return
                
                # Criar usuário master
                first_name = name.split()[0]
                last_name = ' '.join(name.split()[1:]) if len(name.split()) > 1 else ''
                
                user = User.objects.create_user(
                    username=email.split('@')[0],
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=password,
                    role=User.RoleChoices.MASTER_ADMIN,
                    is_staff=True,
                    is_superuser=True,
                    is_active=True
                )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Usuário master criado com sucesso!\n'
                        f'E-mail: {email}\n'
                        f'Senha: {password}\n'
                        f'Role: {user.get_role_display()}'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao criar usuário master: {str(e)}')
            )
