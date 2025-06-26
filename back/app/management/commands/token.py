#  coding: utf-8
from django.core.management.base import BaseCommand

from app.controllers.auth_controller import AuthController
from app.repositories.api_consumer_repository import ApiConsumerRepository


class Command(BaseCommand):
    help = 'Gera um JWT para um sistema externo'

    def add_arguments(self, parser):
        parser.add_argument("sys_id", type=str)

    def handle(self, *app_labels, **options):
        system_name = options['sys_id']
        system = ApiConsumerRepository.get(name=system_name, silent=True)

        if not system:
            self.stdout.write(self.style.WARNING(f'O sistema "{system_name}" não foi encontrado, criando...'))
            system = ApiConsumerRepository.create({"name": system_name})

        token = AuthController.get_token(system.name, 'system')
        
        self.stdout.write(self.style.SUCCESS(f'Access Token: {str(token.access_token)}'))
        self.stdout.write(self.style.SUCCESS(f'Refresh Token: {str(token)}'))
