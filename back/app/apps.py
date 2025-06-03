from django.apps import AppConfig



class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        from app.schemas.installment_schemas import InstallmentOutSchema
        from app.schemas.boleto_schemas import BoletoOutSchema
        
        BoletoOutSchema.model_rebuild()
        InstallmentOutSchema.model_rebuild()