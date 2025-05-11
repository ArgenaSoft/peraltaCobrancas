import logging

from django.http import HttpRequest
from django.contrib.auth import get_user_model
from ninja import Router
from ninja import Router

from app.controllers.auth_controller import AuthController
from app.schemas import LoginSchema, RefreshInputSchema, RefreshPairSchema, TokenOutSchema

payer_router = Router()
lgr = logging.getLogger(__name__)

auth_router = Router()


@auth_router.post("/token", response=TokenOutSchema)
def login(request, data: LoginSchema):
    token, payer_name = AuthController.login(data)
    return {
        "access": str(token.access_token), 
        "refresh": str(token),
        "username": payer_name
    }


@auth_router.post("/refresh", response=RefreshPairSchema)
def refresh_token_pair(request: HttpRequest, data: RefreshInputSchema):
    return AuthController.refresh_pair(data)
