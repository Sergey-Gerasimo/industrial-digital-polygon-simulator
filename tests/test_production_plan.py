"""Тесты для domain/production_plan.py"""

import pytest
import json

from domain.production_plan import ProductionPlanRow, ProductionSchedule


class TestProductionPlanRow:
    """Тесты для класса ProductionPlanRow."""

    def test_production_plan_row_creation_with_defaults(self):
        """Тест создания строки производственного плана со значениями по умолчанию."""
        row = ProductionPlanRow()

        assert row.tender_id == ""
        assert row.product_name == ""
        assert row.priority == 0
        assert row.plan_date == ""
        assert row.dse == ""
        assert row.short_set == ""
        assert row.dse_name == ""
        assert row.planned_quantity == 0
        assert row.actual_quantity == 0
        assert row.remaining_to_produce == 0
        assert row.provision_status == ""
        assert row.note == ""
        assert row.planned_completion_date == ""
        assert row.cost_breakdown == ""
        assert row.order_number == ""

    def test_production_plan_row_creation_with_values(self):
        """Тест создания строки производственного плана с заданными значениями."""
        row = ProductionPlanRow(
            tender_id="tender_001",
            product_name="Изделие А",
            priority=1,
            plan_date="15.02",
            dse="5BM.003.272",
            short_set="5BM.003.272",
            dse_name="Корпус",
            planned_quantity=300,
            actual_quantity=200,
            remaining_to_produce=100,
            provision_status="Обеспечено",
            note="Примечание",
            planned_completion_date="22.12.2010",
            cost_breakdown="20138",
            order_number="107-33/.",
        )

        assert row.tender_id == "tender_001"
        assert row.product_name == "Изделие А"
        assert row.priority == 1
        assert row.plan_date == "15.02"
        assert row.dse == "5BM.003.272"
        assert row.short_set == "5BM.003.272"
        assert row.dse_name == "Корпус"
        assert row.planned_quantity == 300
        assert row.actual_quantity == 200
        assert row.remaining_to_produce == 100
        assert row.provision_status == "Обеспечено"
        assert row.note == "Примечание"
        assert row.planned_completion_date == "22.12.2010"
        assert row.cost_breakdown == "20138"
        assert row.order_number == "107-33/."

    def test_production_plan_row_equality_by_tender_id(self):
        """Тест сравнения строк по tender_id."""
        row1 = ProductionPlanRow(
            tender_id="tender_001",
            product_name="Изделие А",
            priority=1,
        )
        row2 = ProductionPlanRow(
            tender_id="tender_001",
            product_name="Изделие Б",
            priority=2,
        )
        row3 = ProductionPlanRow(
            tender_id="tender_002",
            product_name="Изделие А",
            priority=1,
        )

        # Строки с одинаковым tender_id считаются равными
        assert row1 == row2
        # Строки с разным tender_id не равны
        assert row1 != row3
        # Неравенство с другим типом
        assert row1 != "not a row"
        assert row1 != None  # noqa: E711

    def test_production_plan_row_hash(self):
        """Тест хеширования строк по tender_id."""
        row1 = ProductionPlanRow(tender_id="tender_001", product_name="А")
        row2 = ProductionPlanRow(tender_id="tender_001", product_name="Б")
        row3 = ProductionPlanRow(tender_id="tender_002", product_name="А")

        # Строки с одинаковым tender_id имеют одинаковый хеш
        assert hash(row1) == hash(row2)
        # Строки с разным tender_id имеют разный хеш
        assert hash(row1) != hash(row3)

    def test_production_plan_row_in_set(self):
        """Тест использования строк в множестве (set)."""
        row1 = ProductionPlanRow(tender_id="tender_001", product_name="А")
        row2 = ProductionPlanRow(tender_id="tender_001", product_name="Б")
        row3 = ProductionPlanRow(tender_id="tender_002", product_name="В")

        # В множестве должны быть только уникальные tender_id
        rows_set = {row1, row2, row3}
        assert len(rows_set) == 2  # tender_001 и tender_002
        assert ProductionPlanRow(tender_id="tender_001") in rows_set
        assert ProductionPlanRow(tender_id="tender_002") in rows_set

    def test_production_plan_row_in_dict(self):
        """Тест использования строк как ключей в словаре."""
        row1 = ProductionPlanRow(tender_id="tender_001", product_name="А")
        row2 = ProductionPlanRow(tender_id="tender_001", product_name="Б")

        rows_dict = {row1: "value1"}
        # Строка с тем же tender_id должна находить тот же ключ
        assert rows_dict[row2] == "value1"
        rows_dict[row2] = "value2"
        # Должна перезаписаться значение для того же ключа
        assert rows_dict[row1] == "value2"
        assert len(rows_dict) == 1

    def test_production_plan_row_to_redis_dict(self):
        """Тест сериализации ProductionPlanRow в словарь для Redis."""
        row = ProductionPlanRow(
            tender_id="tender_001",
            product_name="Изделие А",
            priority=5,
            plan_date="03.02",
            dse="3BM.849.011",
            planned_quantity=3,
            actual_quantity=0,
            remaining_to_produce=3,
            provision_status="Обеспечено",
            planned_completion_date="14.03.2011",
            order_number="31-33/33",
        )

        result = row.to_redis_dict()

        assert isinstance(result, dict)
        assert result["tender_id"] == "tender_001"
        assert result["product_name"] == "Изделие А"
        assert result["priority"] == 5
        assert result["plan_date"] == "03.02"
        assert result["dse"] == "3BM.849.011"
        assert result["planned_quantity"] == 3
        assert result["actual_quantity"] == 0
        assert result["remaining_to_produce"] == 3
        assert result["provision_status"] == "Обеспечено"
        assert result["planned_completion_date"] == "14.03.2011"
        assert result["order_number"] == "31-33/33"
        assert result["_type"] == "ProductionPlanRow"

    def test_production_plan_row_to_redis_json(self):
        """Тест сериализации ProductionPlanRow в JSON для Redis."""
        row = ProductionPlanRow(
            tender_id="tender_002",
            product_name="Изделие Б",
            priority=10,
            planned_quantity=240,
            actual_quantity=100,
            remaining_to_produce=140,
        )

        result = row.to_redis_json()

        assert isinstance(result, str)
        parsed = json.loads(result)

        assert parsed["tender_id"] == "tender_002"
        assert parsed["product_name"] == "Изделие Б"
        assert parsed["priority"] == 10
        assert parsed["planned_quantity"] == 240
        assert parsed["actual_quantity"] == 100
        assert parsed["remaining_to_produce"] == 140
        assert parsed["_type"] == "ProductionPlanRow"

    def test_production_plan_row_unicode_fields(self):
        """Тест работы с unicode символами в полях."""
        row = ProductionPlanRow(
            tender_id="tender_unicode",
            product_name="Изделие с русскими символами 🎉",
            dse_name="Корпус устройства",
            note="Примечание с эмодзи 😊",
        )

        result = row.to_redis_dict()

        assert result["product_name"] == "Изделие с русскими символами 🎉"
        assert result["dse_name"] == "Корпус устройства"
        assert result["note"] == "Примечание с эмодзи 😊"

        json_result = row.to_redis_json()
        parsed = json.loads(json_result)
        assert parsed["product_name"] == "Изделие с русскими символами 🎉"

    def test_production_plan_row_provision_status_values(self):
        """Тест различных значений статуса обеспеченности."""
        row_provided = ProductionPlanRow(
            tender_id="tender_001", provision_status="Обеспечено"
        )
        row_not_provided = ProductionPlanRow(
            tender_id="tender_002", provision_status="Не обеспечено"
        )

        assert row_provided.provision_status == "Обеспечено"
        assert row_not_provided.provision_status == "Не обеспечено"

    def test_production_plan_row_date_formats(self):
        """Тест различных форматов дат."""
        row = ProductionPlanRow(
            tender_id="tender_date",
            plan_date="03.02",  # DD.MM
            planned_completion_date="14.03.2011",  # DD.MM.YYYY
        )

        assert row.plan_date == "03.02"
        assert row.planned_completion_date == "14.03.2011"


class TestProductionSchedule:
    """Тесты для класса ProductionSchedule."""

    def test_production_schedule_creation_empty(self):
        """Тест создания пустого производственного плана."""
        schedule = ProductionSchedule()

        assert isinstance(schedule.rows, list)
        assert len(schedule.rows) == 0

    def test_production_schedule_set_row_new(self):
        """Тест добавления новой строки в план."""
        schedule = ProductionSchedule()
        row = ProductionPlanRow(
            tender_id="tender_001",
            product_name="Изделие А",
            priority=1,
        )

        schedule.set_row(row)

        assert len(schedule.rows) == 1
        assert schedule.rows[0].tender_id == "tender_001"
        assert schedule.rows[0].product_name == "Изделие А"
        assert schedule.rows[0].priority == 1

    def test_production_schedule_set_row_replace_existing(self):
        """Тест перезаписи существующей строки с тем же tender_id."""
        schedule = ProductionSchedule()
        row1 = ProductionPlanRow(
            tender_id="tender_001",
            product_name="Изделие А",
            priority=1,
            planned_quantity=100,
        )
        row2 = ProductionPlanRow(
            tender_id="tender_001",
            product_name="Изделие Б",
            priority=2,
            planned_quantity=200,
        )

        schedule.set_row(row1)
        assert len(schedule.rows) == 1
        assert schedule.rows[0].product_name == "Изделие А"
        assert schedule.rows[0].planned_quantity == 100

        schedule.set_row(row2)
        # Должна перезаписаться существующая строка, а не добавиться новая
        assert len(schedule.rows) == 1
        assert schedule.rows[0].tender_id == "tender_001"
        assert schedule.rows[0].product_name == "Изделие Б"
        assert schedule.rows[0].priority == 2
        assert schedule.rows[0].planned_quantity == 200

    def test_production_schedule_set_row_multiple_unique_tenders(self):
        """Тест добавления нескольких строк с разными tender_id."""
        schedule = ProductionSchedule()

        row1 = ProductionPlanRow(tender_id="tender_001", product_name="А", priority=1)
        row2 = ProductionPlanRow(tender_id="tender_002", product_name="Б", priority=2)
        row3 = ProductionPlanRow(tender_id="tender_003", product_name="В", priority=3)

        schedule.set_row(row1)
        schedule.set_row(row2)
        schedule.set_row(row3)

        assert len(schedule.rows) == 3
        assert schedule.rows[0].tender_id == "tender_001"
        assert schedule.rows[1].tender_id == "tender_002"
        assert schedule.rows[2].tender_id == "tender_003"

    def test_production_schedule_set_row_one_row_per_tender(self):
        """Тест что для каждого тендера может быть только одна строка."""
        schedule = ProductionSchedule()

        # Добавляем строку для tender_001
        row1 = ProductionPlanRow(
            tender_id="tender_001",
            product_name="Изделие А",
            priority=1,
        )
        schedule.set_row(row1)

        # Пытаемся добавить еще одну строку для того же тендера
        row2 = ProductionPlanRow(
            tender_id="tender_001",
            product_name="Изделие А Обновленное",
            priority=5,
        )
        schedule.set_row(row2)

        # Должна быть только одна строка, но с обновленными данными
        assert len(schedule.rows) == 1
        assert schedule.rows[0].tender_id == "tender_001"
        assert schedule.rows[0].product_name == "Изделие А Обновленное"
        assert schedule.rows[0].priority == 5

    def test_production_schedule_set_row_update_middle_row(self):
        """Тест обновления строки в середине списка."""
        schedule = ProductionSchedule()

        # Добавляем несколько строк
        schedule.set_row(ProductionPlanRow(tender_id="tender_001", priority=1))
        schedule.set_row(ProductionPlanRow(tender_id="tender_002", priority=2))
        schedule.set_row(ProductionPlanRow(tender_id="tender_003", priority=3))

        assert len(schedule.rows) == 3

        # Обновляем среднюю строку
        updated_row = ProductionPlanRow(
            tender_id="tender_002",
            priority=10,
            product_name="Обновленное изделие",
        )
        schedule.set_row(updated_row)

        assert len(schedule.rows) == 3
        assert schedule.rows[1].tender_id == "tender_002"
        assert schedule.rows[1].priority == 10
        assert schedule.rows[1].product_name == "Обновленное изделие"

    def test_production_schedule_to_redis_dict(self):
        """Тест сериализации ProductionSchedule в словарь для Redis."""
        schedule = ProductionSchedule()
        schedule.set_row(
            ProductionPlanRow(tender_id="tender_001", product_name="А", priority=1)
        )
        schedule.set_row(
            ProductionPlanRow(tender_id="tender_002", product_name="Б", priority=2)
        )

        result = schedule.to_redis_dict()

        assert isinstance(result, dict)
        assert "_type" in result
        assert result["_type"] == "ProductionSchedule"
        assert "rows" in result
        assert isinstance(result["rows"], list)
        assert len(result["rows"]) == 2

        # Проверяем первую строку
        first_row = result["rows"][0]
        assert first_row["tender_id"] == "tender_001"
        assert first_row["product_name"] == "А"
        assert first_row["priority"] == 1

    def test_production_schedule_to_redis_json(self):
        """Тест сериализации ProductionSchedule в JSON для Redis."""
        schedule = ProductionSchedule()
        schedule.set_row(
            ProductionPlanRow(
                tender_id="tender_001",
                product_name="Изделие",
                priority=5,
                planned_quantity=100,
            )
        )

        result = schedule.to_redis_json()

        assert isinstance(result, str)
        parsed = json.loads(result)

        assert parsed["_type"] == "ProductionSchedule"
        assert len(parsed["rows"]) == 1
        assert parsed["rows"][0]["tender_id"] == "tender_001"
        assert parsed["rows"][0]["product_name"] == "Изделие"
        assert parsed["rows"][0]["priority"] == 5
        assert parsed["rows"][0]["planned_quantity"] == 100

    def test_production_schedule_empty_to_redis(self):
        """Тест сериализации пустого плана."""
        schedule = ProductionSchedule()

        result = schedule.to_redis_dict()

        assert result["_type"] == "ProductionSchedule"
        assert result["rows"] == []

    def test_production_schedule_complex_scenario(self):
        """Тест комплексного сценария работы с планом."""
        schedule = ProductionSchedule()

        # Добавляем несколько строк
        row1 = ProductionPlanRow(
            tender_id="tender_001",
            product_name="Изделие А",
            priority=1,
            planned_quantity=100,
            actual_quantity=50,
            remaining_to_produce=50,
        )
        row2 = ProductionPlanRow(
            tender_id="tender_002",
            product_name="Изделие Б",
            priority=2,
            planned_quantity=200,
            actual_quantity=0,
            remaining_to_produce=200,
        )
        row3 = ProductionPlanRow(
            tender_id="tender_003",
            product_name="Изделие В",
            priority=3,
            planned_quantity=300,
            actual_quantity=100,
            remaining_to_produce=200,
        )

        schedule.set_row(row1)
        schedule.set_row(row2)
        schedule.set_row(row3)

        assert len(schedule.rows) == 3

        # Обновляем строку для tender_002
        updated_row2 = ProductionPlanRow(
            tender_id="tender_002",
            product_name="Изделие Б Обновленное",
            priority=5,
            planned_quantity=250,
            actual_quantity=100,
            remaining_to_produce=150,
        )
        schedule.set_row(updated_row2)

        assert len(schedule.rows) == 3
        assert schedule.rows[1].tender_id == "tender_002"
        assert schedule.rows[1].product_name == "Изделие Б Обновленное"
        assert schedule.rows[1].priority == 5
        assert schedule.rows[1].planned_quantity == 250
        assert schedule.rows[1].actual_quantity == 100
        assert schedule.rows[1].remaining_to_produce == 150

        # Первая и третья строки не должны измениться
        assert schedule.rows[0].tender_id == "tender_001"
        assert schedule.rows[0].product_name == "Изделие А"
        assert schedule.rows[2].tender_id == "tender_003"
        assert schedule.rows[2].product_name == "Изделие В"

    def test_production_schedule_many_tenders(self):
        """Тест работы с большим количеством тендеров."""
        schedule = ProductionSchedule()

        # Добавляем 100 строк
        for i in range(100):
            row = ProductionPlanRow(
                tender_id=f"tender_{i:03d}",
                product_name=f"Изделие {i}",
                priority=i,
                planned_quantity=i * 10,
            )
            schedule.set_row(row)

        assert len(schedule.rows) == 100

        # Обновляем строку в середине
        updated_row = ProductionPlanRow(
            tender_id="tender_050",
            product_name="Обновленное изделие 50",
            priority=999,
            planned_quantity=9999,
        )
        schedule.set_row(updated_row)

        assert len(schedule.rows) == 100
        assert schedule.rows[50].tender_id == "tender_050"
        assert schedule.rows[50].priority == 999
        assert schedule.rows[50].planned_quantity == 9999

    def test_production_schedule_update_last_row(self):
        """Тест обновления последней строки в списке."""
        schedule = ProductionSchedule()

        schedule.set_row(ProductionPlanRow(tender_id="tender_001", priority=1))
        schedule.set_row(ProductionPlanRow(tender_id="tender_002", priority=2))
        schedule.set_row(ProductionPlanRow(tender_id="tender_003", priority=3))

        # Обновляем последнюю строку
        updated = ProductionPlanRow(
            tender_id="tender_003",
            priority=99,
            product_name="Обновленное последнее",
        )
        schedule.set_row(updated)

        assert len(schedule.rows) == 3
        assert schedule.rows[2].tender_id == "tender_003"
        assert schedule.rows[2].priority == 99
        assert schedule.rows[2].product_name == "Обновленное последнее"

    def test_production_schedule_update_first_row(self):
        """Тест обновления первой строки в списке."""
        schedule = ProductionSchedule()

        schedule.set_row(ProductionPlanRow(tender_id="tender_001", priority=1))
        schedule.set_row(ProductionPlanRow(tender_id="tender_002", priority=2))

        # Обновляем первую строку
        updated = ProductionPlanRow(
            tender_id="tender_001",
            priority=99,
            product_name="Обновленное первое",
        )
        schedule.set_row(updated)

        assert len(schedule.rows) == 2
        assert schedule.rows[0].tender_id == "tender_001"
        assert schedule.rows[0].priority == 99
        assert schedule.rows[0].product_name == "Обновленное первое"
