#  coding: utf-8
import os
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection

from app.api.auth_api import get_token
from config import ENV, PROD


class Command(BaseCommand):
    help = 'Gera um JWT para um sistema externo'

    def add_arguments(self, parser):
        parser.add_argument("sys_id", type=str)

    def handle(self, *app_labels, **options):
        system_id = options['sys_id']
        token = get_token(system_id, 'system')
        self.stdout.write(self.style.SUCCESS(f'Access Token: {str(token.access_token)}'))
        self.stdout.write(self.style.SUCCESS(f'Refresh Token: {str(token)}'))
