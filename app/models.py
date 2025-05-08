import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def dict(self):
        """
            Retorna um dicionário com os campos do modelo.

            Retorna:
                - dict: Dicionário com os campos do modelo.
        """
        data = {}
        
        for field in self._meta.fields:
            if isinstance(field, models.ForeignKey):
                related_instance = getattr(self, field.name)
                if related_instance:
                    data[field.name] = related_instance.dict()
            elif isinstance(field, models.ManyToManyField):
                related_instances = getattr(self, field.name).all()
                data[field.name] = [instance.dict() for instance in related_instances]
            else:
                data[field.name] = getattr(self, field.name)

        return data


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


# Usuário logável
class User(AbstractBaseUser, BaseModel):
    """
        Representa um Usuário que pode se logar no sistema

        Atributos:
            - cpf: CPF do Usuário.
            - is_active: Indica se o Usuário está ativo ou não.
            - staff_level: Nível de acesso do Usuário (Funcionário ou
            Administrador).
    """
    USERNAME_FIELD = 'cpf'

    cpf = models.CharField(max_length=11, unique=True)
    is_active = models.BooleanField(default=True)
    objects = UserManager()

    def __str__(self):
        return self.cpf


# Credor
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


# Pagador
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


# Acordo
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


# Parcela
class Installment(BaseModel):
    """
        Representa uma Parcela.

        Atributos:
            - number: Número da parcela.
            - agreement: Acordo atrelado à parcela.
    """
    number = models.CharField(max_length=255)
    agreement = models.ForeignKey(Agreement, on_delete=models.CASCADE, related_name='installments')


# Boleto
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


class LoginCode(BaseModel):
    """
        Representa um código de login.

        Atributos:
            - code: Código de login.
            - user: Usuário atrelado ao código.
            - expiration_date: Data de expiração do código.
            - used: Se o código já foi usado
    """
    code = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expiration_date = models.DateTimeField()
    used = models.BooleanField(default=False)


def generate_api_key():
    return uuid.uuid4().hex

class ApiConsumer(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    api_key = models.CharField(max_length=32, unique=True, default=generate_api_key)

    def __str__(self):
        return self.name
