#  coding: utf-8
import os
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection

from config import ENV, PROD


class Command(BaseCommand):
    help = 'Deleta o shema public, deleta a migration e reconstrói tudo de novo'

    def handle(self, *app_labels, **options):
        if ENV == PROD:
            self.stdout.write(self.style.ERROR('Esse comando não pode ser executado em produção'))
            return

        should_seed = options.get('seed', False)

        with connection.cursor() as cursor:
            cursor.execute("PRAGMA writable_schema = 1;")
            cursor.execute("delete from sqlite_master where type in ('table', 'index', 'trigger');")
            cursor.execute("PRAGMA writable_schema = 0;")
            cursor.execute("VACUUM;")
            cursor.execute("PRAGMA INTEGRITY_CHECK;")

        # Deletando todos os arquivos de migrations
        prefix = __file__.split('management')[0] + 'migrations/'
        try:
            for file in os.listdir(prefix):
                if file.endswith('.py') and file != '__init__.py':
                    os.remove(os.path.join(prefix, file))
        except FileNotFoundError:
            print("Migrations não existiam")

        call_command('makemigrations')
        call_command('migrate')

        if should_seed:
            call_command('seed')
