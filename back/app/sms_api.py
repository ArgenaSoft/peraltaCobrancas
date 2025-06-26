import logging
import requests

from config import SMS_API_ENDPOINT, SMS_API_KEY


lgr = logging.getLogger(__name__)


def clean_phone(phone: str) -> str:
    """
    Remove non-numeric characters from the phone number.
    """
    return ''.join(filter(str.isdigit, phone))

def send_sms(phone: str, message: str) -> None:
    url = SMS_API_ENDPOINT
    phone = clean_phone(phone)
    headers = {
        "APIKEY": SMS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "celular": phone,
        "mensagem": message
    }

    try:
        lgr.debug(phone)
        lgr.debug(message)
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        lgr.error(f"Erro ao enviar SMS para {phone}")
        lgr.exception(e)
