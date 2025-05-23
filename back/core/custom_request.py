from typing import Optional
from django.http import HttpRequest

from app.models import Authenticatable


class CustomRequest(HttpRequest):
    """
    ATENÇÃO: Esta classe não é de fato usada pelo Django. Serve apenas para tipagem.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.actor: Authenticatable = None


class InjectActorOnRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.actor = None
        return self.get_response(request)
