import pytest

import pytest
from datetime import datetime, date
from decimal import Decimal
from uuid import uuid4
from dataclasses import dataclass
from typing import Optional

# test_models.py
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import json
from domain import RedisSerializable


class TestEnum(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


@dataclass
class NestedDataClass:
    id: int
    name: str


@dataclass
class TestDataClass(RedisSerializable):
    """Базовый датакласс для тестирования"""

    id: UUID
    name: str
    age: int
    is_active: bool
    price: Decimal
    created_at: datetime
    birth_date: date
    status: TestEnum
    tags: List[str]
    metadata: Dict[str, Any]
    optional_field: Optional[str] = None
    nested: Optional[NestedDataClass] = None
    binary_data: Optional[bytes] = None
    excluded_none: Optional[str] = None


@dataclass
class ComplexNestedClass(RedisSerializable):
    id: UUID
    test_obj: TestDataClass
    numbers: List[int]


class NotADataClass(RedisSerializable):
    """Класс НЕ являющийся датаклассом"""

    def __init__(self, value):
        self.value = value


@dataclass
class EdgeCaseClass(RedisSerializable):
    set_field: set
    tuple_field: tuple
    none_field: Optional[str] = None
    false_field: bool = False
    zero_field: int = 0


@pytest.fixture
def test_uuid():
    return uuid4()


@pytest.fixture
def test_datetime():
    return datetime(2024, 1, 1, 12, 30, 45)


@pytest.fixture
def test_date():
    return date(2024, 1, 1)


@pytest.fixture
def test_decimal():
    return Decimal("123.45")


@pytest.fixture
def test_bytes():
    return b"test data"


@pytest.fixture
def nested_dataclass():
    return NestedDataClass(id=1, name="Nested")


@pytest.fixture
def base_test_data(
    test_uuid, test_datetime, test_date, test_decimal, test_bytes, nested_dataclass
):
    """Базовые тестовые данные"""
    return {
        "id": test_uuid,
        "name": "John Doe",
        "age": 30,
        "is_active": True,
        "price": test_decimal,
        "created_at": test_datetime,
        "birth_date": test_date,
        "status": TestEnum.ACTIVE,
        "tags": ["tag1", "tag2"],
        "metadata": {"key": "value", "nested": {"inner": "data"}},
        "optional_field": "optional",
        "nested": nested_dataclass,
        "binary_data": test_bytes,
        "excluded_none": None,
    }


@pytest.fixture
def test_obj(base_test_data):
    """Фикстура тестового объекта"""
    return TestDataClass(**base_test_data)


@pytest.fixture
def empty_test_obj(test_uuid, test_datetime, test_date):
    """Фикстура объекта с пустыми/нулевыми значениями"""
    return TestDataClass(
        id=test_uuid,
        name="",
        age=0,
        is_active=False,
        price=Decimal("0"),
        created_at=test_datetime,
        birth_date=test_date,
        status=TestEnum.INACTIVE,
        tags=[],
        metadata={},
        optional_field=None,
        nested=None,
        binary_data=b"",
        excluded_none=None,
    )


@pytest.fixture
def complex_nested_obj(test_obj, test_uuid):
    """Фикстура сложного вложенного объекта"""
    return ComplexNestedClass(id=test_uuid, test_obj=test_obj, numbers=[1, 2, 3])


@pytest.fixture
def edge_case_obj():
    """Фикстура для тестирования крайних случаев"""
    return EdgeCaseClass(set_field={1, 2, 3}, tuple_field=(4, 5, 6))
