import logging
from typing import Dict

from ninja import Router
from django.core.handlers.wsgi import WSGIRequest

from app.api import endpoint
from app.controllers.payer_controller import PayerController
from app.models import Payer
from app.schemas import PayerSchema


payer_router = Router()
lgr = logging.getLogger(__name__)


@payer_router.post('/', response={201: PayerSchema.Out})
@endpoint
def create_payer(request: WSGIRequest, data: PayerSchema.In):
    new_payer: Payer = PayerController.create(data)
    return new_payer, 201



