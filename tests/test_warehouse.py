"""Тесты для domain/warehouse.py"""

import pytest
import json

from domain.warehouse import Warehouse
from domain.worker import Worker


class TestWarehouse:
    """Тесты для класса Warehouse."""

    def test_warehouse_creation_with_defaults(self):
        """Тест создания склада со значениями по умолчанию."""
        warehouse = Warehouse()

        assert warehouse.warehouse_id == ""
        assert warehouse.inventory_worker is None
        assert warehouse.size == 0
        assert warehouse.materials == {}
        assert warehouse.loading == 0
        assert warehouse.is_full is True  # 0 >= 0

    def test_warehouse_creation_with_values(self):
        """Тест создания склада с заданными значениями."""
        worker = Worker(worker_id="worker_001", name="Иван Иванов")
        warehouse = Warehouse(
            warehouse_id="warehouse_001",
            inventory_worker=worker,
            size=1000,
            materials={"сталь": 500, "алюминий": 300},
        )

        assert warehouse.warehouse_id == "warehouse_001"
        assert warehouse.inventory_worker == worker
        assert warehouse.size == 1000
        assert warehouse.materials == {"сталь": 500, "алюминий": 300}
        assert warehouse.loading == 800  # 500 + 300
        assert warehouse.is_full is False  # 800 < 1000

    def test_warehouse_loading_property(self):
        """Тест свойства loading (вычисляется из materials)."""
        warehouse = Warehouse(size=1000)

        # Пустой склад
        assert warehouse.loading == 0

        # Добавляем материалы
        warehouse.materials["материал1"] = 100
        assert warehouse.loading == 100

        warehouse.materials["материал2"] = 200
        assert warehouse.loading == 300

        warehouse.materials["материал3"] = 150
        assert warehouse.loading == 450

        # Изменяем количество
        warehouse.materials["материал1"] = 50
        assert warehouse.loading == 400  # 50 + 200 + 150

    def test_warehouse_is_full_property(self):
        """Тест свойства is_full."""
        warehouse = Warehouse(size=1000)

        # Пустой склад
        assert warehouse.is_full is False

        # Заполняем частично
        warehouse.materials["материал"] = 500
        assert warehouse.is_full is False  # 500 < 1000

        # Заполняем до предела
        warehouse.materials["материал"] = 1000
        assert warehouse.is_full is True  # 1000 >= 1000

        # Превышаем лимит
        warehouse.materials["материал"] = 1500
        assert warehouse.is_full is True  # 1500 >= 1000

    def test_warehouse_is_full_with_zero_size(self):
        """Тест is_full когда размер склада равен нулю."""
        warehouse = Warehouse(size=0)

        assert warehouse.is_full is True  # 0 >= 0
        warehouse.materials["материал"] = 0
        assert warehouse.is_full is True  # 0 >= 0

    def test_set_inventory_worker(self):
        """Тест установки кладовщика на склад."""
        warehouse = Warehouse()
        worker = Worker(worker_id="worker_001", name="Кладовщик")

        warehouse.set_inventory_worker(worker)

        assert warehouse.inventory_worker == worker
        assert warehouse.inventory_worker.worker_id == "worker_001"
        assert warehouse.inventory_worker.name == "Кладовщик"

    def test_set_inventory_worker_replace(self):
        """Тест замены кладовщика на складе."""
        warehouse = Warehouse()
        worker1 = Worker(worker_id="worker_001", name="Кладовщик 1")
        worker2 = Worker(worker_id="worker_002", name="Кладовщик 2")

        warehouse.set_inventory_worker(worker1)
        assert warehouse.inventory_worker == worker1

        warehouse.set_inventory_worker(worker2)
        assert warehouse.inventory_worker == worker2
        assert warehouse.inventory_worker.name == "Кладовщик 2"

    def test_increase_size(self):
        """Тест увеличения размера склада."""
        warehouse = Warehouse(size=1000)

        warehouse.increase_size(500)
        assert warehouse.size == 1500

        warehouse.increase_size(100)
        assert warehouse.size == 1600

        warehouse.increase_size(0)
        assert warehouse.size == 1600

    def test_increase_size_from_zero(self):
        """Тест увеличения размера склада с нуля."""
        warehouse = Warehouse(size=0)

        warehouse.increase_size(1000)
        assert warehouse.size == 1000

    def test_decrease_size(self):
        """Тест уменьшения размера склада."""
        warehouse = Warehouse(size=1000)

        warehouse.decrease_size(300)
        assert warehouse.size == 700

        warehouse.decrease_size(200)
        assert warehouse.size == 500

    def test_decrease_size_below_zero(self):
        """Тест уменьшения размера ниже нуля (должно стать 0)."""
        warehouse = Warehouse(size=500)

        warehouse.decrease_size(1000)
        assert warehouse.size == 0

        warehouse.decrease_size(100)
        assert warehouse.size == 0  # Не может быть отрицательным

    def test_decrease_size_from_zero(self):
        """Тест уменьшения размера склада, который уже нулевой."""
        warehouse = Warehouse(size=0)

        warehouse.decrease_size(100)
        assert warehouse.size == 0

    def test_add_material(self):
        """Тест добавления материала на склад."""
        warehouse = Warehouse(size=1000)

        warehouse.add_material("сталь", 200)
        assert warehouse.materials["сталь"] == 200
        assert warehouse.loading == 200

        warehouse.add_material("алюминий", 300)
        assert warehouse.materials["алюминий"] == 300
        assert warehouse.loading == 500

        # Добавляем тот же материал
        warehouse.add_material("сталь", 100)
        assert warehouse.materials["сталь"] == 300
        assert warehouse.loading == 600

    def test_add_material_new_material(self):
        """Тест добавления нового материала (не существующего на складе)."""
        warehouse = Warehouse(size=1000)
        warehouse.materials = {"сталь": 500}

        warehouse.add_material("алюминий", 300)
        assert "алюминий" in warehouse.materials
        assert warehouse.materials["алюминий"] == 300
        assert warehouse.loading == 800

    def test_add_material_exact_capacity(self):
        """Тест добавления материала точно до заполнения склада."""
        warehouse = Warehouse(size=1000)
        warehouse.materials = {"сталь": 500}

        warehouse.add_material("алюминий", 500)
        assert warehouse.materials["алюминий"] == 500
        assert warehouse.loading == 1000
        assert warehouse.is_full is True

    def test_add_material_exceeds_capacity_raises_error(self):
        """Тест что добавление материала сверх емкости вызывает ошибку."""
        warehouse = Warehouse(size=1000)
        warehouse.materials = {"сталь": 500}

        with pytest.raises(ValueError, match="На складе нет места"):
            warehouse.add_material("алюминий", 600)

        # Материал не должен быть добавлен
        assert "алюминий" not in warehouse.materials
        assert warehouse.loading == 500

    def test_add_material_exceeds_capacity_exact(self):
        """Тест что добавление материала, который точно превышает лимит, вызывает ошибку."""
        warehouse = Warehouse(size=1000)
        warehouse.materials = {"сталь": 500}

        with pytest.raises(ValueError, match="На складе нет места"):
            warehouse.add_material("сталь", 501)

        # Количество не должно измениться
        assert warehouse.materials["сталь"] == 500
        assert warehouse.loading == 500

    def test_add_material_negative_quantity_raises_error(self):
        """Тест что добавление отрицательного количества вызывает ошибку."""
        warehouse = Warehouse(size=1000)

        with pytest.raises(
            ValueError, match="Количество материала .* не может быть отрицательным"
        ):
            warehouse.add_material("сталь", -100)

        assert "сталь" not in warehouse.materials
        assert warehouse.loading == 0

    def test_add_material_zero_quantity(self):
        """Тест добавления нулевого количества материала."""
        warehouse = Warehouse(size=1000)

        warehouse.add_material("сталь", 0)
        assert warehouse.materials["сталь"] == 0
        assert warehouse.loading == 0

    def test_remove_material(self):
        """Тест удаления материала со склада."""
        warehouse = Warehouse(size=1000)
        warehouse.materials = {"сталь": 500, "алюминий": 300}

        warehouse.remove_material("сталь", 200)
        assert warehouse.materials["сталь"] == 300
        assert warehouse.loading == 600  # 300 + 300

        warehouse.remove_material("алюминий", 100)
        assert warehouse.materials["алюминий"] == 200
        assert warehouse.loading == 500

    def test_remove_material_all(self):
        """Тест удаления всего материала."""
        warehouse = Warehouse(size=1000)
        warehouse.materials = {"сталь": 500}

        warehouse.remove_material("сталь", 500)
        assert warehouse.materials["сталь"] == 0
        assert warehouse.loading == 0

    def test_remove_material_not_found_raises_error(self):
        """Тест что удаление несуществующего материала вызывает ошибку."""
        warehouse = Warehouse(size=1000)
        warehouse.materials = {"сталь": 500}

        with pytest.raises(ValueError, match="Материал .* не найден на складе"):
            warehouse.remove_material("алюминий", 100)

        assert "алюминий" not in warehouse.materials
        assert warehouse.loading == 500

    def test_remove_material_insufficient_quantity_raises_error(self):
        """Тест что удаление большего количества, чем есть, вызывает ошибку."""
        warehouse = Warehouse(size=1000)
        warehouse.materials = {"сталь": 500}

        with pytest.raises(ValueError, match="На складе нет .* материала .*"):
            warehouse.remove_material("сталь", 600)

        # Количество не должно измениться
        assert warehouse.materials["сталь"] == 500
        assert warehouse.loading == 500

    def test_remove_material_zero_quantity(self):
        """Тест удаления нулевого количества материала."""
        warehouse = Warehouse(size=1000)
        warehouse.materials = {"сталь": 500}

        warehouse.remove_material("сталь", 0)
        assert warehouse.materials["сталь"] == 500
        assert warehouse.loading == 500

    def test_warehouse_to_redis_dict(self):
        """Тест сериализации Warehouse в словарь для Redis."""
        worker = Worker(worker_id="worker_001", name="Кладовщик")
        warehouse = Warehouse(
            warehouse_id="warehouse_001",
            inventory_worker=worker,
            size=1000,
            materials={"сталь": 500, "алюминий": 300},
        )

        result = warehouse.to_redis_dict()

        assert isinstance(result, dict)
        assert result["warehouse_id"] == "warehouse_001"
        assert result["size"] == 1000
        assert result["materials"] == {"сталь": 500, "алюминий": 300}
        assert result["_type"] == "Warehouse"
        # inventory_worker должен быть сериализован
        assert "inventory_worker" in result
        assert isinstance(result["inventory_worker"], dict)

    def test_warehouse_to_redis_dict_without_worker(self):
        """Тест сериализации склада без кладовщика."""
        warehouse = Warehouse(
            warehouse_id="warehouse_002",
            size=500,
            materials={"сталь": 200},
        )

        result = warehouse.to_redis_dict()

        assert result["warehouse_id"] == "warehouse_002"
        assert result["size"] == 500
        assert result["materials"] == {"сталь": 200}
        # inventory_worker должен быть None или отсутствовать
        assert result.get("inventory_worker") is None

    def test_warehouse_to_redis_json(self):
        """Тест сериализации Warehouse в JSON для Redis."""
        warehouse = Warehouse(
            warehouse_id="warehouse_003",
            size=1000,
            materials={"материал": 500},
        )

        result = warehouse.to_redis_json()

        assert isinstance(result, str)
        parsed = json.loads(result)

        assert parsed["warehouse_id"] == "warehouse_003"
        assert parsed["size"] == 1000
        assert parsed["materials"] == {"материал": 500}
        assert parsed["_type"] == "Warehouse"

    def test_warehouse_loading_updates_automatically(self):
        """Тест что loading обновляется автоматически при изменении materials."""
        warehouse = Warehouse(size=1000)

        assert warehouse.loading == 0

        # Добавляем напрямую в словарь
        warehouse.materials["материал1"] = 100
        assert warehouse.loading == 100

        warehouse.materials["материал2"] = 200
        assert warehouse.loading == 300

        # Изменяем значение
        warehouse.materials["материал1"] = 50
        assert warehouse.loading == 250

        # Удаляем ключ
        del warehouse.materials["материал1"]
        assert warehouse.loading == 200

    def test_warehouse_is_full_updates_automatically(self):
        """Тест что is_full обновляется автоматически при изменении materials."""
        warehouse = Warehouse(size=1000)

        assert warehouse.is_full is False

        warehouse.materials["материал"] = 1000
        assert warehouse.is_full is True

        warehouse.materials["материал"] = 500
        assert warehouse.is_full is False

    def test_warehouse_complex_scenario(self):
        """Тест комплексного сценария использования склада."""
        # Создаем склад
        warehouse = Warehouse(size=1000)

        # Устанавливаем кладовщика
        worker = Worker(worker_id="worker_001", name="Кладовщик")
        warehouse.set_inventory_worker(worker)

        # Добавляем материалы
        warehouse.add_material("сталь", 300)
        warehouse.add_material("алюминий", 200)
        assert warehouse.loading == 500
        assert warehouse.is_full is False

        # Увеличиваем размер склада
        warehouse.increase_size(500)
        assert warehouse.size == 1500
        assert warehouse.is_full is False

        # Добавляем еще материалы
        warehouse.add_material("медь", 400)
        assert warehouse.loading == 900
        assert warehouse.is_full is False

        # Удаляем часть материалов
        warehouse.remove_material("сталь", 100)
        assert warehouse.loading == 800
        assert warehouse.materials["сталь"] == 200

        # Уменьшаем размер склада
        warehouse.decrease_size(300)
        assert warehouse.size == 1200

        # Заполняем склад полностью
        warehouse.add_material("никель", 400)
        assert warehouse.loading == 1200
        assert warehouse.is_full is True

    def test_warehouse_materials_empty_dict(self):
        """Тест работы с пустым словарем материалов."""
        warehouse = Warehouse(size=1000, materials={})

        assert warehouse.loading == 0
        assert warehouse.is_full is False

        warehouse.add_material("материал", 100)
        assert warehouse.loading == 100

    def test_warehouse_multiple_materials(self):
        """Тест работы с несколькими материалами."""
        warehouse = Warehouse(size=5000)

        warehouse.add_material("сталь", 1000)
        warehouse.add_material("алюминий", 800)
        warehouse.add_material("медь", 600)
        warehouse.add_material("никель", 400)

        assert warehouse.loading == 2800
        assert warehouse.is_full is False
        assert len(warehouse.materials) == 4

        # Удаляем один материал полностью
        warehouse.remove_material("никель", 400)
        assert warehouse.loading == 2400
        assert warehouse.materials["никель"] == 0

    def test_warehouse_edge_case_zero_size_with_materials(self):
        """Тест граничного случая: размер склада 0, но есть материалы."""
        warehouse = Warehouse(size=0)
        warehouse.materials["материал"] = 100

        # Это может быть невалидное состояние, но свойство должно работать
        assert warehouse.loading == 100
        assert warehouse.is_full is True  # 100 >= 0

    def test_warehouse_add_material_checks_total_not_individual(self):
        """Тест что проверка места проверяет общую загрузку, а не отдельный материал."""
        warehouse = Warehouse(size=1000)
        warehouse.materials = {"сталь": 400, "алюминий": 400}

        # Общая загрузка 800, можем добавить еще 200
        warehouse.add_material("сталь", 200)
        assert warehouse.loading == 1000
        assert warehouse.is_full is True

        # Но не можем добавить больше
        with pytest.raises(ValueError, match="На складе нет места"):
            warehouse.add_material("алюминий", 1)

    def test_warehouse_unicode_material_names(self):
        """Тест работы с unicode символами в названиях материалов."""
        warehouse = Warehouse(size=1000)

        warehouse.add_material("Сталь 🎉", 100)
        warehouse.add_material("Алюминий с эмодзи 😊", 200)

        assert warehouse.materials["Сталь 🎉"] == 100
        assert warehouse.materials["Алюминий с эмодзи 😊"] == 200
        assert warehouse.loading == 300

        result = warehouse.to_redis_dict()
        assert "Сталь 🎉" in result["materials"]
        assert "Алюминий с эмодзи 😊" in result["materials"]

    def test_warehouse_size_negative_after_decrease(self):
        """Тест что размер не может быть отрицательным после уменьшения."""
        warehouse = Warehouse(size=100)

        warehouse.decrease_size(1000)
        assert warehouse.size == 0

        warehouse.decrease_size(100)
        assert warehouse.size == 0

    def test_warehouse_remove_material_exact_amount(self):
        """Тест удаления точного количества материала."""
        warehouse = Warehouse(size=1000)
        warehouse.materials = {"материал": 500}

        warehouse.remove_material("материал", 500)
        assert warehouse.materials["материал"] == 0
        assert warehouse.loading == 0
