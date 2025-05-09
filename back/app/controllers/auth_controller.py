from typing import Dict
from django.utils import timezone
from ninja_jwt.tokens import RefreshToken

from app.exceptions import HttpFriendlyException
from app.models import ApiConsumer, LoginCode, User
from app.repositories.login_code_repository import LoginCodeRepository
from app.repositories.user_repository import UserRepository
from app.schemas import LoginSchema, RefreshInputSchema


class AuthController:
    @classmethod
    def login(cls, schema: LoginSchema) -> RefreshToken:
        try:
            user = UserRepository.get(
                cpf=schema.cpf, 
                payer__phone=schema.phone,
                friendly=False)
            login_code = LoginCodeRepository.get(
                code=schema.code,
                user=user,
                friendly=False)
        except User.DoesNotExist:
            raise HttpFriendlyException(401, "Cpf ou telefone inválidos")
        except LoginCode.DoesNotExist:
            raise HttpFriendlyException(401, "Código inválido")


        if login_code.used:
            raise HttpFriendlyException(401, "Código já usado") 

        if login_code.expiration_date < timezone.now():
            raise HttpFriendlyException(401, "Código expirou") 

        LoginCodeRepository.update(login_code, used=True)

        token = cls.get_token(user.id, "user")
        return token

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
            
            new_refresh = cls.get_token(entity_id, token_type)

            # Retornar os novos tokens
            return {
                "access": str(new_refresh.access_token),
                "refresh": str(new_refresh),
            }
        except (User.DoesNotExist, ApiConsumer.DoesNotExist) as e:
            raise HttpFriendlyException(403, f"{token_type.capitalize()} não encontrado")
        except Exception as e:
            raise HttpFriendlyException(401, f"Token inválido ou expirado: {str(e)}")
    
    @staticmethod
    def get_token(entity_id: int, type: str) -> RefreshToken:
        if type == "user":
            user = UserRepository.get(id=entity_id)
            token = RefreshToken.for_user(user)
        else:
            token = RefreshToken()

        token.payload["type"] = type
        token.payload["entity_id"] = entity_id
        return token
