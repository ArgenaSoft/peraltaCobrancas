#  coding: utf-8
from random import randint
from typing import List
from django.core.management.base import BaseCommand
from django.utils import timezone

from app.models import Installment
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
        installments: List[Installment] = []
        for agree in test_agreements:
            installment_num = randint(1, 10)
            due_date_factor = randint(-5, 5)
            installments.extend(
                InstallmentFactory.create_batch(
                    installment_num, 
                    agreement=agree,
                    due_date=timezone.now() + timezone.timedelta(days=due_date_factor)
                    )
            )

        for inst in installments:
            # Crio o boleto apenas se a data de vencimento da parcela for dentro 2 dias
            if inst.due_date > timezone.now() + timezone.timedelta(days=2):
                continue

            BoletoFactory.create(
                installment=inst,
            )

        # Como as parcelas estão vinculadas a acordos, que por sua vez estao com 
        # credores e pagadores, eu não preciso chamar as outras factories aqui.
        InstallmentFactory.create_batch(10)
        ApiConsumerFactory.create()
