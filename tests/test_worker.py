"""Тесты для domain/worker.py"""

import pytest
import json

from domain.worker import Worker, Qualification, Specialization


class TestQualification:
    """Тесты для enum Qualification."""

    def test_qualification_values(self):
        """Тест значений квалификации."""
        assert Qualification.I == 1
        assert Qualification.II == 2
        assert Qualification.III == 3
        assert Qualification.IV == 4
        assert Qualification.V == 5
        assert Qualification.VI == 6
        assert Qualification.VII == 7
        assert Qualification.VIII == 8
        assert Qualification.IX == 9

    def test_qualification_int_conversion(self):
        """Тест преобразования квалификации в int."""
        assert int(Qualification.I) == 1
        assert int(Qualification.V) == 5
        assert int(Qualification.IX) == 9


class TestSpecialization:
    """Тесты для enum Specialization."""

    def test_specialization_values(self):
        """Тест значений специализации."""
        assert Specialization.NONE == "none"
        assert Specialization.ASSEMBLER == "Слесарь-сборщик"
        assert Specialization.ENGINEER_TECHNOLOGIST == "Инженер-технолог"
        assert Specialization.LOGIST == "Логист"
        assert Specialization.QUALITY_CONTROLLER == "Контролер качества"
        assert Specialization.WAREHOUSE_KEEPER == "Кладовщик"

    def test_specialization_str_conversion(self):
        """Тест получения строкового значения специализации."""
        assert Specialization.NONE.value == "none"
        assert Specialization.ASSEMBLER.value == "Слесарь-сборщик"
        assert Specialization.LOGIST.value == "Логист"


class TestWorker:
    """Тесты для класса Worker."""

    def test_worker_creation_with_defaults(self):
        """Тест создания работника со значениями по умолчанию."""
        worker = Worker()

        assert worker.worker_id == ""
        assert worker.name == ""
        assert worker.qualification == 0
        assert worker.specialty == ""
        assert worker.salary == 0

    def test_worker_creation_with_values(self):
        """Тест создания работника с заданными значениями."""
        worker = Worker(
            worker_id="worker_001",
            name="Иван Иванов",
            qualification=5,
            specialty="Слесарь-сборщик",
            salary=50000,
        )

        assert worker.worker_id == "worker_001"
        assert worker.name == "Иван Иванов"
        assert worker.qualification == 5
        assert worker.specialty == "Слесарь-сборщик"
        assert worker.salary == 50000

    def test_worker_partial_initialization(self):
        """Тест создания работника с частичной инициализацией."""
        worker = Worker(
            worker_id="worker_002",
            name="Петр Петров",
            qualification=3,
        )

        assert worker.worker_id == "worker_002"
        assert worker.name == "Петр Петров"
        assert worker.qualification == 3
        # Остальные поля должны иметь значения по умолчанию
        assert worker.specialty == ""
        assert worker.salary == 0

    def test_set_qualification_valid_range(self):
        """Тест установки квалификации в допустимом диапазоне."""
        worker = Worker()

        worker.set_qualification(1)
        assert worker.qualification == 1

        worker.set_qualification(5)
        assert worker.qualification == 5

        worker.set_qualification(9)
        assert worker.qualification == 9

    def test_set_qualification_enum_values(self):
        """Тест установки квалификации через enum значения."""
        worker = Worker()

        worker.set_qualification(Qualification.I)
        assert worker.qualification == 1

        worker.set_qualification(Qualification.V)
        assert worker.qualification == 5

        worker.set_qualification(Qualification.IX)
        assert worker.qualification == 9

    def test_set_qualification_below_minimum_raises_error(self):
        """Тест что установка квалификации меньше 1 вызывает ошибку."""
        worker = Worker()

        with pytest.raises(
            ValueError, match="Квалификация работника должна быть от 1 до 9"
        ):
            worker.set_qualification(0)

        with pytest.raises(
            ValueError, match="Квалификация работника должна быть от 1 до 9"
        ):
            worker.set_qualification(-1)

        # Значение не должно измениться
        assert worker.qualification == 0

    def test_set_qualification_above_maximum_raises_error(self):
        """Тест что установка квалификации больше 9 вызывает ошибку."""
        worker = Worker()

        with pytest.raises(
            ValueError, match="Квалификация работника должна быть от 1 до 9"
        ):
            worker.set_qualification(10)

        with pytest.raises(
            ValueError, match="Квалификация работника должна быть от 1 до 9"
        ):
            worker.set_qualification(100)

        # Значение не должно измениться
        assert worker.qualification == 0

    def test_set_qualification_boundary_values(self):
        """Тест граничных значений квалификации."""
        worker = Worker()

        # Минимальное значение
        worker.set_qualification(1)
        assert worker.qualification == 1

        # Максимальное значение
        worker.set_qualification(9)
        assert worker.qualification == 9

    def test_set_qualification_updates_existing(self):
        """Тест обновления существующей квалификации."""
        worker = Worker(qualification=3)

        worker.set_qualification(7)
        assert worker.qualification == 7

    def test_worker_mutable(self):
        """Тест что Worker не frozen (можно изменять поля напрямую)."""
        worker = Worker()

        worker.worker_id = "new_id"
        worker.name = "Новое имя"
        worker.qualification = 5
        worker.specialty = "Новая специализация"
        worker.salary = 60000

        assert worker.worker_id == "new_id"
        assert worker.name == "Новое имя"
        assert worker.qualification == 5
        assert worker.specialty == "Новая специализация"
        assert worker.salary == 60000

    def test_worker_to_redis_dict(self):
        """Тест сериализации Worker в словарь для Redis."""
        worker = Worker(
            worker_id="worker_003",
            name="Сергей Сергеев",
            qualification=6,
            specialty="Инженер-технолог",
            salary=75000,
        )

        result = worker.to_redis_dict()

        assert isinstance(result, dict)
        assert result["worker_id"] == "worker_003"
        assert result["name"] == "Сергей Сергеев"
        assert result["qualification"] == 6
        assert result["specialty"] == "Инженер-технолог"
        assert result["salary"] == 75000
        assert result["_type"] == "Worker"

    def test_worker_to_redis_json(self):
        """Тест сериализации Worker в JSON для Redis."""
        worker = Worker(
            worker_id="worker_004",
            name="Алексей Алексеев",
            qualification=4,
            salary=55000,
        )

        result = worker.to_redis_json()

        assert isinstance(result, str)
        parsed = json.loads(result)

        assert parsed["worker_id"] == "worker_004"
        assert parsed["name"] == "Алексей Алексеев"
        assert parsed["qualification"] == 4
        assert parsed["salary"] == 55000
        assert parsed["_type"] == "Worker"

    def test_worker_qualification_zero_allowed_at_creation(self):
        """Тест что квалификация может быть 0 при создании."""
        worker = Worker(qualification=0)

        assert worker.qualification == 0

        # Но нельзя установить через set_qualification
        with pytest.raises(ValueError):
            worker.set_qualification(0)

    def test_worker_specialization_string_values(self):
        """Тест работы со строковыми значениями специализации."""
        worker1 = Worker(specialty="Слесарь-сборщик")
        assert worker1.specialty == "Слесарь-сборщик"

        worker2 = Worker(specialty=Specialization.LOGIST)
        assert worker2.specialty == "Логист"

        worker3 = Worker(specialty="Кастомная специализация")
        assert worker3.specialty == "Кастомная специализация"

    def test_worker_salary_edge_cases(self):
        """Тест граничных значений зарплаты."""
        worker_zero = Worker(salary=0)
        assert worker_zero.salary == 0

        worker_large = Worker(salary=999999999)
        assert worker_large.salary == 999999999

        worker_negative = Worker(salary=-1000)
        assert worker_negative.salary == -1000  # Отрицательная зарплата не валидируется

    def test_worker_unicode_names(self):
        """Тест работы с unicode символами в именах."""
        worker = Worker(
            worker_id="worker_unicode",
            name="Работник с русскими символами 🎉",
            specialty="Специализация с эмодзи 😊",
        )

        result = worker.to_redis_dict()

        assert result["name"] == "Работник с русскими символами 🎉"
        assert result["specialty"] == "Специализация с эмодзи 😊"

        json_result = worker.to_redis_json()
        parsed = json.loads(json_result)
        assert parsed["name"] == "Работник с русскими символами 🎉"

    def test_worker_string_fields_empty_and_whitespace(self):
        """Тест работы с пустыми строками и пробелами."""
        worker = Worker(
            worker_id="  ",
            name="   ",
            specialty="",
        )

        result = worker.to_redis_dict()

        assert result["worker_id"] == "  "
        assert result["name"] == "   "
        assert result["specialty"] == ""

    def test_worker_complex_scenario(self):
        """Тест комплексного сценария использования."""
        # Создаем работника
        worker = Worker(
            worker_id="worker_complex_001",
            name="Комплексный работник",
            qualification=3,
            specialty="Слесарь-сборщик",
            salary=50000,
        )

        # Повышаем квалификацию
        worker.set_qualification(7)
        assert worker.qualification == 7

        # Меняем специализацию
        worker.specialty = "Инженер-технолог"
        assert worker.specialty == "Инженер-технолог"

        # Повышаем зарплату
        worker.salary = 80000
        assert worker.salary == 80000

        # Сериализуем
        redis_dict = worker.to_redis_dict()
        assert redis_dict["qualification"] == 7
        assert redis_dict["specialty"] == "Инженер-технолог"
        assert redis_dict["salary"] == 80000

        # Пытаемся установить невалидную квалификацию
        with pytest.raises(ValueError):
            worker.set_qualification(10)

        # Квалификация не должна измениться
        assert worker.qualification == 7

    def test_worker_all_qualifications(self):
        """Тест установки всех возможных квалификаций."""
        worker = Worker()

        for qual_value in range(1, 10):
            worker.set_qualification(qual_value)
            assert worker.qualification == qual_value

    def test_worker_all_specializations(self):
        """Тест использования всех специализаций из enum."""
        for spec in Specialization:
            worker = Worker(
                worker_id=f"worker_{spec.value}",
                specialty=spec.value,
            )
            assert worker.specialty == spec.value

    def test_worker_set_qualification_with_existing_qualification(self):
        """Тест установки квалификации когда уже есть значение."""
        worker = Worker(qualification=5)

        worker.set_qualification(2)
        assert worker.qualification == 2

        worker.set_qualification(8)
        assert worker.qualification == 8

    def test_worker_qualification_validation_does_not_modify_on_error(self):
        """Тест что при ошибке валидации квалификация не изменяется."""
        worker = Worker(qualification=5)

        # Пытаемся установить невалидное значение
        with pytest.raises(ValueError):
            worker.set_qualification(0)

        # Квалификация должна остаться прежней
        assert worker.qualification == 5

        with pytest.raises(ValueError):
            worker.set_qualification(10)

        assert worker.qualification == 5

    def test_worker_to_redis_dict_exclude_none(self):
        """Тест что None поля исключаются при сериализации."""
        worker = Worker(
            worker_id="worker_005",
            name="Тестовый работник",
            qualification=4,
        )

        result = worker.to_redis_dict(exclude_none=True)

        # Все поля со значениями по умолчанию (не None) должны быть включены
        assert "worker_id" in result
        assert "name" in result
        assert "qualification" in result
        assert "specialty" in result  # Пустая строка не None
        assert "salary" in result  # 0 не None
        assert "_type" in result

    def test_worker_comparison_by_worker_id(self):
        """Тест сравнения работников по worker_id."""
        worker1 = Worker(
            worker_id="worker_001",
            name="Иван",
            qualification=5,
        )
        worker2 = Worker(
            worker_id="worker_001",
            name="Петр",  # Разное имя
            qualification=3,  # Разная квалификация
        )
        worker3 = Worker(
            worker_id="worker_002",
            name="Иван",  # То же имя
            qualification=5,  # Та же квалификация
        )

        # Сравнение по worker_id
        assert worker1 == worker2  # worker_id совпадает
        assert worker1 != worker3  # Разные worker_id
        # Неравенство с другим типом
        assert worker1 != "not a worker"
        assert worker1 != None  # noqa: E711

    def test_worker_hash(self):
        """Тест хеширования работников по worker_id."""
        worker1 = Worker(worker_id="worker_001", name="Иван")
        worker2 = Worker(worker_id="worker_001", name="Петр")
        worker3 = Worker(worker_id="worker_002", name="Иван")

        # Работники с одинаковым worker_id имеют одинаковый хеш
        assert hash(worker1) == hash(worker2)
        # Работники с разным worker_id имеют разный хеш
        assert hash(worker1) != hash(worker3)

    def test_worker_in_set(self):
        """Тест использования работников в множестве (set)."""
        worker1 = Worker(worker_id="worker_001", name="Иван")
        worker2 = Worker(worker_id="worker_001", name="Петр")
        worker3 = Worker(worker_id="worker_002", name="Сергей")

        # В множестве должны быть только уникальные worker_id
        workers_set = {worker1, worker2, worker3}
        assert len(workers_set) == 2  # worker_001 и worker_002
        assert Worker(worker_id="worker_001") in workers_set
        assert Worker(worker_id="worker_002") in workers_set

    def test_worker_in_dict(self):
        """Тест использования работников как ключей в словаре."""
        worker1 = Worker(worker_id="worker_001", name="Иван")
        worker2 = Worker(worker_id="worker_001", name="Петр")

        workers_dict = {worker1: "value1"}
        # Работник с тем же worker_id должен находить тот же ключ
        assert workers_dict[worker2] == "value1"
        workers_dict[worker2] = "value2"
        # Должна перезаписаться значение для того же ключа
        assert workers_dict[worker1] == "value2"
        assert len(workers_dict) == 1
