"""Тесты для domain/workplace.py"""

import pytest
import json

from domain.workplace import Workplace
from domain.worker import Worker
from domain.equipment import Equipment


class TestWorkplace:
    """Тесты для класса Workplace."""

    def test_workplace_creation_with_defaults(self):
        """Тест создания рабочего места со значениями по умолчанию."""
        workplace = Workplace()

        assert workplace.workplace_id == ""
        assert workplace.workplace_name == ""
        assert workplace.required_speciality == ""
        assert workplace.required_qualification == 0
        assert workplace.required_equipment == ""
        assert workplace.worker is None
        assert workplace.equipment is None
        assert workplace.required_stages == []
        assert workplace.is_start_node is False
        assert workplace.is_end_node is False
        assert workplace.next_workplace_ids == []

    def test_workplace_creation_with_values(self):
        """Тест создания рабочего места с заданными значениями."""
        worker = Worker(worker_id="worker_001", name="Иван")
        equipment = Equipment(equipment_id="equip_001", name="Станок")
        workplace = Workplace(
            workplace_id="wp_001",
            workplace_name="Сборочное место",
            required_speciality="Слесарь-сборщик",
            required_qualification=5,
            required_equipment="equip_001",
            worker=worker,
            equipment=equipment,
            required_stages=["сборка", "проверка"],
            is_start_node=True,
            is_end_node=False,
            next_workplace_ids=["wp_002", "wp_003"],
        )

        assert workplace.workplace_id == "wp_001"
        assert workplace.workplace_name == "Сборочное место"
        assert workplace.required_speciality == "Слесарь-сборщик"
        assert workplace.required_qualification == 5
        assert workplace.required_equipment == "equip_001"
        assert workplace.worker == worker
        assert workplace.equipment == equipment
        assert workplace.required_stages == ["сборка", "проверка"]
        assert workplace.is_start_node is True
        assert workplace.is_end_node is False
        assert workplace.next_workplace_ids == ["wp_002", "wp_003"]

    def test_workplace_partial_initialization(self):
        """Тест создания рабочего места с частичной инициализацией."""
        workplace = Workplace(
            workplace_id="wp_002",
            workplace_name="Рабочее место 2",
            required_qualification=3,
        )

        assert workplace.workplace_id == "wp_002"
        assert workplace.workplace_name == "Рабочее место 2"
        assert workplace.required_qualification == 3
        # Остальные поля должны иметь значения по умолчанию
        assert workplace.required_speciality == ""
        assert workplace.worker is None
        assert workplace.equipment is None

    def test_workplace_equality_by_workplace_id(self):
        """Тест сравнения рабочих мест по workplace_id."""
        workplace1 = Workplace(
            workplace_id="wp_001",
            workplace_name="Место 1",
            required_qualification=5,
        )
        workplace2 = Workplace(
            workplace_id="wp_001",
            workplace_name="Место 2",
            required_qualification=3,
        )
        workplace3 = Workplace(
            workplace_id="wp_002",
            workplace_name="Место 1",
            required_qualification=5,
        )

        # Рабочие места с одинаковым workplace_id считаются равными
        assert workplace1 == workplace2
        # Рабочие места с разным workplace_id не равны
        assert workplace1 != workplace3
        # Неравенство с другим типом
        assert workplace1 != "not a workplace"
        assert workplace1 != None  # noqa: E711

    def test_workplace_hash(self):
        """Тест хеширования рабочих мест по workplace_id."""
        workplace1 = Workplace(workplace_id="wp_001", workplace_name="А")
        workplace2 = Workplace(workplace_id="wp_001", workplace_name="Б")
        workplace3 = Workplace(workplace_id="wp_002", workplace_name="А")

        # Рабочие места с одинаковым workplace_id имеют одинаковый хеш
        assert hash(workplace1) == hash(workplace2)
        # Рабочие места с разным workplace_id имеют разный хеш
        assert hash(workplace1) != hash(workplace3)

    def test_workplace_in_set(self):
        """Тест использования рабочих мест в множестве (set)."""
        workplace1 = Workplace(workplace_id="wp_001", workplace_name="А")
        workplace2 = Workplace(workplace_id="wp_001", workplace_name="Б")
        workplace3 = Workplace(workplace_id="wp_002", workplace_name="В")

        # В множестве должны быть только уникальные workplace_id
        workplaces_set = {workplace1, workplace2, workplace3}
        assert len(workplaces_set) == 2  # wp_001 и wp_002
        assert Workplace(workplace_id="wp_001") in workplaces_set
        assert Workplace(workplace_id="wp_002") in workplaces_set

    def test_workplace_in_dict(self):
        """Тест использования рабочих мест как ключей в словаре."""
        workplace1 = Workplace(workplace_id="wp_001", workplace_name="А")
        workplace2 = Workplace(workplace_id="wp_001", workplace_name="Б")

        workplaces_dict = {workplace1: "value1"}
        # Рабочее место с тем же workplace_id должно находить тот же ключ
        assert workplaces_dict[workplace2] == "value1"
        workplaces_dict[workplace2] = "value2"
        # Должна перезаписаться значение для того же ключа
        assert workplaces_dict[workplace1] == "value2"
        assert len(workplaces_dict) == 1

    def test_set_worker(self):
        """Тест установки работника на рабочее место."""
        workplace = Workplace()
        worker = Worker(worker_id="worker_001", name="Иван Иванов")

        workplace.set_worker(worker)

        assert workplace.worker == worker
        assert workplace.worker.worker_id == "worker_001"
        assert workplace.worker.name == "Иван Иванов"

    def test_set_worker_replace(self):
        """Тест замены работника на рабочем месте."""
        workplace = Workplace()
        worker1 = Worker(worker_id="worker_001", name="Иван")
        worker2 = Worker(worker_id="worker_002", name="Петр")

        workplace.set_worker(worker1)
        assert workplace.worker == worker1

        workplace.set_worker(worker2)
        assert workplace.worker == worker2
        assert workplace.worker.name == "Петр"

    def test_set_worker_invalid_type_raises_error(self):
        """Тест что установка не-Worker объекта вызывает ошибку."""
        workplace = Workplace()

        with pytest.raises(
            ValueError, match="Рабочий должен быть объектом класса Worker"
        ):
            workplace.set_worker("not a worker")

        with pytest.raises(
            ValueError, match="Рабочий должен быть объектом класса Worker"
        ):
            workplace.set_worker(None)

        assert workplace.worker is None

    def test_set_equipmnet(self):
        """Тест установки оборудования на рабочее место."""
        workplace = Workplace()
        equipment = Equipment(equipment_id="equip_001", name="Токарный станок")

        workplace.set_equipmnet(equipment)

        assert workplace.equipment == equipment
        assert workplace.equipment.equipment_id == "equip_001"
        assert workplace.equipment.name == "Токарный станок"

    def test_set_equipmnet_replace(self):
        """Тест замены оборудования на рабочем месте."""
        workplace = Workplace()
        equipment1 = Equipment(equipment_id="equip_001", name="Станок 1")
        equipment2 = Equipment(equipment_id="equip_002", name="Станок 2")

        workplace.set_equipmnet(equipment1)
        assert workplace.equipment == equipment1

        workplace.set_equipmnet(equipment2)
        assert workplace.equipment == equipment2
        assert workplace.equipment.name == "Станок 2"

    def test_set_equipmnet_invalid_type_raises_error(self):
        """Тест что установка не-Equipment объекта вызывает ошибку."""
        workplace = Workplace()

        with pytest.raises(
            ValueError, match="Оборудование должно быть объектом класса Equipment"
        ):
            workplace.set_equipmnet("not equipment")

        with pytest.raises(
            ValueError, match="Оборудование должно быть объектом класса Equipment"
        ):
            workplace.set_equipmnet(None)

        assert workplace.equipment is None

    def test_workplace_to_redis_dict(self):
        """Тест сериализации Workplace в словарь для Redis."""
        worker = Worker(worker_id="worker_001", name="Иван")
        equipment = Equipment(equipment_id="equip_001", name="Станок")
        workplace = Workplace(
            workplace_id="wp_001",
            workplace_name="Сборочное место",
            required_speciality="Слесарь-сборщик",
            required_qualification=5,
            required_equipment="equip_001",
            worker=worker,
            equipment=equipment,
            required_stages=["сборка", "проверка"],
            is_start_node=True,
            is_end_node=False,
            next_workplace_ids=["wp_002"],
        )

        result = workplace.to_redis_dict()

        assert isinstance(result, dict)
        assert result["workplace_id"] == "wp_001"
        assert result["workplace_name"] == "Сборочное место"
        assert result["required_speciality"] == "Слесарь-сборщик"
        assert result["required_qualification"] == 5
        assert result["required_equipment"] == "equip_001"
        assert result["required_stages"] == ["сборка", "проверка"]
        assert result["is_start_node"] is True
        assert result["is_end_node"] is False
        assert result["next_workplace_ids"] == ["wp_002"]
        assert result["_type"] == "Workplace"
        # worker и equipment должны быть сериализованы
        assert "worker" in result
        assert isinstance(result["worker"], dict)
        assert "equipment" in result
        assert isinstance(result["equipment"], dict)

    def test_workplace_to_redis_dict_without_worker_and_equipment(self):
        """Тест сериализации рабочего места без работника и оборудования."""
        workplace = Workplace(
            workplace_id="wp_002",
            workplace_name="Рабочее место",
            required_qualification=3,
        )

        result = workplace.to_redis_dict()

        assert result["workplace_id"] == "wp_002"
        assert result["workplace_name"] == "Рабочее место"
        assert result["required_qualification"] == 3
        # worker и equipment должны быть None или отсутствовать
        assert result.get("worker") is None
        assert result.get("equipment") is None

    def test_workplace_to_redis_json(self):
        """Тест сериализации Workplace в JSON для Redis."""
        workplace = Workplace(
            workplace_id="wp_003",
            workplace_name="Тестовое место",
            required_qualification=4,
            is_start_node=True,
        )

        result = workplace.to_redis_json()

        assert isinstance(result, str)
        parsed = json.loads(result)

        assert parsed["workplace_id"] == "wp_003"
        assert parsed["workplace_name"] == "Тестовое место"
        assert parsed["required_qualification"] == 4
        assert parsed["is_start_node"] is True
        assert parsed["_type"] == "Workplace"

    def test_workplace_required_stages_list(self):
        """Тест работы со списком требуемых этапов."""
        workplace = Workplace()

        assert workplace.required_stages == []

        workplace.required_stages = ["этап1", "этап2"]
        assert workplace.required_stages == ["этап1", "этап2"]

        workplace.required_stages.append("этап3")
        assert len(workplace.required_stages) == 3

    def test_workplace_next_workplace_ids_list(self):
        """Тест работы со списком следующих рабочих мест."""
        workplace = Workplace()

        assert workplace.next_workplace_ids == []

        workplace.next_workplace_ids = ["wp_002", "wp_003"]
        assert workplace.next_workplace_ids == ["wp_002", "wp_003"]

        workplace.next_workplace_ids.append("wp_004")
        assert len(workplace.next_workplace_ids) == 3

    def test_workplace_start_and_end_nodes(self):
        """Тест флагов начального и конечного узла."""
        workplace = Workplace()

        assert workplace.is_start_node is False
        assert workplace.is_end_node is False

        workplace.is_start_node = True
        assert workplace.is_start_node is True
        assert workplace.is_end_node is False

        workplace.is_end_node = True
        assert workplace.is_start_node is True
        assert workplace.is_end_node is True

        # Может быть одновременно и начальным, и конечным
        workplace_start_end = Workplace(is_start_node=True, is_end_node=True)
        assert workplace_start_end.is_start_node is True
        assert workplace_start_end.is_end_node is True

    def test_workplace_mutable(self):
        """Тест что Workplace не frozen (можно изменять поля напрямую)."""
        workplace = Workplace()

        workplace.workplace_id = "new_id"
        workplace.workplace_name = "Новое название"
        workplace.required_qualification = 7
        workplace.is_start_node = True

        assert workplace.workplace_id == "new_id"
        assert workplace.workplace_name == "Новое название"
        assert workplace.required_qualification == 7
        assert workplace.is_start_node is True

    def test_workplace_unicode_fields(self):
        """Тест работы с unicode символами в полях."""
        workplace = Workplace(
            workplace_id="wp_unicode",
            workplace_name="Рабочее место с русскими символами 🎉",
            required_speciality="Специализация с эмодзи 😊",
        )

        result = workplace.to_redis_dict()

        assert result["workplace_name"] == "Рабочее место с русскими символами 🎉"
        assert result["required_speciality"] == "Специализация с эмодзи 😊"

        json_result = workplace.to_redis_json()
        parsed = json.loads(json_result)
        assert parsed["workplace_name"] == "Рабочее место с русскими символами 🎉"

    def test_workplace_complex_scenario(self):
        """Тест комплексного сценария использования."""
        # Создаем рабочее место
        workplace = Workplace(
            workplace_id="wp_complex_001",
            workplace_name="Комплексное рабочее место",
            required_speciality="Слесарь-сборщик",
            required_qualification=5,
            required_equipment="equip_001",
            is_start_node=True,
            required_stages=["сборка"],
            next_workplace_ids=["wp_002"],
        )

        # Устанавливаем работника
        worker = Worker(worker_id="worker_001", name="Иван")
        workplace.set_worker(worker)
        assert workplace.worker == worker

        # Устанавливаем оборудование
        equipment = Equipment(equipment_id="equip_001", name="Станок")
        workplace.set_equipmnet(equipment)
        assert workplace.equipment == equipment

        # Добавляем этапы
        workplace.required_stages.append("проверка")
        assert len(workplace.required_stages) == 2

        # Добавляем следующие рабочие места
        workplace.next_workplace_ids.append("wp_003")
        assert len(workplace.next_workplace_ids) == 2

        # Сериализуем
        redis_dict = workplace.to_redis_dict()
        assert redis_dict["workplace_id"] == "wp_complex_001"
        assert redis_dict["is_start_node"] is True

        # Меняем флаги
        workplace.is_start_node = False
        workplace.is_end_node = True
        assert workplace.is_start_node is False
        assert workplace.is_end_node is True

    def test_workplace_empty_lists(self):
        """Тест работы с пустыми списками."""
        workplace = Workplace()

        assert workplace.required_stages == []
        assert workplace.next_workplace_ids == []

        # Можно добавить элементы
        workplace.required_stages.append("этап")
        assert workplace.required_stages == ["этап"]

    def test_workplace_multiple_next_workplaces(self):
        """Тест работы с несколькими следующими рабочими местами."""
        workplace = Workplace()

        workplace.next_workplace_ids = ["wp_001", "wp_002", "wp_003"]
        assert len(workplace.next_workplace_ids) == 3
        assert "wp_001" in workplace.next_workplace_ids

    def test_workplace_qualification_edge_cases(self):
        """Тест граничных значений квалификации."""
        workplace_min = Workplace(required_qualification=0)
        assert workplace_min.required_qualification == 0

        workplace_max = Workplace(required_qualification=9)
        assert workplace_max.required_qualification == 9

        workplace_large = Workplace(required_qualification=100)
        assert workplace_large.required_qualification == 100

    def test_workplace_coordinates_default_none(self):
        """Тест что координаты по умолчанию None."""
        workplace = Workplace()

        assert workplace.x is None
        assert workplace.y is None

    def test_workplace_coordinates_set_values(self):
        """Тест установки координат на площадке 7x7."""
        workplace = Workplace(
            workplace_id="wp_coords_001",
            workplace_name="Рабочее место с координатами",
            x=3,
            y=4,
        )

        assert workplace.x == 3
        assert workplace.y == 4

    def test_workplace_coordinates_all_positions(self):
        """Тест установки координат для всех позиций сетки 7x7."""
        # Тестируем углы сетки
        workplace_top_left = Workplace(x=0, y=0)
        assert workplace_top_left.x == 0
        assert workplace_top_left.y == 0

        workplace_top_right = Workplace(x=6, y=0)
        assert workplace_top_right.x == 6
        assert workplace_top_right.y == 0

        workplace_bottom_left = Workplace(x=0, y=6)
        assert workplace_bottom_left.x == 0
        assert workplace_bottom_left.y == 6

        workplace_bottom_right = Workplace(x=6, y=6)
        assert workplace_bottom_right.x == 6
        assert workplace_bottom_right.y == 6

        # Тестируем центр
        workplace_center = Workplace(x=3, y=3)
        assert workplace_center.x == 3
        assert workplace_center.y == 3

    def test_workplace_coordinates_update(self):
        """Тест изменения координат после создания."""
        workplace = Workplace()

        assert workplace.x is None
        assert workplace.y is None

        # Устанавливаем координаты
        workplace.x = 2
        workplace.y = 5

        assert workplace.x == 2
        assert workplace.y == 5

        # Меняем координаты
        workplace.x = 1
        workplace.y = 1

        assert workplace.x == 1
        assert workplace.y == 1

        # Устанавливаем в None
        workplace.x = None
        workplace.y = None

        assert workplace.x is None
        assert workplace.y is None

    def test_workplace_coordinates_in_redis_dict(self):
        """Тест что координаты сохраняются в словарь для Redis."""
        workplace_with_coords = Workplace(
            workplace_id="wp_redis_coords",
            workplace_name="Рабочее место",
            x=2,
            y=3,
        )

        result = workplace_with_coords.to_redis_dict()

        assert result["x"] == 2
        assert result["y"] == 3

        # Тест с None координатами
        workplace_without_coords = Workplace(
            workplace_id="wp_redis_no_coords",
            workplace_name="Рабочее место без координат",
        )

        result_none = workplace_without_coords.to_redis_dict()
        assert result_none.get("x") is None
        assert result_none.get("y") is None

    def test_workplace_coordinates_combined_with_other_fields(self):
        """Тест координат в комбинации с другими полями."""
        workplace = Workplace(
            workplace_id="wp_combined",
            workplace_name="Комплексное рабочее место",
            required_speciality="Слесарь-сборщик",
            required_qualification=5,
            is_start_node=True,
            x=4,
            y=2,
        )

        assert workplace.workplace_id == "wp_combined"
        assert workplace.workplace_name == "Комплексное рабочее место"
        assert workplace.required_qualification == 5
        assert workplace.is_start_node is True
        assert workplace.x == 4
        assert workplace.y == 2
