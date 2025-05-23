#  coding: utf-8
from random import randint
from django.core.management.base import BaseCommand

from config import ENV, PROD
from tests.factories import AgreementFactory, ApiConsumerFactory, BoletoFactory, InstallmentFactory, PayerFactory, UserFactory


class Command(BaseCommand):
    help = 'Popula o banco com dados de exemplo'

    def handle(self, *app_labels, **options):
        if ENV == PROD:
            self.stdout.write(self.style.ERROR('Esse comando não pode ser executado em produção'))
            return

        test_user = UserFactory.create(
            cpf="12345678901"
        )

        test_payer = PayerFactory.create(
            phone="12345678901",
            name="Teste User",
            user=test_user
        )

        test_agreements = AgreementFactory.create_batch(3, payer=test_payer)
        installments = []
        for agree in test_agreements:
            installment_num = randint(1, 10)
            installments.extend(
                InstallmentFactory.create_batch(
                    installment_num, 
                    agreement=agree)
            )

        for inst in installments:
            BoletoFactory.create(installment=inst)

        # Como as parcelas estão vinculadas a acordos, que por sua vez estao com 
        # credores e pagadores, eu não preciso chamar as outras factories aqui.
        InstallmentFactory.create_batch(10)
        ApiConsumerFactory.create()
