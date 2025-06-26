#  coding: utf-8
from datetime import timedelta
from random import randint
from typing import List
from django.core.management.base import BaseCommand
from django.utils import timezone

from app.models import Boleto, Installment
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

        test_payer_with_agreements = PayerFactory.create(
            phone="12345678901",
            name="Teste User",
            user=test_user
        )

        test_agreements = AgreementFactory.create_batch(3, payer=test_payer_with_agreements)
        # Primeiro acordo — 10 parcelas
        # O primeiro dos 3 acordos deverá possuir 10 parcelas. 
        # 5 já foram pagas, a 6 está atrasada, 
        # a 7 ainda está dentro do prazo e as 
        # últimas não possuem boleto ainda
        agreement1 = test_agreements[0]
        base_date = timezone.now().date() + timedelta(days=5)
        for i in range(1, 11):
            due_date = base_date - timedelta(days=(6 - i) * 30)
            installment = InstallmentFactory.create(
                number=str(i),
                agreement=agreement1,
                due_date=due_date,
            )

            if i <= 5:
                BoletoFactory.create(installment=installment, status=Boleto.Status.PAID.value)
            elif i in [6, 7]:
                if i == 6:
                    installment.due_date = timezone.now().date() - timedelta(days=5)
                BoletoFactory.create(installment=installment, status=Boleto.Status.PENDING.value)
            else:
                # Sem boleto
                pass

        # Segundo acordo — 5 parcelas
        # O segundo acordo possui 5 parcelas. 
        # Apenas a última está pendente, e não está atrasada
        agreement2 = test_agreements[1]
        for i in range(1, 6):
            due_date = timezone.now().date() - timedelta(days=(25 - i * 4))
            installment = InstallmentFactory.create(
                number=str(i),
                agreement=agreement2,
                due_date=due_date,
            )

            if i < 5:
                BoletoFactory.create(installment=installment, status=Boleto.Status.PAID.value)
            else:
                future_date = timezone.now().date() + timedelta(days=7)
                installment.due_date = future_date
                installment.save()
                BoletoFactory.create(installment=installment, status=Boleto.Status.PENDING.value)

        # Terceiro acordo — 7 parcelas
        # O último acordo possui 7 parcelas. A primeira está atrasada. 
        # Da segunda até a quinta parcela está tudo pago. 
        # A sexta está pendente mas dentro do prazo, e a sétima 
        # ainda não possui o boleto
        agreement3 = test_agreements[2]
        for i in range(1, 8):
            installment = InstallmentFactory.create(
                number=str(i),
                agreement=agreement3,
                due_date=timezone.now().date() - timedelta(days=(20 - i * 3))
            )

            if i == 1:
                # Atrasada
                installment.due_date = timezone.now().date() - timedelta(days=10)
                installment.save()
                BoletoFactory.create(installment=installment, status=Boleto.Status.PENDING.value)
            elif 2 <= i <= 5:
                BoletoFactory.create(installment=installment, status=Boleto.Status.PAID.value)
            elif i == 6:
                installment.due_date = timezone.now().date() + timedelta(days=5)
                installment.save()
                BoletoFactory.create(installment=installment, status=Boleto.Status.PENDING.value)
            else:
                # Sem boleto
                pass

        test_user_2 = UserFactory.create(
            cpf="12345678902"
        )

        test_payer_without_agreements = PayerFactory.create(
            phone="12345678902",
            name="Teste User 2",
            user=test_user_2
        )

        self.stdout.write(self.style.SUCCESS('Banco populado com sucesso'))
