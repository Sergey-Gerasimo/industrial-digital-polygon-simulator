"""Тесты для domain/certification.py"""

import pytest
import json

from domain.certification import Certification


class TestCertification:
    """Тесты для класса Certification."""

    def test_certification_creation_with_defaults(self):
        """Тест создания сертификации со значениями по умолчанию."""
        certification = Certification()

        assert certification.certificate_type == ""
        assert certification.is_obtained is False
        assert certification.implementation_cost == 0
        assert certification.implementation_time_days == 0

    def test_certification_creation_with_values(self):
        """Тест создания сертификации с заданными значениями."""
        certification = Certification(
            certificate_type="ISO 9001",
            is_obtained=True,
            implementation_cost=500000,
            implementation_time_days=90,
        )

        assert certification.certificate_type == "ISO 9001"
        assert certification.is_obtained is True
        assert certification.implementation_cost == 500000
        assert certification.implementation_time_days == 90

    def test_certification_partial_initialization(self):
        """Тест создания сертификации с частичной инициализацией."""
        certification = Certification(
            certificate_type="ISO 14001",
            is_obtained=True,
        )

        assert certification.certificate_type == "ISO 14001"
        assert certification.is_obtained is True
        # Остальные поля должны иметь значения по умолчанию
        assert certification.implementation_cost == 0
        assert certification.implementation_time_days == 0

    def test_set_is_obtained_true(self):
        """Тест установки статуса сертификации как полученной."""
        certification = Certification()

        certification.set_is_obtained(True)

        assert certification.is_obtained is True

    def test_set_is_obtained_false(self):
        """Тест установки статуса сертификации как не полученной."""
        certification = Certification(is_obtained=True)

        certification.set_is_obtained(False)

        assert certification.is_obtained is False

    def test_set_is_obtained_toggle(self):
        """Тест переключения статуса сертификации."""
        certification = Certification()

        certification.set_is_obtained(True)
        assert certification.is_obtained is True

        certification.set_is_obtained(False)
        assert certification.is_obtained is False

        certification.set_is_obtained(True)
        assert certification.is_obtained is True

    def test_set_is_obtained_updates_existing(self):
        """Тест обновления существующего статуса."""
        certification = Certification(is_obtained=False)

        certification.set_is_obtained(True)
        assert certification.is_obtained is True

        certification.set_is_obtained(False)
        assert certification.is_obtained is False

    def test_certification_mutable(self):
        """Тест что Certification не frozen (можно изменять поля напрямую)."""
        certification = Certification()

        certification.certificate_type = "Новый тип"
        certification.is_obtained = True
        certification.implementation_cost = 1000000
        certification.implementation_time_days = 120

        assert certification.certificate_type == "Новый тип"
        assert certification.is_obtained is True
        assert certification.implementation_cost == 1000000
        assert certification.implementation_time_days == 120

    def test_certification_to_redis_dict(self):
        """Тест сериализации Certification в словарь для Redis."""
        certification = Certification(
            certificate_type="ISO 9001",
            is_obtained=True,
            implementation_cost=750000,
            implementation_time_days=180,
        )

        result = certification.to_redis_dict()

        assert isinstance(result, dict)
        assert result["certificate_type"] == "ISO 9001"
        assert result["is_obtained"] is True
        assert result["implementation_cost"] == 750000
        assert result["implementation_time_days"] == 180
        assert result["_type"] == "Certification"

    def test_certification_to_redis_json(self):
        """Тест сериализации Certification в JSON для Redis."""
        certification = Certification(
            certificate_type="ISO 14001",
            is_obtained=False,
            implementation_cost=300000,
            implementation_time_days=60,
        )

        result = certification.to_redis_json()

        assert isinstance(result, str)
        parsed = json.loads(result)

        assert parsed["certificate_type"] == "ISO 14001"
        assert parsed["is_obtained"] is False
        assert parsed["implementation_cost"] == 300000
        assert parsed["implementation_time_days"] == 60
        assert parsed["_type"] == "Certification"

    def test_certification_to_redis_json_with_indent(self):
        """Тест форматированного JSON."""
        certification = Certification(certificate_type="Тестовая сертификация")

        result = certification.to_redis_json(indent=2)

        assert isinstance(result, str)
        assert "\n" in result  # Есть форматирование
        parsed = json.loads(result)
        assert parsed["certificate_type"] == "Тестовая сертификация"

    def test_certification_unicode_certificate_type(self):
        """Тест работы с unicode символами в типе сертификации."""
        certification = Certification(
            certificate_type="Сертификация с русскими символами 🎉",
            is_obtained=True,
        )

        result = certification.to_redis_dict()

        assert result["certificate_type"] == "Сертификация с русскими символами 🎉"

        json_result = certification.to_redis_json()
        parsed = json.loads(json_result)
        assert parsed["certificate_type"] == "Сертификация с русскими символами 🎉"

    def test_certification_string_fields_empty_and_whitespace(self):
        """Тест работы с пустыми строками и пробелами."""
        certification = Certification(
            certificate_type="  ",
        )

        result = certification.to_redis_dict()

        assert result["certificate_type"] == "  "

    def test_certification_implementation_cost_edge_cases(self):
        """Тест граничных значений стоимости внедрения."""
        certification_zero = Certification(implementation_cost=0)
        assert certification_zero.implementation_cost == 0

        certification_large = Certification(implementation_cost=999999999)
        assert certification_large.implementation_cost == 999999999

        certification_negative = Certification(implementation_cost=-1000)
        assert certification_negative.implementation_cost == -1000

    def test_certification_implementation_time_days_edge_cases(self):
        """Тест граничных значений времени внедрения."""
        certification_zero = Certification(implementation_time_days=0)
        assert certification_zero.implementation_time_days == 0

        certification_max = Certification(implementation_time_days=365 * 10)
        assert certification_max.implementation_time_days == 3650

        certification_negative = Certification(implementation_time_days=-10)
        assert certification_negative.implementation_time_days == -10

    def test_certification_is_obtained_default_false(self):
        """Тест что по умолчанию сертификация не получена."""
        certification = Certification()

        assert certification.is_obtained is False

        certification = Certification(certificate_type="ISO 9001")

        assert certification.is_obtained is False

    def test_certification_complex_scenario(self):
        """Тест комплексного сценария использования."""
        # Создаем сертификацию
        certification = Certification(
            certificate_type="ISO 9001:2015",
            is_obtained=False,
            implementation_cost=500000,
            implementation_time_days=90,
        )

        assert certification.is_obtained is False

        # Получаем сертификацию
        certification.set_is_obtained(True)
        assert certification.is_obtained is True

        # Обновляем стоимость и время
        certification.implementation_cost = 750000
        certification.implementation_time_days = 120

        assert certification.implementation_cost == 750000
        assert certification.implementation_time_days == 120

        # Сериализуем
        redis_dict = certification.to_redis_dict()
        assert redis_dict["is_obtained"] is True
        assert redis_dict["implementation_cost"] == 750000

        # Теряем сертификацию
        certification.set_is_obtained(False)
        assert certification.is_obtained is False

        # Финальная сериализация
        final_dict = certification.to_redis_dict()
        assert final_dict["is_obtained"] is False

    def test_certification_multiple_certificate_types(self):
        """Тест работы с разными типами сертификаций."""
        iso9001 = Certification(
            certificate_type="ISO 9001",
            is_obtained=True,
            implementation_cost=500000,
            implementation_time_days=90,
        )

        iso14001 = Certification(
            certificate_type="ISO 14001",
            is_obtained=False,
            implementation_cost=400000,
            implementation_time_days=75,
        )

        oshas18001 = Certification(
            certificate_type="OHSAS 18001",
            is_obtained=True,
            implementation_cost=600000,
            implementation_time_days=100,
        )

        assert iso9001.certificate_type == "ISO 9001"
        assert iso14001.certificate_type == "ISO 14001"
        assert oshas18001.certificate_type == "OHSAS 18001"

        assert iso9001.is_obtained is True
        assert iso14001.is_obtained is False
        assert oshas18001.is_obtained is True

    def test_certification_to_redis_dict_exclude_none(self):
        """Тест что None поля исключаются при сериализации."""
        certification = Certification(
            certificate_type="ISO 9001",
            is_obtained=True,
        )

        result = certification.to_redis_dict(exclude_none=True)

        # Все поля со значениями по умолчанию (не None) должны быть включены
        assert "certificate_type" in result
        assert "is_obtained" in result
        assert "implementation_cost" in result  # 0 не является None
        assert "implementation_time_days" in result  # 0 не является None
        assert "_type" in result

    def test_certification_comparison(self):
        """Тест сравнения сертификаций."""
        cert1 = Certification(
            certificate_type="ISO 9001",
            is_obtained=True,
            implementation_cost=500000,
        )
        cert2 = Certification(
            certificate_type="ISO 9001",
            is_obtained=True,
            implementation_cost=500000,
        )
        cert3 = Certification(
            certificate_type="ISO 14001",
            is_obtained=True,
            implementation_cost=500000,
        )

        # По умолчанию dataclass сравнивает все поля
        assert cert1 == cert2  # Все поля совпадают
        assert cert1 != cert3  # Разные типы сертификаций

    def test_certification_set_is_obtained_preserves_other_fields(self):
        """Тест что set_is_obtained не изменяет другие поля."""
        certification = Certification(
            certificate_type="ISO 9001",
            is_obtained=False,
            implementation_cost=500000,
            implementation_time_days=90,
        )

        certification.set_is_obtained(True)

        assert certification.is_obtained is True
        assert certification.certificate_type == "ISO 9001"
        assert certification.implementation_cost == 500000
        assert certification.implementation_time_days == 90

    def test_certification_empty_certificate_type(self):
        """Тест работы с пустым типом сертификации."""
        certification = Certification(certificate_type="")

        assert certification.certificate_type == ""
        assert certification.is_obtained is False

        result = certification.to_redis_dict()
        assert result["certificate_type"] == ""
