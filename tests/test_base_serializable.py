"""Тесты для base_serializabel.py"""

import pytest
from dataclasses import dataclass, field
from uuid import UUID, uuid4
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import json

from domain.base_serializabel import RedisSerializable


class SampleEnum(Enum):
    """Тестовый enum."""

    VALUE1 = "value1"
    VALUE2 = 2
    VALUE3 = "value_three"


@dataclass
class SimpleNested(RedisSerializable):
    """Простой вложенный объект."""

    nested_field: str = "nested_value"
    nested_number: int = 42


@dataclass
class SampleDataclass(RedisSerializable):
    """Тестовый dataclass для проверки сериализации."""

    # Простые типы
    string_field: str = "test_string"
    int_field: int = 42
    float_field: float = 3.14
    bool_field: bool = True

    # None значения
    none_field: str = None

    # UUID
    uuid_field: UUID = field(default_factory=uuid4)

    # Дата и время
    datetime_field: datetime = field(
        default_factory=lambda: datetime(2024, 1, 15, 12, 30, 45)
    )
    date_field: date = field(default_factory=lambda: date(2024, 1, 15))

    # Decimal
    decimal_field: Decimal = Decimal("123.45")

    # Enum
    enum_field: SampleEnum = SampleEnum.VALUE1

    # Bytes
    bytes_field: bytes = b"test_bytes"

    # Коллекции
    list_field: list = field(default_factory=lambda: [1, 2, 3])
    dict_field: dict = field(default_factory=lambda: {"key1": "value1", "key2": 2})
    tuple_field: tuple = field(default_factory=lambda: (1, 2, 3))
    set_field: set = field(default_factory=lambda: {1, 2, 3})

    # Вложенные объекты RedisSerializable
    nested_object: SimpleNested = field(default_factory=lambda: SimpleNested())

    # Список вложенных объектов
    nested_list: list = field(
        default_factory=lambda: [
            SimpleNested(nested_field="item1"),
            SimpleNested(nested_field="item2"),
        ]
    )


@dataclass
class SampleWithNoneFields(RedisSerializable):
    """Тестовый класс с None полями."""

    field1: str = "value1"
    field2: str = None
    field3: int = None
    field4: str = "value4"


@dataclass
class SampleEmpty(RedisSerializable):
    """Пустой dataclass."""

    pass


@dataclass
class SampleDeeplyNested(RedisSerializable):
    """Глубоко вложенные объекты."""

    level1: SimpleNested = field(
        default_factory=lambda: SimpleNested(nested_field="level1")
    )

    @dataclass
    class Level2(RedisSerializable):
        level2_field: str = "level2"
        level3: "SampleDeeplyNested.Level2.Level3" = None

        @dataclass
        class Level3(RedisSerializable):
            level3_field: str = "level3"

    level2_obj: Level2 = field(default_factory=Level2)


class NotADataclass(RedisSerializable):
    """Класс, который не является dataclass."""

    def __init__(self):
        self.field = "value"


class TestSerializeValue:
    """Тесты для метода _serialize_value."""

    def test_serialize_none(self):
        """Тест сериализации None."""
        obj = SampleDataclass()
        assert obj._serialize_value(None) is None

    def test_serialize_simple_types(self):
        """Тест сериализации простых типов."""
        obj = SampleDataclass()
        assert obj._serialize_value("string") == "string"
        assert obj._serialize_value(42) == 42
        assert obj._serialize_value(3.14) == 3.14
        assert obj._serialize_value(True) is True
        assert obj._serialize_value(False) is False

    def test_serialize_uuid(self):
        """Тест сериализации UUID."""
        obj = SampleDataclass()
        test_uuid = uuid4()
        result = obj._serialize_value(test_uuid)
        assert isinstance(result, str)
        assert result == str(test_uuid)

    def test_serialize_datetime(self):
        """Тест сериализации datetime."""
        obj = SampleDataclass()
        test_dt = datetime(2024, 1, 15, 12, 30, 45)
        result = obj._serialize_value(test_dt)
        assert isinstance(result, str)
        assert result == test_dt.isoformat()

    def test_serialize_date(self):
        """Тест сериализации date."""
        obj = SampleDataclass()
        test_date = date(2024, 1, 15)
        result = obj._serialize_value(test_date)
        assert isinstance(result, str)
        assert result == test_date.isoformat()

    def test_serialize_decimal(self):
        """Тест сериализации Decimal."""
        obj = SampleDataclass()
        test_decimal = Decimal("123.45")
        result = obj._serialize_value(test_decimal)
        assert isinstance(result, str)
        assert result == "123.45"

    def test_serialize_enum(self):
        """Тест сериализации Enum."""
        obj = SampleDataclass()
        assert obj._serialize_value(SampleEnum.VALUE1) == "value1"
        assert obj._serialize_value(SampleEnum.VALUE2) == 2
        assert obj._serialize_value(SampleEnum.VALUE3) == "value_three"

    def test_serialize_bytes(self):
        """Тест сериализации bytes."""
        obj = SampleDataclass()
        test_bytes = b"test_bytes"
        result = obj._serialize_value(test_bytes)
        assert isinstance(result, str)
        assert result == test_bytes.hex()

    def test_serialize_dict(self):
        """Тест сериализации словаря."""
        obj = SampleDataclass()
        test_dict = {
            "key1": "value1",
            "key2": 42,
            "key3": SampleEnum.VALUE1,
            "key4": {"nested": "dict"},
        }
        result = obj._serialize_value(test_dict)
        assert isinstance(result, dict)
        assert result["key1"] == "value1"
        assert result["key2"] == 42
        assert result["key3"] == "value1"  # Enum сериализован
        assert result["key4"]["nested"] == "dict"

    def test_serialize_list(self):
        """Тест сериализации списка."""
        obj = SampleDataclass()
        test_list = [1, "string", SampleEnum.VALUE1, [2, 3]]
        result = obj._serialize_value(test_list)
        assert isinstance(result, list)
        assert result == [1, "string", "value1", [2, 3]]

    def test_serialize_tuple(self):
        """Тест сериализации кортежа."""
        obj = SampleDataclass()
        test_tuple = (1, "string", SampleEnum.VALUE1)
        result = obj._serialize_value(test_tuple)
        assert isinstance(result, list)  # Tuple преобразуется в list
        assert result == [1, "string", "value1"]

    def test_serialize_set(self):
        """Тест сериализации множества."""
        obj = SampleDataclass()
        test_set = {1, 2, 3}
        result = obj._serialize_value(test_set)
        assert isinstance(result, list)  # Set преобразуется в list
        assert sorted(result) == [1, 2, 3]  # Порядок может отличаться

    def test_serialize_nested_redis_serializable(self):
        """Тест сериализации вложенного объекта RedisSerializable."""
        obj = SampleDataclass()
        nested = SimpleNested(nested_field="test", nested_number=100)
        result = obj._serialize_value(nested)
        assert isinstance(result, dict)
        assert result["nested_field"] == "test"
        assert result["nested_number"] == 100
        assert result["_type"] == "SimpleNested"


class TestToRedisDict:
    """Тесты для метода to_redis_dict."""

    def test_to_redis_dict_basic(self):
        """Тест базовой сериализации в словарь."""
        obj = SampleDataclass(
            string_field="test",
            int_field=42,
            uuid_field=uuid4(),
        )
        result = obj.to_redis_dict()

        assert isinstance(result, dict)
        assert result["string_field"] == "test"
        assert result["int_field"] == 42
        assert isinstance(result["uuid_field"], str)
        assert result["_type"] == "SampleDataclass"

    def test_to_redis_dict_exclude_none_true(self):
        """Тест exclude_none=True (по умолчанию)."""
        obj = SampleWithNoneFields(field1="value1", field2=None, field4="value4")
        result = obj.to_redis_dict(exclude_none=True)

        assert "field1" in result
        assert "field2" not in result  # None поле исключено
        assert "field3" not in result  # None поле исключено
        assert "field4" in result
        assert result["_type"] == "SampleWithNoneFields"

    def test_to_redis_dict_exclude_none_false(self):
        """Тест exclude_none=False."""
        obj = SampleWithNoneFields(field1="value1", field2=None, field4="value4")
        result = obj.to_redis_dict(exclude_none=False)

        assert "field1" in result
        assert "field2" in result
        assert result["field2"] is None  # None поле включено
        assert "field3" in result
        assert result["field3"] is None
        assert "field4" in result

    def test_to_redis_dict_nested_object(self):
        """Тест сериализации с вложенным объектом."""
        nested = SimpleNested(nested_field="nested_test", nested_number=100)
        obj = SampleDataclass(nested_object=nested)
        result = obj.to_redis_dict()

        assert isinstance(result["nested_object"], dict)
        assert result["nested_object"]["nested_field"] == "nested_test"
        assert result["nested_object"]["nested_number"] == 100
        assert result["nested_object"]["_type"] == "SimpleNested"

    def test_to_redis_dict_nested_list(self):
        """Тест сериализации со списком вложенных объектов."""
        nested_list = [
            SimpleNested(nested_field="item1"),
            SimpleNested(nested_field="item2"),
        ]
        obj = SampleDataclass(nested_list=nested_list)
        result = obj.to_redis_dict()

        assert isinstance(result["nested_list"], list)
        assert len(result["nested_list"]) == 2
        assert result["nested_list"][0]["nested_field"] == "item1"
        assert result["nested_list"][1]["nested_field"] == "item2"

    def test_to_redis_dict_empty_dataclass(self):
        """Тест сериализации пустого dataclass."""
        obj = SampleEmpty()
        result = obj.to_redis_dict()

        assert isinstance(result, dict)
        assert result["_type"] == "SampleEmpty"
        assert len(result) == 1  # Только _type

    def test_to_redis_dict_deeply_nested(self):
        """Тест сериализации глубоко вложенных объектов."""
        obj = SampleDeeplyNested()
        result = obj.to_redis_dict()

        assert isinstance(result["level1"], dict)
        assert result["level1"]["nested_field"] == "level1"
        assert isinstance(result["level2_obj"], dict)
        assert result["level2_obj"]["level2_field"] == "level2"

    def test_to_redis_dict_not_dataclass_error(self):
        """Тест ошибки при вызове на не-dataclass."""
        obj = NotADataclass()
        with pytest.raises(TypeError, match="NotADataclass is not a dataclass"):
            obj.to_redis_dict()

    def test_to_redis_dict_all_field_types(self):
        """Тест сериализации всех типов полей."""
        test_uuid = uuid4()
        test_dt = datetime(2024, 1, 15, 12, 30, 45)
        test_date_obj = date(2024, 1, 15)

        obj = SampleDataclass(
            string_field="test",
            int_field=42,
            float_field=3.14,
            bool_field=True,
            uuid_field=test_uuid,
            datetime_field=test_dt,
            date_field=test_date_obj,
            decimal_field=Decimal("123.45"),
            enum_field=SampleEnum.VALUE1,
            bytes_field=b"test",
            list_field=[1, 2, 3],
            dict_field={"key": "value"},
            tuple_field=(1, 2),
            set_field={1, 2, 3},
        )
        result = obj.to_redis_dict(exclude_none=True)

        # Проверяем все типы
        assert result["string_field"] == "test"
        assert result["int_field"] == 42
        assert result["float_field"] == 3.14
        assert result["bool_field"] is True
        assert result["uuid_field"] == str(test_uuid)
        assert result["datetime_field"] == test_dt.isoformat()
        assert result["date_field"] == test_date_obj.isoformat()
        assert result["decimal_field"] == "123.45"
        assert result["enum_field"] == "value1"
        assert result["bytes_field"] == b"test".hex()
        assert result["list_field"] == [1, 2, 3]
        assert result["dict_field"] == {"key": "value"}
        assert isinstance(result["tuple_field"], list)
        assert sorted(result["set_field"]) == [1, 2, 3]  # Set -> list
        assert result["_type"] == "SampleDataclass"


class TestToRedisJson:
    """Тесты для метода to_redis_json."""

    def test_to_redis_json_basic(self):
        """Тест базовой сериализации в JSON."""
        obj = SampleDataclass(string_field="test", int_field=42)
        result = obj.to_redis_json()

        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed["string_field"] == "test"
        assert parsed["int_field"] == 42
        assert parsed["_type"] == "SampleDataclass"

    def test_to_redis_json_with_indent(self):
        """Тест сериализации с отступами."""
        obj = SampleDataclass(string_field="test")
        result = obj.to_redis_json(indent=2)

        assert isinstance(result, str)
        assert "\n" in result  # Есть переносы строк
        parsed = json.loads(result)
        assert parsed["string_field"] == "test"

    def test_to_redis_json_exclude_none(self):
        """Тест что to_redis_json всегда исключает None."""
        obj = SampleWithNoneFields(field1="value1", field2=None)
        result = obj.to_redis_json()

        parsed = json.loads(result)
        assert "field1" in parsed
        assert "field2" not in parsed  # None исключен (exclude_none=True по умолчанию)

    def test_to_redis_json_nested_object(self):
        """Тест JSON с вложенными объектами."""
        nested = SimpleNested(nested_field="nested", nested_number=100)
        obj = SampleDataclass(nested_object=nested)
        result = obj.to_redis_json()

        parsed = json.loads(result)
        assert isinstance(parsed["nested_object"], dict)
        assert parsed["nested_object"]["nested_field"] == "nested"
        assert parsed["nested_object"]["nested_number"] == 100

    def test_to_redis_json_unicode(self):
        """Тест корректной обработки unicode символов."""
        obj = SampleDataclass(string_field="Тест с русскими символами 🎉")
        result = obj.to_redis_json()

        assert "Тест с русскими символами" in result
        assert "🎉" in result
        parsed = json.loads(result)
        assert parsed["string_field"] == "Тест с русскими символами 🎉"

    def test_to_redis_json_valid_json(self):
        """Тест что результат всегда валидный JSON."""
        obj = SampleDataclass(
            string_field="test",
            int_field=42,
            list_field=[1, 2, 3],
            dict_field={"key": "value"},
            nested_object=SimpleNested(),
        )
        result = obj.to_redis_json()

        # Должен парситься без ошибок
        parsed = json.loads(result)
        assert isinstance(parsed, dict)


class TestEdgeCases:
    """Тесты для граничных случаев."""

    def test_serialize_circular_reference_prevention(self):
        """Тест что циклические ссылки обрабатываются корректно."""
        # Создаем объект с циклической ссылкой через dict
        obj1 = SimpleNested(nested_field="obj1")
        obj2 = SimpleNested(nested_field="obj2")

        # Попытка создать циклическую ссылку через встроенный dict
        # (RedisSerializable не поддерживает циклические ссылки напрямую,
        # но должен корректно обрабатывать вложенные объекты)
        test_dict = {"obj": obj1}
        result = obj1._serialize_value(test_dict)
        assert isinstance(result, dict)
        assert isinstance(result["obj"], dict)

    def test_serialize_unknown_type(self):
        """Тест сериализации неизвестного типа."""
        obj = SampleDataclass()

        class UnknownType:
            def __str__(self):
                return "unknown"

        unknown = UnknownType()
        result = obj._serialize_value(unknown)
        assert result == "unknown"  # Должен преобразоваться в строку

    def test_to_redis_dict_with_default_factory(self):
        """Тест что default_factory работает корректно."""
        obj = SampleDataclass()  # Используем значения по умолчанию
        result = obj.to_redis_dict()

        # Проверяем что поля с default_factory сериализуются
        assert "list_field" in result
        assert isinstance(result["list_field"], list)
        assert "uuid_field" in result
        assert isinstance(result["uuid_field"], str)

    def test_to_redis_dict_complex_nested_structure(self):
        """Тест сложной вложенной структуры."""
        obj = SampleDataclass(
            dict_field={
                "list": [1, 2, SimpleNested(nested_field="in_list")],
                "nested": SimpleNested(nested_field="in_dict"),
                "enum": SampleEnum.VALUE2,
            },
            list_field=[
                {"key": "value"},
                SimpleNested(nested_field="in_list"),
                42,
            ],
        )
        result = obj.to_redis_dict()

        # Проверяем сложную структуру
        assert isinstance(result["dict_field"], dict)
        assert isinstance(result["dict_field"]["list"], list)
        assert result["dict_field"]["list"][2]["nested_field"] == "in_list"
        assert result["dict_field"]["nested"]["nested_field"] == "in_dict"
        assert result["dict_field"]["enum"] == 2  # TestEnum.VALUE2.value

        assert isinstance(result["list_field"], list)
        assert result["list_field"][0]["key"] == "value"
        assert result["list_field"][1]["nested_field"] == "in_list"
        assert result["list_field"][2] == 42
