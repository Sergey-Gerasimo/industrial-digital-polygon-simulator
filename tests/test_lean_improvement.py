"""Тесты для domain/lean_improvement.py"""

import pytest
import json

from domain.lean_improvement import LeanImprovement


class TestLeanImprovement:
    """Тесты для класса LeanImprovement."""

    def test_lean_improvement_creation_with_defaults(self):
        """Тест создания LEAN улучшения со значениями по умолчанию."""
        improvement = LeanImprovement()

        assert improvement.improvement_id == ""
        assert improvement.name == ""
        assert improvement.is_implemented is False
        assert improvement.implementation_cost == 0
        assert improvement.efficiency_gain == 0.0

    def test_lean_improvement_creation_with_values(self):
        """Тест создания LEAN улучшения с заданными значениями."""
        improvement = LeanImprovement(
            improvement_id="improvement_001",
            name="5S система",
            is_implemented=True,
            implementation_cost=50000,
            efficiency_gain=0.15,
        )

        assert improvement.improvement_id == "improvement_001"
        assert improvement.name == "5S система"
        assert improvement.is_implemented is True
        assert improvement.implementation_cost == 50000
        assert improvement.efficiency_gain == 0.15

    def test_lean_improvement_partial_initialization(self):
        """Тест создания LEAN улучшения с частичной инициализацией."""
        improvement = LeanImprovement(
            improvement_id="improvement_002",
            name="Канбан",
        )

        assert improvement.improvement_id == "improvement_002"
        assert improvement.name == "Канбан"
        # Остальные поля должны иметь значения по умолчанию
        assert improvement.is_implemented is False
        assert improvement.implementation_cost == 0
        assert improvement.efficiency_gain == 0.0

    def test_to_dict(self):
        """Тест преобразования в словарь."""
        improvement = LeanImprovement(
            improvement_id="improvement_003",
            name="TPM",
            is_implemented=True,
            implementation_cost=75000,
            efficiency_gain=0.20,
        )

        result = improvement.to_dict()

        assert isinstance(result, dict)
        assert result["improvement_id"] == "improvement_003"
        assert result["name"] == "TPM"
        assert result["is_implemented"] is True
        assert result["implementation_cost"] == 75000
        assert result["efficiency_gain"] == 0.20

    def test_to_dict_with_empty_id(self):
        """Тест преобразования в словарь с пустым ID."""
        improvement = LeanImprovement(
            improvement_id="",
            name="Улучшение",
        )

        result = improvement.to_dict()

        assert result["improvement_id"] is None  # Пустая строка преобразуется в None
        assert result["name"] == "Улучшение"

    def test_to_dict_with_none_id(self):
        """Тест преобразования в словарь когда ID отсутствует."""
        improvement = LeanImprovement(name="Улучшение")
        improvement.improvement_id = ""

        result = improvement.to_dict()

        assert result["improvement_id"] is None

    def test_from_dict(self):
        """Тест создания из словаря."""
        data = {
            "improvement_id": "improvement_004",
            "name": "Система подачи предложений",
            "is_implemented": False,
            "implementation_cost": 30000,
            "efficiency_gain": 0.10,
        }

        improvement = LeanImprovement.from_dict(data)

        assert improvement.improvement_id == "improvement_004"
        assert improvement.name == "Система подачи предложений"
        assert improvement.is_implemented is False
        assert improvement.implementation_cost == 30000
        assert improvement.efficiency_gain == 0.10

    def test_from_dict_with_missing_fields(self):
        """Тест создания из словаря с отсутствующими полями."""
        data = {
            "improvement_id": "improvement_005",
            "name": "Улучшение",
        }

        improvement = LeanImprovement.from_dict(data)

        assert improvement.improvement_id == "improvement_005"
        assert improvement.name == "Улучшение"
        # Отсутствующие поля должны иметь значения по умолчанию
        assert improvement.is_implemented is False
        assert improvement.implementation_cost == 0
        assert improvement.efficiency_gain == 0.0

    def test_from_dict_with_none_id(self):
        """Тест создания из словаря когда improvement_id отсутствует."""
        data = {
            "name": "Улучшение",
            "is_implemented": True,
        }

        improvement = LeanImprovement.from_dict(data)

        assert improvement.improvement_id == ""  # None преобразуется в ""
        assert improvement.name == "Улучшение"
        assert improvement.is_implemented is True

    def test_from_dict_empty_dict(self):
        """Тест создания из пустого словаря."""
        data = {}

        improvement = LeanImprovement.from_dict(data)

        assert improvement.improvement_id == ""
        assert improvement.name == ""
        assert improvement.is_implemented is False
        assert improvement.implementation_cost == 0
        assert improvement.efficiency_gain == 0.0

    def test_to_redis_dict(self):
        """Тест сериализации в словарь для Redis."""
        improvement = LeanImprovement(
            improvement_id="improvement_006",
            name="LEAN улучшение",
            is_implemented=True,
            implementation_cost=100000,
            efficiency_gain=0.25,
        )

        result = improvement.to_redis_dict()

        assert isinstance(result, dict)
        assert result["improvement_id"] == "improvement_006"
        assert result["name"] == "LEAN улучшение"
        assert result["is_implemented"] is True
        assert result["implementation_cost"] == 100000
        assert result["efficiency_gain"] == 0.25
        assert result["_type"] == "LeanImprovement"

    def test_to_redis_dict_exclude_none(self):
        """Тест что None поля исключаются при сериализации."""
        improvement = LeanImprovement(
            improvement_id="",
            name="Улучшение",
        )

        result = improvement.to_redis_dict(exclude_none=True)

        # improvement_id будет None в to_dict, но при exclude_none будет исключен
        # Но так как мы используем to_redis_dict, который использует базовую сериализацию,
        # пустая строка останется пустой строкой
        assert "improvement_id" in result
        assert result["improvement_id"] == ""
        assert "name" in result
        assert "_type" in result

    def test_to_redis_json(self):
        """Тест сериализации в JSON для Redis."""
        improvement = LeanImprovement(
            improvement_id="improvement_007",
            name="Оптимизация процессов",
            is_implemented=True,
            implementation_cost=80000,
            efficiency_gain=0.18,
        )

        result = improvement.to_redis_json()

        assert isinstance(result, str)
        parsed = json.loads(result)

        assert parsed["improvement_id"] == "improvement_007"
        assert parsed["name"] == "Оптимизация процессов"
        assert parsed["is_implemented"] is True
        assert parsed["implementation_cost"] == 80000
        assert parsed["efficiency_gain"] == 0.18
        assert parsed["_type"] == "LeanImprovement"

    def test_to_redis_json_with_indent(self):
        """Тест форматированного JSON."""
        improvement = LeanImprovement(
            improvement_id="improvement_008",
            name="Тестовое улучшение",
        )

        result = improvement.to_redis_json(indent=2)

        assert isinstance(result, str)
        assert "\n" in result  # Есть форматирование
        parsed = json.loads(result)
        assert parsed["improvement_id"] == "improvement_008"

    def test_is_implemented_boolean(self):
        """Тест булевого поля is_implemented."""
        improvement_false = LeanImprovement(is_implemented=False)
        assert improvement_false.is_implemented is False

        improvement_true = LeanImprovement(is_implemented=True)
        assert improvement_true.is_implemented is True

        # Проверка что можно изменить
        improvement_false.is_implemented = True
        assert improvement_false.is_implemented is True

    def test_implementation_cost_edge_cases(self):
        """Тест граничных значений стоимости внедрения."""
        improvement_zero = LeanImprovement(implementation_cost=0)
        assert improvement_zero.implementation_cost == 0

        improvement_large = LeanImprovement(implementation_cost=999999999)
        assert improvement_large.implementation_cost == 999999999

        improvement_negative = LeanImprovement(implementation_cost=-1000)
        assert improvement_negative.implementation_cost == -1000

    def test_efficiency_gain_edge_cases(self):
        """Тест граничных значений прироста эффективности."""
        improvement_zero = LeanImprovement(efficiency_gain=0.0)
        assert improvement_zero.efficiency_gain == 0.0

        improvement_one = LeanImprovement(efficiency_gain=1.0)
        assert improvement_one.efficiency_gain == 1.0

        improvement_negative = LeanImprovement(efficiency_gain=-0.1)
        assert improvement_negative.efficiency_gain == -0.1

        improvement_over_one = LeanImprovement(efficiency_gain=2.5)
        assert improvement_over_one.efficiency_gain == 2.5

        improvement_small = LeanImprovement(efficiency_gain=0.001)
        assert improvement_small.efficiency_gain == 0.001

    def test_efficiency_gain_float_precision(self):
        """Тест точности float значений."""
        improvement = LeanImprovement(efficiency_gain=0.123456789)

        result = improvement.to_redis_dict()
        assert isinstance(result["efficiency_gain"], float)
        assert result["efficiency_gain"] == 0.123456789

    def test_unicode_names(self):
        """Тест работы с unicode символами в названии."""
        improvement = LeanImprovement(
            improvement_id="improvement_unicode",
            name="Улучшение с русскими символами 🎉 и эмодзи",
        )

        result = improvement.to_redis_dict()

        assert result["name"] == "Улучшение с русскими символами 🎉 и эмодзи"

        json_result = improvement.to_redis_json()
        parsed = json.loads(json_result)
        assert parsed["name"] == "Улучшение с русскими символами 🎉 и эмодзи"

    def test_round_trip_serialization(self):
        """Тест полного цикла: to_dict -> from_dict."""
        original = LeanImprovement(
            improvement_id="improvement_roundtrip",
            name="Круговая проверка",
            is_implemented=True,
            implementation_cost=60000,
            efficiency_gain=0.12,
        )

        # Преобразуем в словарь и обратно
        data = original.to_dict()
        restored = LeanImprovement.from_dict(data)

        # Сравниваем поля (кроме improvement_id, который может стать None)
        assert restored.name == original.name
        assert restored.is_implemented == original.is_implemented
        assert restored.implementation_cost == original.implementation_cost
        assert restored.efficiency_gain == original.efficiency_gain

    def test_round_trip_redis_serialization(self):
        """Тест полного цикла: to_redis_dict -> from_dict."""
        original = LeanImprovement(
            improvement_id="improvement_redis",
            name="Redis проверка",
            is_implemented=False,
            implementation_cost=40000,
            efficiency_gain=0.08,
        )

        # Преобразуем в redis dict
        redis_dict = original.to_redis_dict()
        # Убираем служебное поле _type для from_dict
        redis_dict.pop("_type", None)

        # Преобразуем обратно
        restored = LeanImprovement.from_dict(redis_dict)

        assert restored.improvement_id == original.improvement_id
        assert restored.name == original.name
        assert restored.is_implemented == original.is_implemented
        assert restored.implementation_cost == original.implementation_cost
        assert restored.efficiency_gain == original.efficiency_gain

    def test_complex_scenario(self):
        """Тест комплексного сценария использования."""
        # Создаем улучшение
        improvement = LeanImprovement(
            improvement_id="improvement_complex",
            name="Комплексное улучшение",
            is_implemented=False,
            implementation_cost=90000,
            efficiency_gain=0.22,
        )

        # Проверяем начальное состояние
        assert improvement.is_implemented is False

        # Изменяем состояние
        improvement.is_implemented = True
        improvement.implementation_cost = 95000
        improvement.efficiency_gain = 0.25

        # Проверяем изменения
        assert improvement.is_implemented is True
        assert improvement.implementation_cost == 95000
        assert improvement.efficiency_gain == 0.25

        # Сериализуем
        redis_dict = improvement.to_redis_dict()
        assert redis_dict["is_implemented"] is True
        assert redis_dict["implementation_cost"] == 95000
        assert redis_dict["efficiency_gain"] == 0.25

        # JSON сериализация
        json_result = improvement.to_redis_json()
        parsed = json.loads(json_result)
        assert parsed["is_implemented"] is True

    def test_from_dict_with_none_values(self):
        """Тест создания из словаря с None значениями."""
        data = {
            "improvement_id": None,
            "name": None,
            "is_implemented": None,
            "implementation_cost": None,
            "efficiency_gain": None,
        }

        improvement = LeanImprovement.from_dict(data)

        assert improvement.improvement_id == ""  # None -> "" через or ""
        assert improvement.name == ""
        assert (
            improvement.is_implemented is False
        )  # None -> False через get(..., False)
        assert improvement.implementation_cost == 0  # None -> 0 через get(..., 0)
        assert improvement.efficiency_gain == 0.0  # None -> 0.0 через get(..., 0.0)

    def test_from_dict_with_string_boolean(self):
        """Тест создания из словаря когда bool представлен как строка."""
        data = {
            "improvement_id": "improvement_str_bool",
            "name": "Тест",
            "is_implemented": "true",  # Строка вместо bool
        }

        improvement = LeanImprovement.from_dict(data)

        # Строка "true" будет считаться True в Python
        assert improvement.is_implemented == "true"  # Не преобразуется автоматически
        assert improvement.name == "Тест"

    def test_set_is_implemented_true(self):
        """Тест установки статуса реализации как реализованного."""
        improvement = LeanImprovement()

        improvement.set_is_implemented(True)

        assert improvement.is_implemented is True

    def test_set_is_implemented_false(self):
        """Тест установки статуса реализации как не реализованного."""
        improvement = LeanImprovement(is_implemented=True)

        improvement.set_is_implemented(False)

        assert improvement.is_implemented is False

    def test_set_is_implemented_toggle(self):
        """Тест переключения статуса реализации."""
        improvement = LeanImprovement()

        improvement.set_is_implemented(True)
        assert improvement.is_implemented is True

        improvement.set_is_implemented(False)
        assert improvement.is_implemented is False

        improvement.set_is_implemented(True)
        assert improvement.is_implemented is True

    def test_set_is_implemented_updates_existing(self):
        """Тест обновления существующего статуса."""
        improvement = LeanImprovement(is_implemented=False)

        improvement.set_is_implemented(True)
        assert improvement.is_implemented is True

        improvement.set_is_implemented(False)
        assert improvement.is_implemented is False

    def test_set_is_implemented_preserves_other_fields(self):
        """Тест что set_is_implemented не изменяет другие поля."""
        improvement = LeanImprovement(
            improvement_id="improvement_test",
            name="Тестовое улучшение",
            is_implemented=False,
            implementation_cost=50000,
            efficiency_gain=0.15,
        )

        improvement.set_is_implemented(True)

        assert improvement.is_implemented is True
        assert improvement.improvement_id == "improvement_test"
        assert improvement.name == "Тестовое улучшение"
        assert improvement.implementation_cost == 50000
        assert improvement.efficiency_gain == 0.15

    def test_lean_improvement_mutable(self):
        """Тест что LeanImprovement не frozen (можно изменять поля напрямую)."""
        improvement = LeanImprovement()

        improvement.improvement_id = "new_id"
        improvement.name = "Новое название"
        improvement.is_implemented = True
        improvement.implementation_cost = 100000
        improvement.efficiency_gain = 0.3

        assert improvement.improvement_id == "new_id"
        assert improvement.name == "Новое название"
        assert improvement.is_implemented is True
        assert improvement.implementation_cost == 100000
        assert improvement.efficiency_gain == 0.3

    def test_lean_improvement_comparison(self):
        """Тест сравнения улучшений."""
        improvement1 = LeanImprovement(
            improvement_id="improvement_001",
            name="Улучшение",
            is_implemented=True,
            implementation_cost=50000,
            efficiency_gain=0.15,
        )
        improvement2 = LeanImprovement(
            improvement_id="improvement_001",
            name="Улучшение",
            is_implemented=True,
            implementation_cost=50000,
            efficiency_gain=0.15,
        )
        improvement3 = LeanImprovement(
            improvement_id="improvement_002",
            name="Другое улучшение",
            is_implemented=False,
            implementation_cost=30000,
            efficiency_gain=0.10,
        )

        # По умолчанию dataclass сравнивает все поля
        assert improvement1 == improvement2  # Все поля совпадают
        assert improvement1 != improvement3  # Разные ID и другие поля
