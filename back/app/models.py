from enum import Enum
import uuid
import unidecode

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    READABLE_NAME = None

    @staticmethod
    def resolve_foreign_field_value(value, dry: bool = False):
        if value and not dry:
            return value.dict(dry=dry)
        else:
            return value.pk if value else None

    def dict(self, dry: bool = False):
        """
        Retorna um dicionário com os campos do modelo.

        dry=True: exclui relações (FK, O2O, M2M)
        """
        data = {}

        for field in self._meta.fields:
            if dry and field.is_relation:
                continue

            try:
                value = getattr(self, field.name)
            except AttributeError:
                continue

            if isinstance(field, models.ManyToManyField):
                data[field.name] = [obj.pk for obj in value.all()] if not dry else []
            elif isinstance(field, models.ForeignKey) or isinstance(field, models.OneToOneField):
                data[field.name] = self.resolve_foreign_field_value(value, dry)
            else:
                data[field.name] = value

        return data

    class Meta:
        abstract = True


class Authenticatable(BaseModel):
    """
        Representa um modelo que pode ser autenticado.
    """
    is_human: bool = False

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    class Meta:
        abstract = True


class UserManager(BaseUserManager):
    def create_user(self, cpf, **extra_fields):
        if not cpf:
            raise ValueError("CPF é obrigatório")
        user = self.model(cpf=cpf, **extra_fields)
        user.set_unusable_password()  # não usamos senha
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, Authenticatable):
    """
        Representa um Usuário que pode se logar no sistema

        Atributos:
            - cpf: CPF do Usuário.
            - is_active: Indica se o Usuário está ativo ou não.
            - staff_level: Nível de acesso do Usuário (Funcionário ou
            Administrador).
    """
    READABLE_NAME = 'Usuário'
    USERNAME_FIELD = 'cpf'
    is_human = True

    cpf = models.CharField(max_length=11, unique=True)
    is_active = models.BooleanField(default=True)
    objects = UserManager()

    def __str__(self):
        return self.cpf


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
    READABLE_NAME = 'Credor'
    name = models.CharField(max_length=255)
    reissue_margin = models.SmallIntegerField()

    @property
    def slug_name(self):
        """
            Retorna o nome do credor com espaços substituídos por underline, em minúsculo e sem acentos ou símbolos especiais.

            Retorna:
                - str: Nome do credor formatado.
        """
        return unidecode.unidecode(self.name).replace(' ', '_').lower()


class Payer(BaseModel):
    """
        Representa um Pagador.

        Atributos:
            - name: Nome do Pagador.
            - cpf: CPF do Pagador.
            - phone: Telefone do Pagador.
    """
    READABLE_NAME = 'Pagador'
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='payer')
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
    class Status(str, Enum):
        OPEN = 'open'
        CLOSED = 'closed'

    READABLE_NAME = 'Acordo'
    number = models.CharField(max_length=255)
    payer = models.ForeignKey(Payer, on_delete=models.CASCADE, related_name='agreements')
    creditor = models.ForeignKey(Creditor, on_delete=models.CASCADE, related_name='agreements')
    status = models.CharField(
        max_length=10,
        choices=[(status.value, status.name.capitalize()) for status in Status],
        default=Status.OPEN.value,
    )

    @property
    def slug_name(self):
        """
            Retorna o nome do acordo com espaços substituídos por underline, em minúsculo e sem acentos ou símbolos especiais.

            Retorna:
                - str: Nome do acordo formatado.
        """
        return unidecode.unidecode(self.number).replace(' ', '_').lower()


class Installment(BaseModel):
    """
        Representa uma Parcela.

        Atributos:
            - number: Número da parcela.
            - agreement: Acordo atrelado à parcela.
            - due_date: Data de vencimento da parcela.
    """
    READABLE_NAME = 'Parcela'
    number = models.CharField(max_length=255)
    agreement = models.ForeignKey(Agreement, on_delete=models.CASCADE, related_name='installments')
    due_date = models.DateField()

    @property
    def slug_name(self):
        """
            Retorna o nome da parcela com espaços substituídos por underline, em minúsculo e sem acentos ou símbolos especiais.

            Retorna:
                - str: Nome da parcela formatado.
        """
        return unidecode.unidecode(self.number).replace(' ', '_').lower()


class Boleto(BaseModel):
    """
        Representa um Boleto.

        Atributos:
            - pdf: Caminho do PDF do boleto no sistema.
            - installment: Parcela atrelada ao boleto.
            - status: Status do boleto (Pendente, Pago).
    """
    READABLE_NAME = 'Boleto'
    class Status(str, Enum):
        PENDING = 'pending'
        PAID = 'paid'


    pdf = models.FileField(upload_to='boletos/')
    installment = models.OneToOneField(Installment, on_delete=models.CASCADE, related_name='boleto')
    status = models.CharField(
        max_length=10,
        choices=[(status.value, status.name.capitalize()) for status in Status],
        default=Status.PENDING.value,
    )

    def dict(self, *args, **kwargs):
        """
            Retorna um dicionário com os campos do modelo.

            Retorna:
                - dict: Dicionário com os campos do modelo.
        """
        data = super().dict(*args, **kwargs)
        data['pdf'] = self.pdf.url if hasattr(self.pdf, 'url') else str(self.pdf)
        return data


class LoginCode(BaseModel):
    """
        Representa um código de login.

        Atributos:
            - code: Código de login.
            - user: Usuário atrelado ao código.
            - expiration_date: Data de expiração do código.
            - used: Se o código já foi usado
    """
    READABLE_NAME = 'Código'
    code = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expiration_date = models.DateTimeField()
    used = models.BooleanField(default=False)


def generate_api_key():
    return uuid.uuid4().hex


class ApiConsumer(Authenticatable):
    READABLE_NAME = 'Sistema externo'
    is_human = False
    name = models.CharField(max_length=255, unique=True)
    api_key = models.CharField(max_length=32, unique=True, default=generate_api_key)

    def __str__(self):
        return self.name


class PastNumber(BaseModel):
    """
        Representa um número passado.

        Atributos:
            - number: Número passado.
            - user: Usuário atrelado ao número.
    """
    READABLE_NAME = 'Número passado'
    number = models.CharField(max_length=255, unique=True)
    payer = models.ForeignKey(Payer, on_delete=models.CASCADE, related_name='past_numbers')

    def __str__(self):
        return self.number
