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
    """
        Middleware para a autenticação por JWT.
        Este middleware sempre seta o campo 'actor'.
    """
    def authenticate(self, request, token):
        try:
            validated_token = AccessToken(token)
            token_type = validated_token.get("type")
            entity_id = validated_token.get("entity_id")

            if not token_type or not entity_id:
                raise HttpFriendlyException(401, "Token inválido")

            if token_type == 'user':
                return self.get_user(entity_id, request, validated_token)
            elif token_type == 'system':
                return self.get_api_consumer(entity_id, request, validated_token)

            raise HttpFriendlyException(401, "Tipo de usuário não reconhecido")

        except TokenError as e:
            if e.__cause__:
                hidden_cause = e.__cause__.__cause__
                if hidden_cause and isinstance(hidden_cause, ExpiredSignatureError):
                    raise HttpFriendlyException(401, "Token expirado")

            lgr.error("Causa desconhecida:")
            lgr.exception(e)
            raise HttpFriendlyException(401, "Token inválido")

    def get_user(self, entity_id: str, request, validated_token: AccessToken):
        try:
            user = UserRepository.get(id=entity_id)
            request.auth = validated_token
            request.actor = user
            if not self.allow_user(user):
                raise HttpFriendlyException(403, "Rota não permitida para este usuário")

            return user
        except User.DoesNotExist:
            raise HttpFriendlyException(403, "Usuário não encontrado")

    def get_api_consumer(self, entity_id: str, request, validated_token: AccessToken):
        try:
            system = ApiConsumerRepository.get(api_key=entity_id)
            request.auth = validated_token
            request.actor = system
            return system
        except ApiConsumer.DoesNotExist:
            raise HttpFriendlyException(403, "Sistema externo não encontrado")

    def allow_user(self, user: User):
        """
            Retorna se é possível User acessar a rota.
            Deixei o parâmetro user pois no futuro pode ser que seja necessário 
            para algum tipo de filtragem, como permitir staff
        """
        return False


class AllowHumansAuth(CustomJWTAuth):
    def allow_user(self, user: User):
        return True
