from django.db import models
from django.contrib.auth.models import AbstractBaseUser

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class User(AbstractBaseUser, BaseModel):
    """
        Representa um Usuário que pode se logar no sistema

        Atributos:
            - cpf: CPF do Usuário.
            - is_active: Indica se o Usuário está ativo ou não.
            - staff_level: Nível de acesso do Usuário (Funcionário ou
            Administrador).
    """
    POSSIBLE_STAFF_LEVELS = (
        ('staff', 'Funcionário'),
        ('admin', 'Administrador'),
    )

    USERNAME_FIELD = 'cpf'

    cpf = models.CharField(max_length=11, unique=True)
    is_active = models.BooleanField(default=True)
    staff_level = models.CharField(
        max_length=10,
        choices=POSSIBLE_STAFF_LEVELS,
        default='staff',)


class Creditor(BaseModel):
    """
        Representa um Credor.

        Atributos:
            - name: Nome do Credor.
            - reissue_margin: Margem, em dias, de reemissão de boletos do 
            Credor. Caso o Pagador tente pegar a segunda via de um boleto
            faltando menos que essa quantidade de dias para o vencimento,
            o sistema automaticamente solicita a reemissão do boleto.
    """
    name = models.CharField(max_length=255)
    reissue_margin = models.SmallIntegerField()


class Payer(BaseModel):
    """
        Representa um Pagador.

        Atributos:
            - name: Nome do Pagador.
            - cpf: CPF do Pagador.
            - phone: Telefone do Pagador.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)


class Agreement(BaseModel):
    """
        Representa um Acordo.

        Atributos:
            - number: Número do sinistro.
            - payer: Pagador atrelado ao acordo.
            - creditor: Credor atrelado ao acordo.
    """
    number = models.CharField(max_length=255)
    payer = models.ForeignKey(Payer, on_delete=models.CASCADE)
    creditor = models.ForeignKey(Creditor, on_delete=models.CASCADE)


class Installment(BaseModel):
    """
        Representa uma Parcela.

        Atributos:
            - number: Número da parcela.
            - agreement: Acordo atrelado à parcela.
    """
    number = models.CharField(max_length=255)
    agreement = models.ForeignKey(Agreement, on_delete=models.CASCADE, related_name='installments')


class Boleto(BaseModel):
    """
        Representa um Boleto.

        Atributos:
            - pdf: Caminho do PDF do boleto no sistema.
            - installment: Parcela atrelada ao boleto.
            - status: Status do boleto (Pendente, Pago).
            - due_date: Data de vencimento do boleto.
    """
    POSSIBLE_STATUSES = (
        ('pending', 'Pendente'),
        ('paid', 'Pago'),
    )
    pdf = models.FileField(upload_to='boletos/')
    installment = models.ForeignKey(Installment, on_delete=models.CASCADE, related_name='boletos')
    status = models.CharField(
        max_length=10,
        choices=POSSIBLE_STATUSES,
        default='pending',
    )
    due_date = models.DateField()
