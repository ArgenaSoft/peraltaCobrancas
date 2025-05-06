from datetime import timedelta
import logging

from django.conf import settings
from django.http import HttpRequest
from django.contrib.auth import get_user_model
from ninja import Router
from ninja import Router
from ninja_jwt.tokens import RefreshToken

from app.exceptions import HttpFriendlyException
from app.models import ApiConsumer
from app.repositories.user_repository import UserRepository
from app.schemas import AuthSchema

payer_router = Router()
lgr = logging.getLogger(__name__)

User = get_user_model()
auth_router = Router()

def get_token(entity_id: int, type: str) -> RefreshToken:
    # Crie o token e adicione as informações na payload
    
    if type == "user":
        user = UserRepository.get(id=entity_id)
        token = RefreshToken.for_user(user)
    else:
        token = RefreshToken()

    token.payload["type"] = type
    token.payload["entity_id"] = entity_id
    # Gerar o token
    return token


@auth_router.post("/token", response=AuthSchema.TokenOut)
def login(request, data: AuthSchema.AuthInput):
    try:
        user = UserRepository.get(cpf=data.cpf, payer__phone=data.phone)
    except User.DoesNotExist:
        raise HttpFriendlyException(401, "CPF ou telefone inválidos")

    token = get_token(user.id, "user")
    return {"access": str(token.access_token), "refresh": str(token)}


@auth_router.post("/refresh", response=AuthSchema.TokenPair)
def refresh_token_pair(request: HttpRequest, data: AuthSchema.RefreshInput):
    try:
        token = RefreshToken(data.refresh)
        token_type = token.get("type")
        entity_id = token.get("entity_id")
        
        if not token_type or not entity_id:
            raise HttpFriendlyException(401, "Token inválido")

        if token_type not in ['user', 'system']:
            raise HttpFriendlyException(401, "Tipo de token inválido")
        
        new_refresh = get_token(entity_id, token_type)

        # Retornar os novos tokens
        return {
            "access": str(new_refresh.access_token),
            "refresh": str(new_refresh),
        }
    except (User.DoesNotExist, ApiConsumer.DoesNotExist) as e:
        raise HttpFriendlyException(403, f"{token_type.capitalize()} não encontrado")
    except Exception as e:
        raise HttpFriendlyException(401, f"Token inválido ou expirado: {str(e)}")
