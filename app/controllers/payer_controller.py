from app.controllers.user_controller import UserController
from app.models import Payer, User
from app.repositories.payer_repository import PayerRepository
from app.schemas import PayerSchema, UserSchema


class PayerController:
    @classmethod
    def create(cls, payer_schema: PayerSchema.In) -> Payer:
        """
        Cria um novo pagador.

        Parâmetros:
            - payer_schema: Schema do pagador a ser criado.

        Retorna:
            - Payer: Pagador criado.
        """
        uc_schema: UserSchema.In = UserSchema.In(
            cpf=payer_schema.cpf,
            is_active=True
        )

        user: User = UserController.create(uc_schema)
        payer_data = payer_schema.model_dump(exclude_none=True)
        payer_data['user_id'] = user.pk
        
        return PayerRepository.create(payer_data)

    @classmethod
    def update(cls, payer_id: int, payer_schema: PayerSchema.PatchIn) -> Payer:
        """
        Atualiza um pagador existente.

        Parâmetros:
            - payer_id: ID do pagador a ser atualizado.
            - payer_schema: Schema do pagador a ser atualizado.

        Retorna:
            - Payer: Pagador atualizado.
        """
        payer = PayerRepository.get(pk=payer_id)
        return PayerRepository.update(payer, **payer_schema.model_dump(exclude_none=True))
