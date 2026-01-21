import logging
import getpass

from django.core.management.base import BaseCommand

from app.models import User
from app.controllers.user_controller import UserController
from app.schemas.user_schemas import AdminInSchema


lgr = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Cria ou atualiza o usuário administrador"

    def handle(self, *args, **options):
        cpf = input("CPF/CNPJ do admin: ")
        password = getpass.getpass("Senha: ")

        created = False
        user = UserController.get(cpf_cnpj=cpf, silent=True)
        if not user:
            created = True
            schema = AdminInSchema(cpf_cnpj=cpf, staff_level=User.StaffLevel.ADMIN)
            user = UserController.create(schema)

        user.set_password(password)
        user.is_active = True
        user.save()

        msg = f"Admin {user.cpf_cnpj} " + ("criado" if created else "atualizado")
        lgr.info(msg)
        self.stdout.write(self.style.SUCCESS(msg))
