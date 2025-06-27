#  coding: utf-8
import logging
from django.core.management.base import BaseCommand

from app.controllers.auth_controller import AuthController
from app.repositories.api_consumer_repository import ApiConsumerRepository


lgr = logging.getLogger(__name__)


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
        
        lgr.info(f"Tokens de acesso e refresh gerados para o sistema {system.name} (ID: {system.id})")
        self.stdout.write(self.style.SUCCESS(f'Access Token: {str(token.access_token)}'))
        self.stdout.write(self.style.SUCCESS(f'Refresh Token: {str(token)}'))
