#  coding: utf-8
from django.core.management.base import BaseCommand

from config import ENV, PROD
from tests.factories import PayerFactory


class Command(BaseCommand):
    help = 'Popula o banco com dados de exemplo'

    def handle(self, *app_labels, **options):
        if ENV == PROD:
            self.stdout.write(self.style.ERROR('Esse comando não pode ser executado em produção'))
            return

        PayerFactory.create_batch(10)
