"""Тесты для domain/simulaton.py - класс SimulationParameters"""

import pytest
from unittest.mock import AsyncMock, patch

from domain.simulaton import (
    SimulationParameters,
    SaleStrategest,
    DealingWithDefects,
)
from domain.warehouse import Warehouse
from domain.worker import Worker
from domain.supplier import Supplier
from domain.tender import Tender
from domain.logist import Logist
from domain.process_graph import ProcessGraph, Route
from domain.workplace import Workplace
from domain.equipment import Equipment
from domain.certification import Certification
from domain.lean_improvement import LeanImprovement
from domain.production_plan import ProductionSchedule, ProductionPlanRow


class TestSimulationParameters:
    """Тесты для класса SimulationParameters."""

    def test_creation_with_defaults(self):
        """Тест создания SimulationParameters со значениями по умолчанию."""
        params = SimulationParameters()

        assert params.logist is None
        assert params.suppliers == []
        assert params.backup_suppliers == []
        assert isinstance(params.materials_warehouse, Warehouse)
        assert isinstance(params.product_warehouse, Warehouse)
        assert isinstance(params.processes, ProcessGraph)
        assert params.tenders == []
        assert params.dealing_with_defects == DealingWithDefects.NONE
        assert params.production_improvements == []
        assert params.sales_strategy == SaleStrategest.NONE
        assert isinstance(params.production_schedule, ProductionSchedule)
        assert params.certifications == []
        assert params.lean_improvements == []
        assert params.capital == 10000000

    def test_from_simulation_parameters(self):
        """Тест создания копии SimulationParameters."""
        original = SimulationParameters(capital=5000000)
        copy = SimulationParameters.from_simulation_parameters(original)

        assert copy.capital == 5000000
        assert copy is not original
        # Изменение копии не должно влиять на оригинал
        copy.capital = 1000
        assert original.capital == 5000000

    @pytest.mark.asyncio
    async def test_create_default(self):
        """Тест создания параметров с дефолтными значениями из БД."""
        # Мокаем сессию и репозитории
        mock_session = AsyncMock()
        mock_lean_repo = AsyncMock()
        mock_workplace_repo = AsyncMock()

        # Мокаем данные из БД
        mock_lean_repo.get_all = AsyncMock(
            return_value=[
                LeanImprovement(
                    improvement_id="imp1",
                    name="Улучшение 1",
                    is_implemented=True,
                ),
                LeanImprovement(
                    improvement_id="imp2",
                    name="Улучшение 2",
                    is_implemented=True,
                ),
            ]
        )

        mock_workplace_repo.get_all = AsyncMock(
            return_value=[
                Workplace(workplace_id="wp1", worker=Worker(worker_id="w1")),
                Workplace(workplace_id="wp2", equipment=Equipment(equipment_id="e1")),
            ]
        )

        # Патчим импорты в правильном месте
        with (
            patch(
                "application.simulation_factory.LeanImprovementRepository",
                return_value=mock_lean_repo,
            ),
            patch(
                "application.simulation_factory.WorkplaceRepository",
                return_value=mock_workplace_repo,
            ),
        ):
            from application.simulation_factory import (
                create_default_simulation_parameters,
            )

            params = await create_default_simulation_parameters(mock_session)

            # Проверяем что улучшения созданы с is_implemented=False
            assert len(params.lean_improvements) == 2
            assert all(not imp.is_implemented for imp in params.lean_improvements)

            # Проверяем что рабочие места без worker и equipment
            assert len(params.processes.workplaces) == 2
            assert all(wp.worker is None for wp in params.processes.workplaces)
            assert all(wp.equipment is None for wp in params.processes.workplaces)

            # Проверяем что routes пуст
            assert params.processes.routes == []

    def test_set_sales_strategy(self):
        """Тест установки стратегии продаж."""
        params = SimulationParameters()

        # Валидная стратегия
        params.set_sales_strategy("none")
        assert params.sales_strategy == SaleStrategest.NONE

        params.set_sales_strategy("Низкие цены")
        assert params.sales_strategy == SaleStrategest.LOW_PRICES

        # Невалидная стратегия
        with pytest.raises(ValueError, match="Недопустимое значение"):
            params.set_sales_strategy("invalid")

        # Не строка
        with pytest.raises(ValueError, match="должна быть строкой"):
            params.set_sales_strategy(123)

    def test_add_product_improvement(self):
        """Тест добавления улучшения производства."""
        params = SimulationParameters()
        improvement = LeanImprovement(
            improvement_id="imp1", name="Улучшение 1", is_implemented=False
        )
        params.production_improvements = [improvement]

        params.add_product_inprovement("Улучшение 1")
        assert improvement.is_implemented is True

        # Несуществующее улучшение
        with pytest.raises(ValueError, match="не найдено"):
            params.add_product_inprovement("Несуществующее")

    def test_remove_product_improvement(self):
        """Тест удаления улучшения производства."""
        params = SimulationParameters()
        improvement = LeanImprovement(
            improvement_id="imp1", name="Улучшение 1", is_implemented=True
        )
        params.production_improvements = [improvement]

        params.remove_product_improvement("Улучшение 1")
        assert improvement.is_implemented is False

        # Несуществующее улучшение
        with pytest.raises(ValueError, match="не найдено"):
            params.remove_product_improvement("Несуществующее")

    def test_add_tender(self):
        """Тест добавления тендера."""
        params = SimulationParameters()
        tender = Tender(tender_id="t1", quantity_of_products=100)

        params.add_tender(tender)

        assert tender in params.tenders
        assert len(params.production_schedule.rows) == 1
        assert params.production_schedule.rows[0].tender_id == "t1"
        assert params.production_schedule.rows[0].planned_quantity == 100

        # Дубликат
        with pytest.raises(ValueError, match="уже существует"):
            params.add_tender(tender)

    def test_remove_tender(self):
        """Тест удаления тендера."""
        params = SimulationParameters()
        tender = Tender(tender_id="t1", quantity_of_products=100)
        params.add_tender(tender)

        params.remove_tender("t1")

        assert tender not in params.tenders
        assert len(params.production_schedule.rows) == 0

    def test_set_logist(self):
        """Тест установки логиста."""
        params = SimulationParameters()
        logist = Logist(worker_id="l1", name="Логист 1")

        params.set_logist(logist)
        assert params.logist == logist

        # Невалидный тип
        with pytest.raises(ValueError, match="должен быть объектом"):
            params.set_logist("not a logist")

    def test_set_has_certification(self):
        """Тест установки статуса сертификации."""
        params = SimulationParameters()
        cert = Certification(certificate_type="ISO9001", is_obtained=False)
        params.certifications = [cert]

        params.set_has_certification("ISO9001", True)
        assert cert.is_obtained is True

        params.set_has_certification("ISO9001", False)
        assert cert.is_obtained is False

        # Несуществующая сертификация
        with pytest.raises(ValueError, match="не найдена"):
            params.set_has_certification("INVALID", True)

    def test_set_certification_status(self):
        """Тест установки статуса сертификации (альтернативный метод)."""
        params = SimulationParameters()
        cert = Certification(certificate_type="ISO9001", is_obtained=False)
        params.certifications = [cert]

        params.set_certification_status("ISO9001", True)
        assert cert.is_obtained is True

        # Несуществующая сертификация
        with pytest.raises(ValueError, match="не найдена"):
            params.set_certification_status("INVALID", True)

    def test_add_supplier(self):
        """Тест добавления поставщика."""
        params = SimulationParameters()
        supplier = Supplier(supplier_id="s1", name="Поставщик 1")

        params.add_supplier(supplier)
        assert supplier in params.suppliers

        # Дубликат
        with pytest.raises(ValueError, match="уже существует"):
            params.add_supplier(supplier)

        # Невалидный тип
        with pytest.raises(ValueError, match="должен быть объектом"):
            params.add_supplier("not a supplier")

    def test_remove_supplier(self):
        """Тест удаления поставщика."""
        params = SimulationParameters()
        supplier = Supplier(supplier_id="s1", name="Поставщик 1")
        params.add_supplier(supplier)

        params.remove_supplier("s1")
        assert supplier not in params.suppliers

    def test_add_backup_supplier(self):
        """Тест добавления резервного поставщика."""
        params = SimulationParameters()
        supplier = Supplier(supplier_id="bs1", name="Резервный поставщик 1")

        params.add_backup_supplier(supplier)
        assert supplier in params.backup_suppliers

        # Дубликат
        with pytest.raises(ValueError, match="уже существует"):
            params.add_backup_supplier(supplier)

    def test_remove_backup_supplier(self):
        """Тест удаления резервного поставщика."""
        params = SimulationParameters()
        supplier = Supplier(supplier_id="bs1", name="Резервный поставщик 1")
        params.add_backup_supplier(supplier)

        params.remove_backup_supplier("bs1")
        assert supplier not in params.backup_suppliers

    def test_set_material_warehouse_inventory_worker(self):
        """Тест установки кладовщика на склад материалов."""
        params = SimulationParameters()
        worker = Worker(worker_id="w1", name="Кладовщик 1")

        params.set_material_warehouse_inventory_worker(worker)
        assert params.materials_warehouse.inventory_worker == worker

        # Невалидный тип
        with pytest.raises(ValueError, match="должен быть объектом"):
            params.set_material_warehouse_inventory_worker("not a worker")

    def test_set_product_warehouse_inventory_worker(self):
        """Тест установки кладовщика на склад продукции."""
        params = SimulationParameters()
        worker = Worker(worker_id="w1", name="Кладовщик 1")

        params.set_product_warehouse_inventory_worker(worker)
        assert params.product_warehouse.inventory_worker == worker

    def test_increase_material_warehouse_size(self):
        """Тест увеличения размера склада материалов."""
        params = SimulationParameters(capital=10000000)
        initial_size = params.materials_warehouse.size

        params.increase_material_warehouse_size(100)
        assert params.materials_warehouse.size == initial_size + 100
        assert params.capital == 10000000 - 100 * 100

        # Недостаточно капитала
        params.capital = 100
        with pytest.raises(ValueError, match="Недостаточно капитала"):
            params.increase_material_warehouse_size(10)

        # Нулевой или отрицательный размер
        with pytest.raises(ValueError, match="больше нуля"):
            params.increase_material_warehouse_size(0)
        with pytest.raises(ValueError, match="больше нуля"):
            params.increase_material_warehouse_size(-10)

    def test_increase_product_warehouse_size(self):
        """Тест увеличения размера склада продукции."""
        params = SimulationParameters(capital=10000000)
        initial_size = params.product_warehouse.size

        params.increase_product_warehouse_size(50)
        assert params.product_warehouse.size == initial_size + 50
        assert params.capital == 10000000 - 50 * 100

    def test_set_process_graph(self):
        """Тест установки графа процесса."""
        params = SimulationParameters()
        wp1 = Workplace(workplace_id="wp1")
        wp2 = Workplace(workplace_id="wp2")
        params.processes.workplaces = [wp1, wp2]

        # Создаем новый граф с теми же рабочими местами и новым маршрутом
        new_graph = ProcessGraph(
            process_graph_id="new_id",
            workplaces=[wp1, wp2],
            routes=[Route(from_workplace="wp1", to_workplace="wp2", length=10)],
        )

        params.set_process_graph(new_graph)

        assert params.processes.process_graph_id == "new_id"
        assert len(params.processes.routes) == 1

        # Попытка добавить новое рабочее место (не должно быть разрешено)
        wp3 = Workplace(workplace_id="wp3")
        invalid_graph = ProcessGraph(workplaces=[wp1, wp2, wp3])
        with pytest.raises(ValueError, match="нет в существующем"):
            params.set_process_graph(invalid_graph)

    def test_set_process_graph_updates_coordinates(self):
        """Тест что set_process_graph обновляет координаты существующих рабочих мест."""
        params = SimulationParameters()
        # Создаем рабочие места без координат (None)
        wp1 = Workplace(workplace_id="wp1", workplace_name="Workplace 1")
        wp2 = Workplace(workplace_id="wp2", workplace_name="Workplace 2")
        params.processes.workplaces = [wp1, wp2]

        # Проверяем, что изначально координаты None
        assert wp1.x is None
        assert wp1.y is None
        assert wp2.x is None
        assert wp2.y is None

        # Создаем новый граф с теми же рабочими местами, но с координатами
        new_wp1 = Workplace(workplace_id="wp1", workplace_name="Workplace 1", x=2, y=3)
        new_wp2 = Workplace(workplace_id="wp2", workplace_name="Workplace 2", x=5, y=1)
        new_graph = ProcessGraph(
            process_graph_id="updated_graph",
            workplaces=[new_wp1, new_wp2],
            routes=[],
        )

        params.set_process_graph(new_graph)

        # Проверяем, что координаты обновились
        assert wp1.x == 2
        assert wp1.y == 3
        assert wp2.x == 5
        assert wp2.y == 1

        # Проверяем, что другие поля не изменились
        assert wp1.workplace_id == "wp1"
        assert wp1.workplace_name == "Workplace 1"
        assert wp2.workplace_id == "wp2"
        assert wp2.workplace_name == "Workplace 2"

    def test_set_process_graph_updates_coordinates_to_none(self):
        """Тест что set_process_graph может обновить координаты обратно в None."""
        params = SimulationParameters()
        # Создаем рабочие места с координатами
        wp1 = Workplace(workplace_id="wp1", workplace_name="Workplace 1", x=2, y=3)
        wp2 = Workplace(workplace_id="wp2", workplace_name="Workplace 2", x=5, y=1)
        params.processes.workplaces = [wp1, wp2]

        # Проверяем, что изначально координаты установлены
        assert wp1.x == 2
        assert wp1.y == 3

        # Создаем новый граф с теми же рабочими местами, но с None координатами
        new_wp1 = Workplace(workplace_id="wp1", workplace_name="Workplace 1", x=None, y=None)
        new_wp2 = Workplace(workplace_id="wp2", workplace_name="Workplace 2", x=None, y=None)
        new_graph = ProcessGraph(
            process_graph_id="updated_graph",
            workplaces=[new_wp1, new_wp2],
            routes=[],
        )

        params.set_process_graph(new_graph)

        # Проверяем, что координаты обновились на None
        assert wp1.x is None
        assert wp1.y is None
        assert wp2.x is None
        assert wp2.y is None

    def test_set_process_graph_updates_coordinates_partial(self):
        """Тест обновления координат для части рабочих мест."""
        params = SimulationParameters()
        wp1 = Workplace(workplace_id="wp1", workplace_name="Workplace 1", x=1, y=1)
        wp2 = Workplace(workplace_id="wp2", workplace_name="Workplace 2", x=2, y=2)
        wp3 = Workplace(workplace_id="wp3", workplace_name="Workplace 3", x=3, y=3)
        params.processes.workplaces = [wp1, wp2, wp3]

        # Обновляем координаты только для wp1 и wp2
        new_wp1 = Workplace(workplace_id="wp1", workplace_name="Workplace 1", x=4, y=5)
        new_wp2 = Workplace(workplace_id="wp2", workplace_name="Workplace 2", x=6, y=0)
        # wp3 не включаем в новый граф (но он должен остаться в существующих)
        new_graph = ProcessGraph(
            process_graph_id="partial_update",
            workplaces=[new_wp1, new_wp2],  # только 2 из 3
            routes=[],
        )

        params.set_process_graph(new_graph)

        # Проверяем, что координаты wp1 и wp2 обновились
        assert wp1.x == 4
        assert wp1.y == 5
        assert wp2.x == 6
        assert wp2.y == 0

        # wp3 должен остаться с прежними координатами (но его нет в новом графе,
        # поэтому метод вызовет ошибку, так как все рабочие места из нового графа
        # должны существовать в старом)
        # На самом деле, метод проверяет что все новые рабочие места есть в существующих,
        # но не требует что все существующие есть в новых
        # Но в данном случае мы передаем только часть, поэтому всё должно быть ок
        # wp3 должен остаться с теми же координатами
        assert wp3.x == 3
        assert wp3.y == 3

    def test_set_process_graph_updates_only_specified_workplace_coordinates(self):
        """Тест что обновление координат одного рабочего места не влияет на остальные."""
        params = SimulationParameters()
        # Создаем несколько рабочих мест с разными координатами
        wp1 = Workplace(workplace_id="wp1", workplace_name="Workplace 1", x=1, y=1)
        wp2 = Workplace(workplace_id="wp2", workplace_name="Workplace 2", x=2, y=2)
        wp3 = Workplace(workplace_id="wp3", workplace_name="Workplace 3", x=None, y=None)
        wp4 = Workplace(workplace_id="wp4", workplace_name="Workplace 4", x=4, y=4)
        params.processes.workplaces = [wp1, wp2, wp3, wp4]

        # Сохраняем исходные координаты для проверки
        original_coords = {
            "wp1": (wp1.x, wp1.y),
            "wp2": (wp2.x, wp2.y),
            "wp3": (wp3.x, wp3.y),
            "wp4": (wp4.x, wp4.y),
        }

        # Обновляем координаты только для wp2
        new_wp1 = Workplace(workplace_id="wp1", workplace_name="Workplace 1", x=1, y=1)  # те же координаты
        new_wp2 = Workplace(workplace_id="wp2", workplace_name="Workplace 2", x=5, y=6)  # новые координаты
        new_wp3 = Workplace(workplace_id="wp3", workplace_name="Workplace 3", x=None, y=None)  # остаются None
        new_wp4 = Workplace(workplace_id="wp4", workplace_name="Workplace 4", x=4, y=4)  # те же координаты
        new_graph = ProcessGraph(
            process_graph_id="selective_update",
            workplaces=[new_wp1, new_wp2, new_wp3, new_wp4],
            routes=[],
        )

        params.set_process_graph(new_graph)

        # Проверяем, что только wp2 изменился
        assert wp1.x == 1, "wp1.x не должен измениться"
        assert wp1.y == 1, "wp1.y не должен измениться"
        assert wp2.x == 5, "wp2.x должен обновиться"
        assert wp2.y == 6, "wp2.y должен обновиться"
        assert wp3.x is None, "wp3.x должен остаться None"
        assert wp3.y is None, "wp3.y должен остаться None"
        assert wp4.x == 4, "wp4.x не должен измениться"
        assert wp4.y == 4, "wp4.y не должен измениться"

    def test_set_process_graph_one_workplace_gets_coordinates_others_stay_none(self):
        """Тест что одно рабочее место получает координаты, а остальные остаются с None."""
        params = SimulationParameters()
        # Создаем несколько рабочих мест все с None координатами
        wp1 = Workplace(workplace_id="wp1", workplace_name="Workplace 1", x=None, y=None)
        wp2 = Workplace(workplace_id="wp2", workplace_name="Workplace 2", x=None, y=None)
        wp3 = Workplace(workplace_id="wp3", workplace_name="Workplace 3", x=None, y=None)
        params.processes.workplaces = [wp1, wp2, wp3]

        # Проверяем, что все изначально None
        assert wp1.x is None
        assert wp1.y is None
        assert wp2.x is None
        assert wp2.y is None
        assert wp3.x is None
        assert wp3.y is None

        # Обновляем координаты только для wp2, остальные остаются None
        new_wp1 = Workplace(workplace_id="wp1", workplace_name="Workplace 1", x=None, y=None)
        new_wp2 = Workplace(workplace_id="wp2", workplace_name="Workplace 2", x=3, y=4)  # получает координаты
        new_wp3 = Workplace(workplace_id="wp3", workplace_name="Workplace 3", x=None, y=None)
        new_graph = ProcessGraph(
            process_graph_id="one_gets_coords",
            workplaces=[new_wp1, new_wp2, new_wp3],
            routes=[],
        )

        params.set_process_graph(new_graph)

        # Проверяем, что только wp2 получил координаты, остальные остались None
        assert wp1.x is None, "wp1.x должен остаться None"
        assert wp1.y is None, "wp1.y должен остаться None"
        assert wp2.x == 3, "wp2.x должен получить координату 3"
        assert wp2.y == 4, "wp2.y должен получить координату 4"
        assert wp3.x is None, "wp3.x должен остаться None"
        assert wp3.y is None, "wp3.y должен остаться None"

    def test_set_process_graph_one_workplace_loses_coordinates_others_keep(self):
        """Тест что одно рабочее место теряет координаты (становится None), а остальные сохраняют."""
        params = SimulationParameters()
        # Создаем несколько рабочих мест все с координатами
        wp1 = Workplace(workplace_id="wp1", workplace_name="Workplace 1", x=1, y=1)
        wp2 = Workplace(workplace_id="wp2", workplace_name="Workplace 2", x=2, y=2)
        wp3 = Workplace(workplace_id="wp3", workplace_name="Workplace 3", x=3, y=3)
        params.processes.workplaces = [wp1, wp2, wp3]

        # Проверяем, что все изначально имеют координаты
        assert wp1.x == 1
        assert wp1.y == 1
        assert wp2.x == 2
        assert wp2.y == 2
        assert wp3.x == 3
        assert wp3.y == 3

        # Обновляем: wp2 теряет координаты (становится None), остальные сохраняют
        new_wp1 = Workplace(workplace_id="wp1", workplace_name="Workplace 1", x=1, y=1)  # сохраняет
        new_wp2 = Workplace(workplace_id="wp2", workplace_name="Workplace 2", x=None, y=None)  # теряет координаты
        new_wp3 = Workplace(workplace_id="wp3", workplace_name="Workplace 3", x=3, y=3)  # сохраняет
        new_graph = ProcessGraph(
            process_graph_id="one_loses_coords",
            workplaces=[new_wp1, new_wp2, new_wp3],
            routes=[],
        )

        params.set_process_graph(new_graph)

        # Проверяем, что только wp2 потерял координаты, остальные сохранили
        assert wp1.x == 1, "wp1.x должен сохраниться"
        assert wp1.y == 1, "wp1.y должен сохраниться"
        assert wp2.x is None, "wp2.x должен стать None"
        assert wp2.y is None, "wp2.y должен стать None"
        assert wp3.x == 3, "wp3.x должен сохраниться"
        assert wp3.y == 3, "wp3.y должен сохраниться"

    def test_set_production_plan_row(self):
        """Тест обновления строки производственного плана."""
        params = SimulationParameters()

        # Сначала нужно создать строку через добавление тендера
        tender = Tender(tender_id="t1", quantity_of_products=100)
        params.add_tender(tender)
        assert len(params.production_schedule.rows) == 1

        # Теперь обновляем существующую строку
        updated_row = ProductionPlanRow(
            tender_id="t1", planned_quantity=200, actual_quantity=100
        )
        params.set_production_plan_row(updated_row)
        assert len(params.production_schedule.rows) == 1
        assert params.production_schedule.rows[0].planned_quantity == 200
        assert params.production_schedule.rows[0].actual_quantity == 100

        # Попытка обновить несуществующую строку должна вызвать ошибку
        non_existent_row = ProductionPlanRow(tender_id="t2", planned_quantity=300)
        with pytest.raises(ValueError, match="не найдена"):
            params.set_production_plan_row(non_existent_row)

    def test_set_quality_inspection(self):
        """Тест установки контроля качества для поставщика."""
        params = SimulationParameters()
        supplier = Supplier(supplier_id="s1")
        params.suppliers = [supplier]

        params.set_quality_inspection("s1", True)
        assert supplier.quality_inspection_enabled is True

        params.set_quality_inspection("s1", False)
        assert supplier.quality_inspection_enabled is False

        # Поставщик в резервных
        backup_supplier = Supplier(supplier_id="bs1")
        params.backup_suppliers = [backup_supplier]
        params.set_quality_inspection("bs1", True)
        assert backup_supplier.quality_inspection_enabled is True

        # Несуществующий поставщик
        with pytest.raises(ValueError, match="не найден"):
            params.set_quality_inspection("invalid", True)

    def test_set_delivery_period(self):
        """Тест установки периода поставок."""
        params = SimulationParameters()
        supplier = Supplier(supplier_id="s1")
        params.suppliers = [supplier]

        params.set_delivery_period("s1", 14)
        assert supplier.delivery_period_days == 14

        # Отрицательный период
        with pytest.raises(ValueError, match="неотрицательным"):
            params.set_delivery_period("s1", -1)

        # Несуществующий поставщик
        with pytest.raises(ValueError, match="не найден"):
            params.set_delivery_period("invalid", 14)

    def test_set_equipment_maintenance_interval(self):
        """Тест установки интервала обслуживания оборудования."""
        params = SimulationParameters()
        equipment = Equipment(equipment_id="e1")
        workplace = Workplace(workplace_id="wp1", equipment=equipment)
        params.processes.workplaces = [workplace]

        params.set_equipment_maintenance_interval("e1", 30)
        assert equipment.maintenance_period == 30

        # Отрицательный интервал
        with pytest.raises(ValueError, match="неотрицательным"):
            params.set_equipment_maintenance_interval("e1", -1)

        # Несуществующее оборудование
        with pytest.raises(ValueError, match="не найдено"):
            params.set_equipment_maintenance_interval("invalid", 30)

    def test_set_lean_improvement_status(self):
        """Тест установки статуса LEAN улучшения."""
        params = SimulationParameters()
        improvement = LeanImprovement(
            improvement_id="imp1", name="Улучшение 1", is_implemented=False
        )
        # set_lean_improvement_status ищет в lean_improvements, а не в production_improvements
        params.lean_improvements = [improvement]

        params.set_lean_improvement_status("Улучшение 1", True)
        assert improvement.is_implemented is True

        params.set_lean_improvement_status("Улучшение 1", False)
        assert improvement.is_implemented is False

        # Несуществующее улучшение
        with pytest.raises(ValueError, match="не найдено"):
            params.set_lean_improvement_status("Несуществующее", True)

    def test_get_required_materials(self):
        """Тест получения списка требуемых материалов."""
        params = SimulationParameters()
        materials = params.get_required_materials()

        assert isinstance(materials, list)
        # По умолчанию список должен быть пустым или содержать константы

    def test_get_available_improvements(self):
        """Тест получения списка доступных улучшений."""
        params = SimulationParameters()
        improvement1 = LeanImprovement(improvement_id="imp1", name="Улучшение 1")
        improvement2 = LeanImprovement(improvement_id="imp2", name="Улучшение 2")
        params.production_improvements = [improvement1, improvement2]

        names = params.get_available_improvements()

        assert isinstance(names, list)
        assert len(names) == 2
        assert "Улучшение 1" in names
        assert "Улучшение 2" in names

    def test_get_defect_policies(self):
        """Тест получения политик обработки дефектов."""
        params = SimulationParameters()
        params.dealing_with_defects = DealingWithDefects.DISPOSE

        policies, current = params.get_defect_policies()

        assert isinstance(policies, list)
        assert len(policies) > 0
        assert "Утилизировать" in policies
        assert current == "Утилизировать"
        assert isinstance(current, str)

    def test_complex_scenario(self):
        """Комплексный тест использования нескольких методов вместе."""
        params = SimulationParameters(capital=10000000)

        # Добавляем поставщика
        supplier = Supplier(supplier_id="s1", name="Поставщик 1")
        params.add_supplier(supplier)

        # Добавляем тендер
        tender = Tender(tender_id="t1", quantity_of_products=100)
        params.add_tender(tender)

        # Устанавливаем стратегию продаж
        params.set_sales_strategy("Низкие цены")

        # Увеличиваем размер склада
        params.increase_material_warehouse_size(50)

        # Проверяем результаты
        assert supplier in params.suppliers
        assert tender in params.tenders
        assert params.sales_strategy == SaleStrategest.LOW_PRICES
        assert params.capital == 10000000 - 50 * 100
        assert params.materials_warehouse.size == 1000 + 50
