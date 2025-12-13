"""Тесты для domain/equipment.py"""

import pytest
import json

from domain.equipment import Equipment


class TestEquipment:
    """Тесты для класса Equipment."""

    def test_equipment_creation_with_defaults(self):
        """Тест создания оборудования со значениями по умолчанию."""
        equipment = Equipment()

        assert equipment.equipment_id == ""
        assert equipment.name == ""
        assert equipment.equipment_type == ""
        assert equipment.reliability == 0.0
        assert equipment.maintenance_period == 0
        assert equipment.maintenance_cost == 0
        assert equipment.cost == 0
        assert equipment.repair_cost == 0
        assert equipment.repair_time == 0

    def test_equipment_creation_with_values(self):
        """Тест создания оборудования с заданными значениями."""
        equipment = Equipment(
            equipment_id="equip_001",
            name="Токарный станок",
            equipment_type="CNC",
            reliability=0.95,
            maintenance_period=30,
            maintenance_cost=5000,
            cost=100000,
            repair_cost=15000,
            repair_time=24,
        )

        assert equipment.equipment_id == "equip_001"
        assert equipment.name == "Токарный станок"
        assert equipment.equipment_type == "CNC"
        assert equipment.reliability == 0.95
        assert equipment.maintenance_period == 30
        assert equipment.maintenance_cost == 5000
        assert equipment.cost == 100000
        assert equipment.repair_cost == 15000
        assert equipment.repair_time == 24

    def test_equipment_partial_initialization(self):
        """Тест создания оборудования с частичной инициализацией."""
        equipment = Equipment(
            equipment_id="equip_002",
            name="Фрезерный станок",
            reliability=0.9,
        )

        assert equipment.equipment_id == "equip_002"
        assert equipment.name == "Фрезерный станок"
        assert equipment.reliability == 0.9
        # Остальные поля должны иметь значения по умолчанию
        assert equipment.equipment_type == ""
        assert equipment.maintenance_period == 0
        assert equipment.maintenance_cost == 0

    def test_set_maintenance_period(self):
        """Тест установки периода обслуживания."""
        equipment = Equipment()

        equipment.set_maintenance_period(45)
        assert equipment.maintenance_period == 45

        equipment.set_maintenance_period(0)
        assert equipment.maintenance_period == 0

        equipment.set_maintenance_period(365)
        assert equipment.maintenance_period == 365

    def test_set_maintenance_period_negative(self):
        """Тест установки отрицательного периода обслуживания."""
        equipment = Equipment()

        # Метод не проверяет отрицательные значения на уровне домена
        equipment.set_maintenance_period(-10)
        assert equipment.maintenance_period == -10

    def test_set_maintenance_period_updates_existing(self):
        """Тест обновления существующего периода обслуживания."""
        equipment = Equipment(maintenance_period=30)
        assert equipment.maintenance_period == 30

        equipment.set_maintenance_period(60)
        assert equipment.maintenance_period == 60

    def test_equipment_mutable(self):
        """Тест что Equipment не frozen (можно изменять поля напрямую)."""
        equipment = Equipment()

        equipment.equipment_id = "new_id"
        equipment.name = "New Name"
        equipment.reliability = 0.99

        assert equipment.equipment_id == "new_id"
        assert equipment.name == "New Name"
        assert equipment.reliability == 0.99

    def test_equipment_to_redis_dict(self):
        """Тест сериализации Equipment в словарь для Redis."""
        equipment = Equipment(
            equipment_id="equip_003",
            name="Сварочный аппарат",
            equipment_type="Welding",
            reliability=0.88,
            maintenance_period=20,
            maintenance_cost=3000,
            cost=50000,
            repair_cost=10000,
            repair_time=12,
        )

        result = equipment.to_redis_dict()

        assert isinstance(result, dict)
        assert result["equipment_id"] == "equip_003"
        assert result["name"] == "Сварочный аппарат"
        assert result["equipment_type"] == "Welding"
        assert result["reliability"] == 0.88
        assert result["maintenance_period"] == 20
        assert result["maintenance_cost"] == 3000
        assert result["cost"] == 50000
        assert result["repair_cost"] == 10000
        assert result["repair_time"] == 12
        assert result["_type"] == "Equipment"

    def test_equipment_to_redis_dict_exclude_none(self):
        """Тест что None поля исключаются при сериализации."""
        equipment = Equipment(
            equipment_id="equip_004",
            name="Оборудование",
            reliability=0.9,
        )

        result = equipment.to_redis_dict(exclude_none=True)

        # Все поля со значениями по умолчанию (не None) должны быть включены
        assert "equipment_id" in result
        assert "name" in result
        assert "reliability" in result
        assert "maintenance_period" in result  # 0 не является None
        assert "_type" in result

    def test_equipment_to_redis_dict_with_all_fields_none(self):
        """Тест сериализации когда все строковые поля пустые."""
        equipment = Equipment()

        result = equipment.to_redis_dict(exclude_none=True)

        # Пустые строки не являются None, поэтому они должны быть включены
        assert "equipment_id" in result
        assert result["equipment_id"] == ""
        assert "name" in result
        assert result["name"] == ""
        assert "equipment_type" in result
        assert result["equipment_type"] == ""
        assert "_type" in result

    def test_equipment_to_redis_json(self):
        """Тест сериализации Equipment в JSON для Redis."""
        equipment = Equipment(
            equipment_id="equip_005",
            name="Шлифовальный станок",
            equipment_type="Grinder",
            reliability=0.92,
            maintenance_period=15,
            maintenance_cost=2500,
            cost=75000,
            repair_cost=12000,
            repair_time=18,
        )

        result = equipment.to_redis_json()

        assert isinstance(result, str)
        parsed = json.loads(result)

        assert parsed["equipment_id"] == "equip_005"
        assert parsed["name"] == "Шлифовальный станок"
        assert parsed["equipment_type"] == "Grinder"
        assert parsed["reliability"] == 0.92
        assert parsed["maintenance_period"] == 15
        assert parsed["maintenance_cost"] == 2500
        assert parsed["cost"] == 75000
        assert parsed["repair_cost"] == 12000
        assert parsed["repair_time"] == 18
        assert parsed["_type"] == "Equipment"

    def test_equipment_to_redis_json_with_indent(self):
        """Тест форматированного JSON."""
        equipment = Equipment(
            equipment_id="equip_006",
            name="Тестовое оборудование",
        )

        result = equipment.to_redis_json(indent=2)

        assert isinstance(result, str)
        assert "\n" in result  # Есть форматирование
        parsed = json.loads(result)
        assert parsed["equipment_id"] == "equip_006"

    def test_equipment_reliability_edge_cases(self):
        """Тест граничных значений надежности."""
        # Минимальная надежность
        equipment_min = Equipment(reliability=0.0)
        assert equipment_min.reliability == 0.0

        # Максимальная надежность
        equipment_max = Equipment(reliability=1.0)
        assert equipment_max.reliability == 1.0

        # Надежность больше 1.0 (может быть в реальных данных)
        equipment_over = Equipment(reliability=1.5)
        assert equipment_over.reliability == 1.5

        # Отрицательная надежность
        equipment_neg = Equipment(reliability=-0.5)
        assert equipment_neg.reliability == -0.5

    def test_equipment_costs_edge_cases(self):
        """Тест граничных значений стоимостных полей."""
        equipment = Equipment(
            maintenance_cost=0,
            cost=0,
            repair_cost=0,
        )

        assert equipment.maintenance_cost == 0
        assert equipment.cost == 0
        assert equipment.repair_cost == 0

        equipment_large = Equipment(
            maintenance_cost=999999999,
            cost=999999999,
            repair_cost=999999999,
        )

        assert equipment_large.maintenance_cost == 999999999
        assert equipment_large.cost == 999999999
        assert equipment_large.repair_cost == 999999999

    def test_equipment_time_fields_edge_cases(self):
        """Тест граничных значений временных полей."""
        equipment = Equipment(
            maintenance_period=0,
            repair_time=0,
        )

        assert equipment.maintenance_period == 0
        assert equipment.repair_time == 0

        equipment_max = Equipment(
            maintenance_period=365 * 10,  # 10 лет
            repair_time=168,  # Неделя в часах
        )

        assert equipment_max.maintenance_period == 3650
        assert equipment_max.repair_time == 168

    def test_equipment_unicode_names(self):
        """Тест работы с unicode символами в названии."""
        equipment = Equipment(
            equipment_id="equip_unicode",
            name="Оборудование с русскими символами 🎉",
            equipment_type="Тип оборудования",
        )

        result = equipment.to_redis_dict()

        assert result["name"] == "Оборудование с русскими символами 🎉"
        assert result["equipment_type"] == "Тип оборудования"

        json_result = equipment.to_redis_json()
        parsed = json.loads(json_result)
        assert parsed["name"] == "Оборудование с русскими символами 🎉"

    def test_equipment_string_fields_empty_and_whitespace(self):
        """Тест работы с пустыми строками и пробелами."""
        equipment = Equipment(
            equipment_id="  ",
            name="   ",
            equipment_type="",
        )

        result = equipment.to_redis_dict()

        assert result["equipment_id"] == "  "
        assert result["name"] == "   "
        assert result["equipment_type"] == ""

    def test_equipment_float_precision(self):
        """Тест точности float значений."""
        equipment = Equipment(
            reliability=0.123456789,
        )

        result = equipment.to_redis_dict()
        # Проверяем что float сериализуется корректно
        assert isinstance(result["reliability"], float)
        assert result["reliability"] == 0.123456789

    def test_equipment_complex_scenario(self):
        """Тест комплексного сценария использования."""
        # Создаем оборудование
        equipment = Equipment(
            equipment_id="equip_complex_001",
            name="Сложное оборудование для производства",
            equipment_type="Production Line",
            reliability=0.97,
            maintenance_period=45,
            maintenance_cost=15000,
            cost=500000,
            repair_cost=50000,
            repair_time=48,
        )

        # Изменяем период обслуживания
        equipment.set_maintenance_period(60)

        # Проверяем изменения
        assert equipment.maintenance_period == 60

        # Сериализуем
        redis_dict = equipment.to_redis_dict()
        assert redis_dict["maintenance_period"] == 60

        # Изменяем другие поля напрямую (так как класс не frozen)
        equipment.reliability = 0.99
        equipment.cost = 600000

        # Проверяем что изменения сохранились
        assert equipment.reliability == 0.99
        assert equipment.cost == 600000

        # Финальная сериализация
        final_dict = equipment.to_redis_dict()
        assert final_dict["reliability"] == 0.99
        assert final_dict["cost"] == 600000
        assert final_dict["maintenance_period"] == 60

    def test_equipment_comparison_by_id(self):
        """Тест что Equipment сравнивается только по ID (__eq__ переопределен)."""
        equipment1 = Equipment(equipment_id="equip_001")
        equipment2 = Equipment(equipment_id="equip_001")
        equipment3 = Equipment(equipment_id="equip_002")

        # Equipment сравнивается только по equipment_id (не по всем полям)
        assert equipment1 == equipment2  # Одинаковые ID
        assert equipment1 != equipment3  # Разные ID

        # Даже с разными именами, если ID одинаковый - объекты равны
        equipment4 = Equipment(equipment_id="equip_001", name="Name1")
        equipment5 = Equipment(equipment_id="equip_001", name="Name2")

        assert equipment4 == equipment5  # Одинаковые ID, несмотря на разные имена
