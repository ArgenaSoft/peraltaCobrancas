import logging
from django.db.models.query import QuerySet

from typing import Dict, Generic, List, Optional, Type, TypeVar
from app.exceptions import HttpFriendlyException
from app.models import BaseModel, SoftDeleteModel


lgr = logging.getLogger(__name__)
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
        model_fields = {field.name for field in cls.model._meta.get_fields() if not field.auto_created}

        for attr, value in data.items():
            if attr in model_fields:
                setattr(new_instance, attr, value)

        new_instance.save()
        return new_instance

    @classmethod
    def get(cls, friendly: bool = True, silent: bool = False, **kwargs) -> T:
        """
        Obtém uma instância do modelo com base nos atributos fornecidos.

        Parâmetros:
            - kwargs: Atributos do modelo a serem buscados.

        Retorna:
            - Instância do modelo correspondente.
        """
        try:
            return cls.model.objects.get(**kwargs)
        except cls.model.MultipleObjectsReturned:
            return cls.filter_first(**kwargs)
        except cls.model.DoesNotExist:
            if silent:
                return None

            if not friendly:
                raise
            raise HttpFriendlyException(404, f"{cls.model.READABLE_NAME} não encontrado")

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
        Deleta uma instância do modelo. Se essa instância for um modelo que
        herda de SoftDeleteModel, apenas marca como deletada.
        Se for um modelo que herda de BaseModel, deleta fisicamente.

        Parâmetros:
            - instance: Instância do modelo a ser deletada.

        Retorna:
            - None
        """
        if isinstance(instance, SoftDeleteModel):
            instance.is_deleted = True
            instance.save()
        else:
            instance.delete()

    @classmethod
    def filter(cls, include_rels: Optional[List[str]] = None, *args, **kwargs) -> QuerySet[T]:
        """
        Filtra instâncias do modelo com base nos atributos fornecidos,
        incluindo relacionamentos especificados.

        Parâmetros:
            - include_rels: Lista de nomes de relacionamentos a serem carregados.
            - kwargs: Atributos do modelo a serem filtrados.

        Retorna:
            - QuerySet com as instâncias correspondentes.
        """
        try:
            qs = cls.model.objects.filter(**kwargs)

            if include_rels:
                try:
                    try:
                        qs = qs.select_related(*include_rels)
                    except Exception:
                        qs = qs.prefetch_related(*include_rels)
                except Exception as e:
                    lgr.debug(f"Relacionamento(s) {include_rels} não encontrado(s) no modelo {cls.model.READABLE_NAME}")

            return qs
        except cls.model.DoesNotExist:
            raise HttpFriendlyException(404, f"{cls.model.READABLE_NAME} não encontrado")

    @classmethod
    def filter_first(cls, **kwargs) -> T:
        """
        Filtra a primeira instância do modelo com base nos atributos fornecidos.

        Parâmetros:
            - kwargs: Atributos do modelo a serem filtrados.

        Retorna:
            - Instância do modelo correspondente.
        """
        return cls.filter(**kwargs).first()

    @classmethod
    def exists(cls, *args, **kwargs) -> bool:
        """
        Verifica se uma instância do modelo existe com base nos atributos fornecidos.

        Parâmetros:
            - kwargs: Atributos do modelo a serem verificados.

        Retorna:
            - bool: Verdadeiro se a instância existir, falso caso contrário.
        """
        return cls.model.objects.filter(**kwargs).exists()
