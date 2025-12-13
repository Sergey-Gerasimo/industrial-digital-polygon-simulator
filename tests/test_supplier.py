"""Тесты для domain/supplier.py"""

import pytest
import json

from domain.supplier import Supplier


class TestSupplier:
    """Тесты для класса Supplier."""

    def test_supplier_creation_with_defaults(self):
        """Тест создания поставщика со значениями по умолчанию."""
        supplier = Supplier()

        assert supplier.supplier_id == ""
        assert supplier.name == ""
        assert supplier.product_name == ""
        assert supplier.material_type == ""
        assert supplier.delivery_period == 0
        assert supplier.special_delivery_period == 0
        assert supplier.reliability == 0.0
        assert supplier.product_quality == 0.0
        assert supplier.cost == 0
        assert supplier.special_delivery_cost == 0
        # Доменные поля
        assert supplier.quality_inspection_enabled is False
        assert supplier.delivery_period_days == 7

    def test_supplier_creation_with_values(self):
        """Тест создания поставщика с заданными значениями."""
        supplier = Supplier(
            supplier_id="supplier_001",
            name="ООО Поставщик",
            product_name="Сталь",
            material_type="Металл",
            delivery_period=30,
            special_delivery_period=14,
            reliability=0.95,
            product_quality=0.92,
            cost=50000,
            special_delivery_cost=75000,
        )

        assert supplier.supplier_id == "supplier_001"
        assert supplier.name == "ООО Поставщик"
        assert supplier.product_name == "Сталь"
        assert supplier.material_type == "Металл"
        assert supplier.delivery_period == 30
        assert supplier.special_delivery_period == 14
        assert supplier.reliability == 0.95
        assert supplier.product_quality == 0.92
        assert supplier.cost == 50000
        assert supplier.special_delivery_cost == 75000
        # Доменные поля по умолчанию
        assert supplier.quality_inspection_enabled is False
        assert supplier.delivery_period_days == 7

    def test_supplier_partial_initialization(self):
        """Тест создания поставщика с частичной инициализацией."""
        supplier = Supplier(
            supplier_id="supplier_002",
            name="ИП Иванов",
            reliability=0.88,
        )

        assert supplier.supplier_id == "supplier_002"
        assert supplier.name == "ИП Иванов"
        assert supplier.reliability == 0.88
        # Остальные поля должны иметь значения по умолчанию
        assert supplier.product_name == ""
        assert supplier.material_type == ""
        assert supplier.delivery_period == 0
        assert supplier.cost == 0

    def test_is_special_delivery_false_when_special_less(self):
        """Тест свойства is_special_delivery когда special_delivery_period < delivery_period."""
        supplier = Supplier(
            delivery_period=30,
            special_delivery_period=14,
        )

        assert (
            supplier.is_special_delivery is False
        )  # 14 >= 30 = False, значит обычная доставка

    def test_is_special_delivery_true_when_equal(self):
        """Тест свойства is_special_delivery когда периоды равны."""
        supplier = Supplier(
            delivery_period=30,
            special_delivery_period=30,
        )

        assert supplier.is_special_delivery is True  # 30 >= 30 = True

    def test_is_special_delivery_true_when_special_greater(self):
        """Тест свойства is_special_delivery когда special_delivery_period > delivery_period."""
        supplier = Supplier(
            delivery_period=30,
            special_delivery_period=45,
        )

        assert (
            supplier.is_special_delivery is True
        )  # 45 >= 30 = True, значит специальная доставка

    def test_is_special_delivery_with_zero_periods(self):
        """Тест свойства is_special_delivery с нулевыми периодами."""
        supplier = Supplier()

        assert supplier.is_special_delivery is True  # 0 >= 0

    def test_set_quality_inspection_enable(self):
        """Тест включения контроля качества."""
        supplier = Supplier()

        supplier.set_quality_inspection(True)

        assert supplier.quality_inspection_enabled is True

    def test_set_quality_inspection_disable(self):
        """Тест выключения контроля качества."""
        supplier = Supplier(quality_inspection_enabled=True)

        supplier.set_quality_inspection(False)

        assert supplier.quality_inspection_enabled is False

    def test_set_quality_inspection_toggle(self):
        """Тест переключения контроля качества."""
        supplier = Supplier()

        supplier.set_quality_inspection(True)
        assert supplier.quality_inspection_enabled is True

        supplier.set_quality_inspection(False)
        assert supplier.quality_inspection_enabled is False

        supplier.set_quality_inspection(True)
        assert supplier.quality_inspection_enabled is True

    def test_set_delivery_period(self):
        """Тест установки периода поставок."""
        supplier = Supplier()

        supplier.set_delivery_period(14)
        assert supplier.delivery_period_days == 14

        supplier.set_delivery_period(0)
        assert supplier.delivery_period_days == 0

        supplier.set_delivery_period(365)
        assert supplier.delivery_period_days == 365

    def test_set_delivery_period_updates_existing(self):
        """Тест обновления существующего периода поставок."""
        supplier = Supplier(delivery_period_days=7)

        supplier.set_delivery_period(30)
        assert supplier.delivery_period_days == 30

    def test_set_delivery_period_negative_raises_error(self):
        """Тест что отрицательный период поставок вызывает ValueError."""
        supplier = Supplier()

        with pytest.raises(
            ValueError, match="Период поставок не может быть отрицательным"
        ):
            supplier.set_delivery_period(-1)

        with pytest.raises(
            ValueError, match="Период поставок не может быть отрицательным"
        ):
            supplier.set_delivery_period(-100)

        # Значение не должно измениться
        assert supplier.delivery_period_days == 7

    def test_set_delivery_period_zero_allowed(self):
        """Тест что нулевой период поставок разрешен."""
        supplier = Supplier()

        supplier.set_delivery_period(0)
        assert supplier.delivery_period_days == 0

    def test_supplier_mutable(self):
        """Тест что Supplier не frozen (можно изменять поля напрямую)."""
        supplier = Supplier()

        supplier.supplier_id = "new_id"
        supplier.name = "Новое название"
        supplier.reliability = 0.99
        supplier.quality_inspection_enabled = True
        supplier.delivery_period_days = 21

        assert supplier.supplier_id == "new_id"
        assert supplier.name == "Новое название"
        assert supplier.reliability == 0.99
        assert supplier.quality_inspection_enabled is True
        assert supplier.delivery_period_days == 21

    def test_supplier_to_redis_dict(self):
        """Тест сериализации Supplier в словарь для Redis."""
        supplier = Supplier(
            supplier_id="supplier_003",
            name="ООО МеталлСнаб",
            product_name="Алюминий",
            material_type="Металл",
            delivery_period=20,
            special_delivery_period=10,
            reliability=0.93,
            product_quality=0.90,
            cost=60000,
            special_delivery_cost=90000,
        )

        result = supplier.to_redis_dict()

        assert isinstance(result, dict)
        assert result["supplier_id"] == "supplier_003"
        assert result["name"] == "ООО МеталлСнаб"
        assert result["product_name"] == "Алюминий"
        assert result["material_type"] == "Металл"
        assert result["delivery_period"] == 20
        assert result["special_delivery_period"] == 10
        assert result["reliability"] == 0.93
        assert result["product_quality"] == 0.90
        assert result["cost"] == 60000
        assert result["special_delivery_cost"] == 90000
        assert result["_type"] == "Supplier"

    def test_supplier_to_redis_dict_includes_domain_fields(self):
        """Тест что доменные поля включаются в сериализацию."""
        supplier = Supplier(
            supplier_id="supplier_004",
            quality_inspection_enabled=True,
            delivery_period_days=14,
        )

        result = supplier.to_redis_dict()

        # Доменные поля должны быть в сериализации
        assert "quality_inspection_enabled" in result
        assert result["quality_inspection_enabled"] is True
        assert "delivery_period_days" in result
        assert result["delivery_period_days"] == 14
        # Стандартные поля также должны быть
        assert result["supplier_id"] == "supplier_004"
        assert result["_type"] == "Supplier"

    def test_supplier_to_redis_json(self):
        """Тест сериализации Supplier в JSON для Redis."""
        supplier = Supplier(
            supplier_id="supplier_005",
            name="Поставщик Тест",
            reliability=0.85,
            cost=40000,
        )

        result = supplier.to_redis_json()

        assert isinstance(result, str)
        parsed = json.loads(result)

        assert parsed["supplier_id"] == "supplier_005"
        assert parsed["name"] == "Поставщик Тест"
        assert parsed["reliability"] == 0.85
        assert parsed["cost"] == 40000
        assert parsed["_type"] == "Supplier"

    def test_supplier_to_redis_json_with_indent(self):
        """Тест форматированного JSON."""
        supplier = Supplier(
            supplier_id="supplier_006",
            name="Тестовый поставщик",
        )

        result = supplier.to_redis_json(indent=2)

        assert isinstance(result, str)
        assert "\n" in result  # Есть форматирование
        parsed = json.loads(result)
        assert parsed["supplier_id"] == "supplier_006"

    def test_supplier_reliability_edge_cases(self):
        """Тест граничных значений надежности."""
        supplier_min = Supplier(reliability=0.0)
        assert supplier_min.reliability == 0.0

        supplier_max = Supplier(reliability=1.0)
        assert supplier_max.reliability == 1.0

        supplier_over = Supplier(reliability=1.5)
        assert supplier_over.reliability == 1.5

        supplier_neg = Supplier(reliability=-0.5)
        assert supplier_neg.reliability == -0.5

    def test_supplier_product_quality_edge_cases(self):
        """Тест граничных значений качества продукции."""
        supplier_min = Supplier(product_quality=0.0)
        assert supplier_min.product_quality == 0.0

        supplier_max = Supplier(product_quality=1.0)
        assert supplier_max.product_quality == 1.0

        supplier_over = Supplier(product_quality=1.2)
        assert supplier_over.product_quality == 1.2

    def test_supplier_costs_edge_cases(self):
        """Тест граничных значений стоимостных полей."""
        supplier = Supplier(
            cost=0,
            special_delivery_cost=0,
        )

        assert supplier.cost == 0
        assert supplier.special_delivery_cost == 0

        supplier_large = Supplier(
            cost=999999999,
            special_delivery_cost=999999999,
        )

        assert supplier_large.cost == 999999999
        assert supplier_large.special_delivery_cost == 999999999

    def test_supplier_periods_edge_cases(self):
        """Тест граничных значений периодов доставки."""
        supplier = Supplier(
            delivery_period=0,
            special_delivery_period=0,
        )

        assert supplier.delivery_period == 0
        assert supplier.special_delivery_period == 0

        supplier_max = Supplier(
            delivery_period=365 * 10,  # 10 лет
            special_delivery_period=365 * 5,  # 5 лет
        )

        assert supplier_max.delivery_period == 3650
        assert supplier_max.special_delivery_period == 1825

    def test_supplier_unicode_names(self):
        """Тест работы с unicode символами в названиях."""
        supplier = Supplier(
            supplier_id="supplier_unicode",
            name="ООО Поставщик с русскими символами 🎉",
            product_name="Материал с эмодзи 😊",
        )

        result = supplier.to_redis_dict()

        assert result["name"] == "ООО Поставщик с русскими символами 🎉"
        assert result["product_name"] == "Материал с эмодзи 😊"

        json_result = supplier.to_redis_json()
        parsed = json.loads(json_result)
        assert parsed["name"] == "ООО Поставщик с русскими символами 🎉"

    def test_supplier_string_fields_empty_and_whitespace(self):
        """Тест работы с пустыми строками и пробелами."""
        supplier = Supplier(
            supplier_id="  ",
            name="   ",
            product_name="",
            material_type="",
        )

        result = supplier.to_redis_dict()

        assert result["supplier_id"] == "  "
        assert result["name"] == "   "
        assert result["product_name"] == ""
        assert result["material_type"] == ""

    def test_supplier_float_precision(self):
        """Тест точности float значений."""
        supplier = Supplier(
            reliability=0.123456789,
            product_quality=0.987654321,
        )

        result = supplier.to_redis_dict()
        assert isinstance(result["reliability"], float)
        assert result["reliability"] == 0.123456789
        assert isinstance(result["product_quality"], float)
        assert result["product_quality"] == 0.987654321

    def test_supplier_complex_scenario(self):
        """Тест комплексного сценария использования."""
        # Создаем поставщика
        supplier = Supplier(
            supplier_id="supplier_complex_001",
            name="Комплексный поставщик",
            product_name="Сталь высокого качества",
            material_type="Металл",
            delivery_period=30,
            special_delivery_period=14,
            reliability=0.97,
            product_quality=0.95,
            cost=100000,
            special_delivery_cost=150000,
        )

        # Проверяем свойство is_special_delivery
        # special_delivery_period=14, delivery_period=30 => 14 >= 30 = False
        # Значит обычная доставка
        assert supplier.is_special_delivery is False

        # Включаем контроль качества
        supplier.set_quality_inspection(True)
        assert supplier.quality_inspection_enabled is True

        # Устанавливаем период поставок
        supplier.set_delivery_period(21)
        assert supplier.delivery_period_days == 21

        # Сериализуем
        redis_dict = supplier.to_redis_dict()
        assert redis_dict["reliability"] == 0.97
        assert redis_dict["delivery_period"] == 30

        # Изменяем поля напрямую
        supplier.reliability = 0.99
        supplier.cost = 120000

        # Проверяем изменения
        assert supplier.reliability == 0.99
        assert supplier.cost == 120000

        # Выключаем контроль качества
        supplier.set_quality_inspection(False)
        assert supplier.quality_inspection_enabled is False

        # Обновляем период поставок
        supplier.set_delivery_period(30)
        assert supplier.delivery_period_days == 30

        # Финальная сериализация
        final_dict = supplier.to_redis_dict()
        assert final_dict["reliability"] == 0.99
        assert final_dict["cost"] == 120000

    def test_supplier_domain_fields_in_redis(self):
        """Тест что доменные поля сохраняются в Redis сериализацию."""
        supplier = Supplier(
            supplier_id="supplier_domain_test",
            quality_inspection_enabled=True,
            delivery_period_days=15,
        )

        # Изменяем доменные поля
        supplier.set_quality_inspection(False)
        supplier.set_delivery_period(20)

        # Сериализуем
        redis_dict = supplier.to_redis_dict()

        # Доменные поля должны присутствовать в сериализации
        assert "quality_inspection_enabled" in redis_dict
        assert redis_dict["quality_inspection_enabled"] is False
        assert "delivery_period_days" in redis_dict
        assert redis_dict["delivery_period_days"] == 20

        # И они должны быть в объекте
        assert supplier.quality_inspection_enabled is False
        assert supplier.delivery_period_days == 20

    def test_supplier_multiple_delivery_scenarios(self):
        """Тест различных сценариев определения специальной доставки."""
        # Специальная доставка (special >= delivery_period)
        special = Supplier(delivery_period=30, special_delivery_period=45)
        assert special.is_special_delivery is True  # 45 >= 30

        # Обычная доставка (special < delivery_period)
        normal = Supplier(delivery_period=30, special_delivery_period=14)
        assert normal.is_special_delivery is False  # 14 >= 30 = False

        # Равные периоды (считается специальной)
        equal = Supplier(delivery_period=30, special_delivery_period=30)
        assert equal.is_special_delivery is True  # 30 >= 30

    def test_supplier_delivery_period_validation_boundary(self):
        """Тест граничных значений валидации периода поставок."""
        supplier = Supplier()

        # Ноль должен быть разрешен
        supplier.set_delivery_period(0)
        assert supplier.delivery_period_days == 0

        # Отрицательные значения должны вызывать ошибку
        with pytest.raises(ValueError):
            supplier.set_delivery_period(-1)

        # Положительные значения должны работать
        supplier.set_delivery_period(1)
        assert supplier.delivery_period_days == 1

        supplier.set_delivery_period(365)
        assert supplier.delivery_period_days == 365
