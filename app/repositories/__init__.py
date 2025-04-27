
from typing import Dict, Generic, Type, TypeVar
from app.models import BaseModel


T = TypeVar("T", bound=BaseModel)

class BaseRepository(Generic[T]):
    """
    Classe base para repositórios.

    Atributos:
        - model: Modelo associado ao repositório.
    """
    model: Type[T]

    @classmethod
    def create(cls, data: Dict) -> T:
        """
        Cria uma nova instância do modelo. Ignora campos passados que não 
        correspondem a campos existentes no model

        Parâmetros:
            - kwargs: Atributos do modelo a serem criados.

        Retorna:
            - Instância do modelo criada.
        """
        new_instance = cls.model()
        for attr, value in data.items():
            if hasattr(new_instance, attr):
                setattr(new_instance, attr, value)
        
        new_instance.save()
        return new_instance

    @classmethod
    def get(cls, **kwargs) -> T:
        """
        Obtém uma instância do modelo com base nos atributos fornecidos.

        Parâmetros:
            - kwargs: Atributos do modelo a serem buscados.

        Retorna:
            - Instância do modelo correspondente.
        """
        return cls.model.objects.get(**kwargs)

    @classmethod
    def update(cls, instance: T, **kwargs) -> T:
        """
        Atualiza uma instância do modelo com base nos atributos fornecidos.

        Parâmetros:
            - instance: Instância do modelo a ser atualizada.
            - kwargs: Atributos do modelo a serem atualizados.

        Retorna:
            - Instância do modelo atualizada.
        """
        for attr, value in kwargs.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
    @classmethod
    def delete(cls, instance: T) -> None:
        """
        Deleta uma instância do modelo.

        Parâmetros:
            - instance: Instância do modelo a ser deletada.

        Retorna:
            - None
        """
        instance.delete()
        return None
