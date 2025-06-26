import logging
from typing import Dict, Tuple, Union
from django.utils import timezone
from app.controllers.payer_controller import PayerController
from app.repositories.past_number_repository import PastNumberRepository
from app.repositories.payer_repository import PayerRepository
from ninja_jwt.tokens import RefreshToken, Token

from app.exceptions import HttpFriendlyException
from app.models import ApiConsumer, LoginCode, Payer, User
from app.repositories.login_code_repository import LoginCodeRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schemas import LoginSchema, RefreshInputSchema
from app.schemas.payer_schemas import PayerPatchInSchema

lgr = logging.getLogger(__name__)

class AuthController:
    @classmethod
    def login(cls, schema: LoginSchema) -> Tuple[RefreshToken, str]:
        try:
            user: User = UserRepository.get(cpf=schema.cpf, friendly=False)
            payer: Payer = user.payer

            login_code = LoginCodeRepository.get(
                code=schema.code,
                user=user,
                friendly=False)
        except User.DoesNotExist:
            raise HttpFriendlyException(401, "Cpf inválido.")
        except Payer.DoesNotExist:
            lgr.error("Existe usuário sem payer no banco: %s", schema.cpf)
            raise HttpFriendlyException(500, "Problema interno. Entre em contato com o suporte")
        except LoginCode.DoesNotExist:
            raise HttpFriendlyException(401, "Código inválido.")

        if login_code.used:
            raise HttpFriendlyException(401, "Código já usado") 

        if login_code.expiration_date < timezone.now():
            raise HttpFriendlyException(401, "Código expirou") 

        if payer.phone != schema.phone and not PastNumberRepository.exists(number=schema.phone):
            PastNumberRepository.create({
                "number":schema.phone,
                "payer":payer
            })

            PayerController.update(payer.id, PayerPatchInSchema(phone=schema.phone))

        token = cls.get_token(user.id, "user")
        LoginCodeRepository.update(login_code, used=True)
        return token, payer.name

    @classmethod
    def refresh_pair(cls, schema: RefreshInputSchema) -> Dict:
        try:
            token = RefreshToken(schema.refresh)
            token_type = token.get("type")
            entity_id = token.get("entity_id")
            
            if not token_type or not entity_id:
                raise HttpFriendlyException(401, "Token inválido")

            if token_type not in ['user', 'system']:
                raise HttpFriendlyException(401, "Tipo de token inválido")
            
            try:
                new_refresh = cls.get_token(entity_id, token_type)
            except (User.DoesNotExist, ApiConsumer.DoesNotExist) as e:
                raise HttpFriendlyException(403, f"{token_type.capitalize()} não encontrado")

            # Retornar os novos tokens
            return {
                "access": str(new_refresh.access_token),
                "refresh": str(new_refresh),
            }
        except Exception as e:
            raise HttpFriendlyException(401, f"Token inválido ou expirado: {str(e)}")
    
    @staticmethod
    def get_token(entity_id: int, type: str) -> Union[RefreshToken, Token]:
        if type == "user":
            user = UserRepository.get(id=entity_id)
            token = RefreshToken.for_user(user)
        else:
            token = RefreshToken()

        token.payload["type"] = type
        token.payload["entity_id"] = entity_id
        return token
