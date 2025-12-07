from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar, Union
from uuid import UUID

DBModel = TypeVar("DBModel")
EntityModel = TypeVar("EntityModel")


class AbstractRepository(ABC, Generic[EntityModel]):

    @abstractmethod
    async def save(self, model: EntityModel) -> Union[EntityModel, None]: ...

    @abstractmethod
    async def get(self, id: Union[UUID, str]) -> Union[EntityModel, None]: ...

    @abstractmethod
    async def delete(self, id: Union[UUID, str]) -> Union[EntityModel, None]: ...
