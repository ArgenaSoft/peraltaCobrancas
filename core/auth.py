import logging

from jwt.exceptions import ExpiredSignatureError
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.exceptions import TokenError
from ninja_jwt.tokens import AccessToken

from app.exceptions import HttpFriendlyException
from app.models import ApiConsumer, User
from app.repositories.api_consumer_repository import ApiConsumerRepository
from app.repositories.user_repository import UserRepository


lgr = logging.getLogger(__name__)

class CustomJWTAuth(JWTAuth):
    def authenticate(self, request, token):
        try:
            # Validando o token
            validated_token = AccessToken(token)
            token_type = validated_token.get("type")  # Pode ser 'user' ou 'system'
            entity_id = validated_token.get("entity_id")  # O ID que pode ser de usuário ou sistema externo

            if not token_type or not entity_id:
                raise HttpFriendlyException(401, "Token inválido")

            # Se for 'user', buscar no modelo User
            if token_type == 'user':
                try:
                    user = UserRepository.get(id=entity_id)
                    request.auth = validated_token  # Armazena o token no request
                    return user
                except User.DoesNotExist:
                    raise HttpFriendlyException(403, "Usuário não encontrado")

            # Se for 'system', buscar no modelo ApiConsumer
            elif token_type == 'system':
                try:
                    system = ApiConsumerRepository.get(api_key=entity_id)
                    request.auth = validated_token  # Armazena o token no request
                    return system
                except ApiConsumer.DoesNotExist:
                    raise HttpFriendlyException(403, "Sistema externo não encontrado")

            raise HttpFriendlyException(401, "Tipo de usuário não reconhecido")

        except TokenError as e:
            if e.__cause__ :
                hidden_cause = e.__cause__.__cause__ 
                if hidden_cause and isinstance(hidden_cause, ExpiredSignatureError):
                    raise HttpFriendlyException(401, "Token expirado")
            
            lgr.error("Causa desconhecida:")
            lgr.exception(e)
            raise HttpFriendlyException(401, "Token inválido")
