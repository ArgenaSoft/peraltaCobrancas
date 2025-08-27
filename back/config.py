import os

PROD = 'prod'
DEV = 'dev'

ENV = os.getenv('ENV', PROD).lower()

ACCESS_TOKEN_EXPIRATION_SECONDS = int(os.getenv('ACCESS_TOKEN_EXPIRATION_SECONDS', 60 * 60 * 24))
REFRESH_TOKEN_EXPIRATION_SECONDS = int(os.getenv('REFRESH_TOKEN_EXPIRATION_SECONDS', 60 * 60 * 24 * 2))

SMS_CODE_EXPIRATION_SECONDS = int(os.getenv('SMS_CODE_EXPIRATION_SECONDS', 15))
SMS_API_ENDPOINT = os.getenv('SMS_API_ENDPOINT', "API-ENDPOINT-HERE")
SMS_API_KEY =  os.getenv('SMS_API_KEY', "API-KEY-HERE")

USING_AWS = bool(os.getenv('USING_AWS', 'False'))
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')

AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME', '')

AWS_S3_ENDPOINT_URL = os.getenv('AWS_S3_ENDPOINT_URL', '')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
AWS_S3_SIGNATURE_VERSION = os.getenv('AWS_S3_SIGNATURE_VERSION', 's3v4')
AWS_S3_FILE_OVERWRITE = bool(os.getenv('AWS_S3_FILE_OVERWRITE', 'False'))
AWS_DEFAULT_ACL = os.getenv('AWS_DEFAULT_ACL', None)

if USING_AWS and (not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY or not AWS_STORAGE_BUCKET_NAME):
    raise Exception("Se for usar AWS, precisa configurar AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY e AWS_STORAGE_BUCKET_NAME")

try:
    from local_config import * # type: ignore
except ImportError:
    print("No local_config.py found, using default settings.")
