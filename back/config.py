import os


PROD = 'prod'
DEV = 'dev'

ENV = os.getenv('ENV', PROD).lower()
SMS_CODE_EXPIRATION_SECONDS = int(os.getenv('SMS_CODE_EXPIRATION_SECONDS', 15))
SMS_API_ENDPOINT = os.getenv('SMS_API_ENDPOINT', "API-ENDPOINT-HERE")
SMS_API_KEY =  os.getenv('SMS_API_KEY', "API-KEY-HERE")

try:
    from local_config import * # type: ignore
except ImportError:
    print("No local_config.py found, using default settings.")
