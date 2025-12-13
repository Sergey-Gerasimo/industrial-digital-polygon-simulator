"""
Интеграционные тесты для SimulationService сервиса.

Тесты проверяют все методы сервиса через gRPC, используя реальную базу данных
в Docker контейнере. Особое внимание уделено методам обновления состояния.
"""

import pytest
import uuid
import grpc

from grpc_generated.simulator_pb2 import (
    CreateSimulationRquest,
    GetSimulationRequest,
    RunSimulationRequest,
    # Конфигурация персонала
    SetLogistRequest,
    SetWarehouseInventoryWorkerRequest,
    SetWorkerOnWorkerplaceRequest,
    UnSetWorkerOnWorkerplaceRequest,
    # Конфигурация поставщиков
    AddSupplierRequest,
    DeleteSupplierRequest,
    # Конфигурация складов
    IncreaseWarehouseSizeRequest,
    # Управление графом процесса
    UpdateProcessGraphRequest,
    # Распределение плана (Производство)
    SetProductionPlanRowRequest,
    # Конфигурация тендеров
    AddTenderRequest,
    RemoveTenderRequest,
    # Общие настройки
    SetDealingWithDefectsRequest,
    SetSalesStrategyRequest,
    SetLeanImprovementStatusRequest,
    # Специфичные настройки по ролям
    SetQualityInspectionRequest,
    SetDeliveryPeriodRequest,
    SetCertificationStatusRequest,
    WarehouseType,
    GetMetricsRequest,
    GetAllMetricsRequest,
)
from grpc_generated.simulator_pb2_grpc import SimulationServiceStub
from domain import (
    Qualification,
    Specialization,
    ConsumerType,
    PaymentForm,
    DealingWithDefects,
    SaleStrategest,
)


class TestSimulationBasicMethods:
    """Тесты для базовых методов работы с симуляцией."""

    def test_create_simulation(self, simulation_stub, db_manager_stub):
        """Тест создания симуляции."""
        request = CreateSimulationRquest()
        response = simulation_stub.create_simulation(request)

        # SimulationResponse имеет поле simulations типа Simulation (не список)
        assert response.HasField("simulations")

        simulation = response.simulations
        assert simulation.simulation_id
        assert simulation.capital == 10000000  # Дефолтный капитал из фабрики
        assert len(simulation.parameters) == 1
        assert simulation.parameters[0].step == 1  # Начальный шаг должен быть 1

    def test_get_simulation(self, simulation_stub, db_manager_stub):
        """Тест получения симуляции по ID."""
        # Создаем симуляцию
        create_request = CreateSimulationRquest()
        create_response = simulation_stub.create_simulation(create_request)
        assert create_response.HasField("simulations")

        simulation_id = create_response.simulations.simulation_id

        # Получаем симуляцию
        get_request = GetSimulationRequest(simulation_id=simulation_id)
        get_response = simulation_stub.get_simulation(get_request)

        assert get_response.HasField("simulations")
        assert get_response.simulations.simulation_id == simulation_id


class TestRunSimulation:
    """Тесты для метода run_simulation с проверкой ограничения на 4 шага."""

    def test_run_simulation_basic(self, simulation_stub, db_manager_stub):
        """Тест базового вызова run_simulation."""
        # Создаем симуляцию
        create_request = CreateSimulationRquest()
        create_response = simulation_stub.create_simulation(create_request)
        simulation_id = create_response.simulations.simulation_id

        # Запускаем симуляцию
        run_request = RunSimulationRequest(simulation_id=simulation_id)
        response = simulation_stub.run_simulation(run_request)

        # SimulationResponse имеет поле simulations типа Simulation (не список)
        assert response.HasField("simulations")

        simulation = response.simulations
        # После первого запуска должно быть:
        # - 1 результат для step=1
        # - 2 параметра (step=1 и step=2)
        # Проверяем, что результаты и параметры соответствуют ожидаемым значениям
        assert len(simulation.results) == 1
        assert simulation.results[0].step == 1
        assert len(simulation.parameters) == 2
        params_by_step = sorted(simulation.parameters, key=lambda p: p.step)
        assert params_by_step[0].step == 1
        assert params_by_step[1].step == 2
        assert len(simulation.results) == 1

        assert simulation.results[0].step == 1
        assert len(simulation.parameters) == 2

        params_by_step = sorted(simulation.parameters, key=lambda p: p.step)
        assert params_by_step[0].step == 1
        assert params_by_step[1].step == 2

    def test_run_simulation_stops_at_step_4(self, simulation_stub, db_manager_stub):
        """Тест что run_simulation останавливается на шаге 4 и выдает ошибку при 5-м запуске."""
        # Создаем симуляцию
        create_request = CreateSimulationRquest()
        create_response = simulation_stub.create_simulation(create_request)
        simulation_id = create_response.simulations.simulation_id

        # Запускаем симуляцию 4 раза успешно (шаги 1-4)
        for i in range(4):
            run_request = RunSimulationRequest(simulation_id=simulation_id)
            response = simulation_stub.run_simulation(run_request)

            # Проверяем что запрос успешен
            assert response.HasField("simulations")

            # Получаем актуальное состояние после каждого запуска
            get_request = GetSimulationRequest(simulation_id=simulation_id)
            get_response = simulation_stub.get_simulation(get_request)
            simulation = get_response.simulations

            # Проверяем что количество параметров и результатов не превышает 4
            assert (
                len(simulation.parameters) <= 4
            ), f"После {i+1} запуска количество параметров превышает 4: {len(simulation.parameters)}"
            assert (
                len(simulation.results) <= 4
            ), f"После {i+1} запуска количество результатов превышает 4: {len(simulation.results)}"

        # Финальная проверка после 4 запусков
        get_request = GetSimulationRequest(simulation_id=simulation_id)
        get_response = simulation_stub.get_simulation(get_request)
        simulation = get_response.simulations

        # Должно быть ровно 4 параметра (шаги 1, 2, 3, 4)
        assert len(simulation.parameters) == 4
        params_by_step = sorted(simulation.parameters, key=lambda p: p.step)
        assert params_by_step[0].step == 1
        assert params_by_step[1].step == 2
        assert params_by_step[2].step == 3
        assert params_by_step[3].step == 4

        # Должно быть ровно 4 результата (шаги 1, 2, 3, 4)
        assert len(simulation.results) == 4
        results_by_step = sorted(simulation.results, key=lambda r: r.step)
        assert results_by_step[0].step == 1
        assert results_by_step[1].step == 2
        assert results_by_step[2].step == 3
        assert results_by_step[3].step == 4

        # Проверяем что результаты содержат все необходимые метрики
        for result in simulation.results:
            assert result.HasField("factory_metrics")
            assert result.HasField("production_metrics")
            assert result.HasField("quality_metrics")
            assert result.HasField("engineering_metrics")
            assert result.HasField("commercial_metrics")
            assert result.HasField("procurement_metrics")
            assert result.profit >= 0
            assert result.cost >= 0

        # Пытаемся запустить симуляцию 5-й раз - должна быть ошибка
        run_request = RunSimulationRequest(simulation_id=simulation_id)
        with pytest.raises(grpc.RpcError) as exc_info:
            simulation_stub.run_simulation(run_request)

        # Проверяем что это именно ошибка FAILED_PRECONDITION
        assert exc_info.value.code() == grpc.StatusCode.FAILED_PRECONDITION
        assert "Максимальное количество шагов симуляции (4) уже достигнуто" in str(
            exc_info.value.details()
        )

        # Проверяем, что состояние не изменилось после попытки 5-го запуска
        get_request_after = GetSimulationRequest(simulation_id=simulation_id)
        get_response_after = simulation_stub.get_simulation(get_request_after)
        simulation_after = get_response_after.simulations

        # Все еще должно быть ровно 4 параметра и 4 результата
        assert len(simulation_after.parameters) == 4
        assert len(simulation_after.results) == 4

    def test_run_simulation_updates_results_and_parameters(
        self, simulation_stub, db_manager_stub
    ):
        """Тест что run_simulation корректно обновляет results и parameters."""
        # Создаем симуляцию
        create_request = CreateSimulationRquest()
        create_response = simulation_stub.create_simulation(create_request)
        simulation_id = create_response.simulations.simulation_id

        # Изначально должно быть 1 параметр и 0 результатов
        get_request = GetSimulationRequest(simulation_id=simulation_id)
        initial_response = simulation_stub.get_simulation(get_request)
        initial_simulation = initial_response.simulations
        assert len(initial_simulation.parameters) == 1
        assert len(initial_simulation.results) == 0

        # Запускаем симуляцию 4 раза
        for step in range(1, 5):
            run_request = RunSimulationRequest(simulation_id=simulation_id)
            response = simulation_stub.run_simulation(run_request)

            # Проверяем состояние после каждого запуска
            get_request = GetSimulationRequest(simulation_id=simulation_id)
            get_response = simulation_stub.get_simulation(get_request)
            simulation = get_response.simulations

            # После каждого запуска должно быть step результатов и step+1 параметров
            # (если step < 4) или 4 параметра (если step == 4)
            expected_results = step
            expected_params = min(step + 1, 4)

            assert (
                len(simulation.results) == expected_results
            ), f"После {step} запуска ожидалось {expected_results} результатов, получено {len(simulation.results)}"
            assert (
                len(simulation.parameters) == expected_params
            ), f"После {step} запуска ожидалось {expected_params} параметров, получено {len(simulation.parameters)}"

            # Проверяем что последний результат имеет правильный step
            if simulation.results:
                last_result = max(simulation.results, key=lambda r: r.step)
                assert last_result.step == step

            # Проверяем что последний параметр имеет правильный step
            if simulation.parameters:
                last_param = max(simulation.parameters, key=lambda p: p.step)
                expected_param_step = min(step + 1, 4)
                assert last_param.step == expected_param_step

    def test_run_simulation_fails_after_step_4(self, simulation_stub, db_manager_stub):
        """Тест что run_simulation выдает ошибку при попытке запустить в 5-й раз."""
        # Создаем симуляцию
        create_request = CreateSimulationRquest()
        create_response = simulation_stub.create_simulation(create_request)
        simulation_id = create_response.simulations.simulation_id

        # Запускаем симуляцию 4 раза (нормально)
        for _ in range(4):
            run_request = RunSimulationRequest(simulation_id=simulation_id)
            response = simulation_stub.run_simulation(run_request)
            # Проверяем что запрос успешен
            assert response.HasField("simulations")

        # Проверяем что действительно есть 4 результата и 4 параметра
        get_request = GetSimulationRequest(simulation_id=simulation_id)
        get_response = simulation_stub.get_simulation(get_request)
        simulation = get_response.simulations
        assert len(simulation.results) == 4
        assert len(simulation.parameters) == 4

        # Попытка запустить в 5-й раз должна выдать ошибку
        run_request = RunSimulationRequest(simulation_id=simulation_id)
        with pytest.raises(grpc.RpcError) as exc_info:
            simulation_stub.run_simulation(run_request)

        assert exc_info.value.code() == grpc.StatusCode.FAILED_PRECONDITION
        assert (
            "максимальное количество шагов" in exc_info.value.details().lower()
            or "максимальное количество шагов" in exc_info.value.details()
        )


class TestStateUpdateMethods:
    """Тесты для методов обновления состояния симуляции."""

    def test_set_logist(self, simulation_stub, db_manager_stub):
        """Тест установки логиста."""
        # Создаем симуляцию
        create_request = CreateSimulationRquest()
        create_response = simulation_stub.create_simulation(create_request)
        simulation_id = create_response.simulations.simulation_id

        # Создаем логиста через db_manager
        from grpc_generated.simulator_pb2 import CreateLogistRequest
        from domain import VehicleType

        logist_request = CreateLogistRequest(
            name="Test Logist",
            qualification=Qualification.III.value,
            specialty=Specialization.LOGIST.value,
            salary=60000,
            speed=50,
            vehicle_type=VehicleType.TRUCK.value,
        )
        logist = db_manager_stub.create_logist(logist_request)
        assert logist.worker_id

        # Устанавливаем логиста
        set_request = SetLogistRequest(
            simulation_id=simulation_id,
            worker_id=logist.worker_id,
        )
        response = simulation_stub.set_logist(set_request)

        assert response.HasField("simulations")
        # Проверяем что логист установлен
        get_request = GetSimulationRequest(simulation_id=simulation_id)
        get_response = simulation_stub.get_simulation(get_request)
        simulation = get_response.simulations
        # Логист должен быть в параметрах
        assert simulation.parameters[0].HasField("logist")
        assert simulation.parameters[0].logist.worker_id == logist.worker_id

    def test_set_warehouse_inventory_worker(self, simulation_stub, db_manager_stub):
        """Тест установки складского работника."""
        # Создаем симуляцию
        create_request = CreateSimulationRquest()
        create_response = simulation_stub.create_simulation(create_request)
        simulation_id = create_response.simulations.simulation_id

        # Создаем рабочего
        from grpc_generated.simulator_pb2 import CreateWorkerRequest

        worker_request = CreateWorkerRequest(
            name="Test Worker",
            qualification=Qualification.III.value,
            specialty=Specialization.ASSEMBLER.value,
            salary=50000,
        )
        worker = db_manager_stub.create_worker(worker_request)
        assert worker.worker_id

        # Устанавливаем складского работника для склада материалов
        set_request = SetWarehouseInventoryWorkerRequest(
            simulation_id=simulation_id,
            worker_id=worker.worker_id,
            warehouse_type=WarehouseType.WAREHOUSE_TYPE_MATERIALS,
        )
        response = simulation_stub.set_warehouse_inventory_worker(set_request)

        assert response.HasField("simulations")

    def test_add_supplier(self, simulation_stub, db_manager_stub):
        """Тест добавления поставщика."""
        # Создаем симуляцию
        create_request = CreateSimulationRquest()
        create_response = simulation_stub.create_simulation(create_request)
        simulation_id = create_response.simulations.simulation_id

        # Создаем поставщика
        from grpc_generated.simulator_pb2 import CreateSupplierRequest

        supplier_request = CreateSupplierRequest(
            name="Test Supplier",
            product_name="Test Product",
            material_type="Metal",
            delivery_period=30,
            reliability=0.95,
            product_quality=0.90,
            cost=1000,
        )
        supplier = db_manager_stub.create_supplier(supplier_request)
        assert supplier.supplier_id

        # Добавляем поставщика к симуляции
        add_request = AddSupplierRequest(
            simulation_id=simulation_id,
            supplier_id=supplier.supplier_id,
            is_backup=False,
        )
        response = simulation_stub.add_supplier(add_request)

        assert response.HasField("simulations")

        # Проверяем что поставщик добавлен
        get_request = GetSimulationRequest(simulation_id=simulation_id)
        get_response = simulation_stub.get_simulation(get_request)
        simulation = get_response.simulations
        # Поставщик должен быть в списке suppliers параметров
        supplier_ids = [s.supplier_id for s in simulation.parameters[0].suppliers]
        assert supplier.supplier_id in supplier_ids

    def test_add_tender(self, simulation_stub, db_manager_stub):
        """Тест добавления тендера."""
        # Создаем симуляцию
        create_request = CreateSimulationRquest()
        create_response = simulation_stub.create_simulation(create_request)
        simulation_id = create_response.simulations.simulation_id

        # Создаем заказчика и тендер
        from grpc_generated.simulator_pb2 import (
            CreateConsumerRequest,
            CreateTenderRequest,
        )

        consumer_request = CreateConsumerRequest(
            name="Test Consumer",
            type=ConsumerType.NOT_GOVERMANT.value,
        )
        consumer = db_manager_stub.create_consumer(consumer_request)

        tender_request = CreateTenderRequest(
            consumer_id=consumer.consumer_id,
            cost=100000,
            quantity_of_products=100,
            penalty_per_day=1000,
            warranty_years=2,
            payment_form=PaymentForm.FULL_ADVANCE.value,
        )
        tender = db_manager_stub.create_tender(tender_request)
        assert tender.tender_id

        # Добавляем тендер к симуляции
        add_request = AddTenderRequest(
            simulation_id=simulation_id,
            tender_id=tender.tender_id,
        )
        response = simulation_stub.add_tender(add_request)

        assert response.HasField("simulations")

    def test_set_dealing_with_defects(self, simulation_stub, db_manager_stub):
        """Тест установки политики работы с дефектами."""
        # Создаем симуляцию
        create_request = CreateSimulationRquest()
        create_response = simulation_stub.create_simulation(create_request)
        simulation_id = create_response.simulations.simulation_id

        # Устанавливаем политику
        set_request = SetDealingWithDefectsRequest(
            simulation_id=simulation_id,
            dealing_with_defects=DealingWithDefects.DISPOSE.value,
        )
        response = simulation_stub.set_dealing_with_defects(set_request)

        assert response.HasField("simulations")

        # Проверяем что политика установлена
        get_request = GetSimulationRequest(simulation_id=simulation_id)
        get_response = simulation_stub.get_simulation(get_request)
        simulation = get_response.simulations
        assert (
            simulation.parameters[0].dealing_with_defects
            == DealingWithDefects.DISPOSE.value
        )

    def test_set_sales_strategy(self, simulation_stub, db_manager_stub):
        """Тест установки стратегии продаж."""
        # Создаем симуляцию
        create_request = CreateSimulationRquest()
        create_response = simulation_stub.create_simulation(create_request)
        simulation_id = create_response.simulations.simulation_id

        # Устанавливаем стратегию
        set_request = SetSalesStrategyRequest(
            simulation_id=simulation_id,
            strategy=SaleStrategest.LOW_PRICES.value,
        )
        response = simulation_stub.set_sales_strategy(set_request)

        assert response.HasField("simulations")

        # Проверяем что стратегия установлена
        get_request = GetSimulationRequest(simulation_id=simulation_id)
        get_response = simulation_stub.get_simulation(get_request)
        simulation = get_response.simulations
        assert (
            simulation.parameters[0].sales_strategy == SaleStrategest.LOW_PRICES.value
        )

    def test_set_lean_improvement_status(self, simulation_stub, db_manager_stub):
        """Тест установки статуса LEAN улучшения."""
        # Создаем симуляцию (улучшения уже должны быть в ней после создания)
        create_request = CreateSimulationRquest()
        create_response = simulation_stub.create_simulation(create_request)
        simulation_id = create_response.simulations.simulation_id

        # Получаем симуляцию и проверяем, что улучшения уже в ней
        get_request = GetSimulationRequest(simulation_id=simulation_id)
        get_response = simulation_stub.get_simulation(get_request)
        simulation = get_response.simulations

        # Проверяем, что улучшения уже есть в симуляции
        assert (
            len(simulation.parameters[0].lean_improvements) > 0
        ), "Улучшения должны быть уже в симуляции после создания"

        # Берем имя первого доступного улучшения
        improvement_name = simulation.parameters[0].lean_improvements[0].name
        assert improvement_name, "Улучшение должно иметь имя"

        # Устанавливаем статус улучшения (которое уже есть в симуляции)
        set_request = SetLeanImprovementStatusRequest(
            simulation_id=simulation_id,
            name=improvement_name,
            is_implemented=True,
        )
        response = simulation_stub.set_lean_improvement_status(set_request)

        assert response.HasField("simulations")

        # Проверяем, что статус обновился
        get_request_after = GetSimulationRequest(simulation_id=simulation_id)
        get_response_after = simulation_stub.get_simulation(get_request_after)
        simulation_after = get_response_after.simulations

        # Находим улучшение после обновления
        updated_improvement = None
        for improvement in simulation_after.parameters[0].lean_improvements:
            if improvement.name == improvement_name:
                updated_improvement = improvement
                break

        assert (
            updated_improvement is not None
        ), f"Улучшение '{improvement_name}' должно быть в списке"
        assert (
            updated_improvement.is_implemented is True
        ), f"Статус улучшения '{improvement_name}' должен быть True"

    def test_increase_warehouse_size(self, simulation_stub, db_manager_stub):
        """Тест увеличения размера склада."""
        # Создаем симуляцию
        create_request = CreateSimulationRquest()
        create_response = simulation_stub.create_simulation(create_request)
        simulation_id = create_response.simulations.simulation_id

        # Получаем начальный размер склада
        get_request = GetSimulationRequest(simulation_id=simulation_id)
        initial_response = simulation_stub.get_simulation(get_request)
        initial_size = initial_response.simulations.parameters[
            0
        ].materials_warehouse.size

        # Увеличиваем размер склада материалов
        increase_request = IncreaseWarehouseSizeRequest(
            simulation_id=simulation_id,
            warehouse_type=WarehouseType.WAREHOUSE_TYPE_MATERIALS,
            size=100,
        )
        response = simulation_stub.increase_warehouse_size(increase_request)

        assert response.HasField("simulations")

        # Проверяем что размер увеличился
        get_request = GetSimulationRequest(simulation_id=simulation_id)
        get_response = simulation_stub.get_simulation(get_request)
        new_size = get_response.simulations.parameters[0].materials_warehouse.size
        assert new_size == initial_size + 100

    # -----------------------------------------------------------------
    #          Тесты для получения метрик
    # -----------------------------------------------------------------

    def test_get_factory_metrics_success(self, simulation_stub):
        """Тест успешного получения метрик завода."""
        # Создаем симуляцию и выполняем шаг
        create_response = simulation_stub.create_simulation(CreateSimulationRquest())
        simulation_id = create_response.simulations.simulation_id

        # Запускаем симуляцию (нужен хотя бы один шаг)
        run_response = simulation_stub.run_simulation(
            RunSimulationRequest(simulation_id=simulation_id)
        )
        assert run_response.simulations

        # Получаем метрики завода с указанием step=1
        metrics_response = simulation_stub.get_factory_metrics(
            GetMetricsRequest(simulation_id=simulation_id, step=1)
        )

        assert metrics_response.metrics
        assert hasattr(metrics_response.metrics, "total_procurement_cost")
        assert hasattr(metrics_response.metrics, "profitability")
        assert hasattr(metrics_response.metrics, "oee")
        assert isinstance(metrics_response.timestamp, str)

    def test_get_production_metrics_success(self, simulation_stub):
        """Тест успешного получения метрик производства."""
        # Создаем симуляцию и выполняем шаг
        create_response = simulation_stub.create_simulation(CreateSimulationRquest())
        simulation_id = create_response.simulations.simulation_id

        # Запускаем симуляцию
        run_response = simulation_stub.run_simulation(
            RunSimulationRequest(simulation_id=simulation_id)
        )
        assert run_response.simulations

        # Получаем метрики производства с указанием step=1
        metrics_response = simulation_stub.get_production_metrics(
            GetMetricsRequest(simulation_id=simulation_id, step=1)
        )

        assert metrics_response.metrics
        assert isinstance(metrics_response.timestamp, str)

    def test_get_quality_metrics_success(self, simulation_stub):
        """Тест успешного получения метрик качества."""
        # Создаем симуляцию и выполняем шаг
        create_response = simulation_stub.create_simulation(CreateSimulationRquest())
        simulation_id = create_response.simulations.simulation_id

        # Запускаем симуляцию
        run_response = simulation_stub.run_simulation(
            RunSimulationRequest(simulation_id=simulation_id)
        )
        assert run_response.simulations

        # Получаем метрики качества с указанием step=1
        metrics_response = simulation_stub.get_quality_metrics(
            GetMetricsRequest(simulation_id=simulation_id, step=1)
        )

        assert metrics_response.metrics
        assert isinstance(metrics_response.timestamp, str)

    def test_get_engineering_metrics_success(self, simulation_stub):
        """Тест успешного получения инженерных метрик."""
        # Создаем симуляцию и выполняем шаг
        create_response = simulation_stub.create_simulation(CreateSimulationRquest())
        simulation_id = create_response.simulations.simulation_id

        # Запускаем симуляцию
        run_response = simulation_stub.run_simulation(
            RunSimulationRequest(simulation_id=simulation_id)
        )
        assert run_response.simulations

        # Получаем инженерные метрики с указанием step=1
        metrics_response = simulation_stub.get_engineering_metrics(
            GetMetricsRequest(simulation_id=simulation_id, step=1)
        )

        assert metrics_response.metrics
        assert isinstance(metrics_response.timestamp, str)

    def test_get_commercial_metrics_success(self, simulation_stub):
        """Тест успешного получения коммерческих метрик."""
        # Создаем симуляцию и выполняем шаг
        create_response = simulation_stub.create_simulation(CreateSimulationRquest())
        simulation_id = create_response.simulations.simulation_id

        # Запускаем симуляцию
        run_response = simulation_stub.run_simulation(
            RunSimulationRequest(simulation_id=simulation_id)
        )
        assert run_response.simulations

        # Получаем коммерческие метрики с указанием step=1
        metrics_response = simulation_stub.get_commercial_metrics(
            GetMetricsRequest(simulation_id=simulation_id, step=1)
        )

        assert metrics_response.metrics
        assert isinstance(metrics_response.timestamp, str)

    def test_get_procurement_metrics_success(self, simulation_stub):
        """Тест успешного получения метрик закупок."""
        # Создаем симуляцию и выполняем шаг
        create_response = simulation_stub.create_simulation(CreateSimulationRquest())
        simulation_id = create_response.simulations.simulation_id

        # Запускаем симуляцию
        run_response = simulation_stub.run_simulation(
            RunSimulationRequest(simulation_id=simulation_id)
        )
        assert run_response.simulations

        # Получаем метрики закупок с указанием step=1
        metrics_response = simulation_stub.get_procurement_metrics(
            GetMetricsRequest(simulation_id=simulation_id, step=1)
        )

        assert metrics_response.metrics
        assert isinstance(metrics_response.timestamp, str)

    def test_get_all_metrics_success(self, simulation_stub):
        """Тест успешного получения всех метрик."""
        # Создаем симуляцию и выполняем шаг
        create_response = simulation_stub.create_simulation(CreateSimulationRquest())
        simulation_id = create_response.simulations.simulation_id

        # Запускаем симуляцию
        run_response = simulation_stub.run_simulation(
            RunSimulationRequest(simulation_id=simulation_id)
        )
        assert run_response.simulations

        # Получаем все метрики с указанием step=1
        all_metrics_response = simulation_stub.get_all_metrics(
            GetAllMetricsRequest(simulation_id=simulation_id, step=1)
        )

        assert all_metrics_response.factory
        assert all_metrics_response.production
        assert all_metrics_response.quality
        assert all_metrics_response.engineering
        assert all_metrics_response.commercial
        assert all_metrics_response.procurement
        assert isinstance(all_metrics_response.timestamp, str)

    def test_get_metrics_with_step_parameter(self, simulation_stub):
        """Тест получения метрик с параметром step - должен работать без ошибок."""
        # Создаем симуляцию
        create_response = simulation_stub.create_simulation(CreateSimulationRquest())
        simulation_id = create_response.simulations.simulation_id

        # Запускаем симуляцию несколько раз для создания нескольких шагов
        # После первого запуска: step=1 доступен
        # После второго запуска: step=1 и step=2 доступны
        for _ in range(2):
            run_response = simulation_stub.run_simulation(
                RunSimulationRequest(simulation_id=simulation_id)
            )
            assert run_response.simulations

        # Проверяем, что результаты созданы
        get_request = GetSimulationRequest(simulation_id=simulation_id)
        get_response = simulation_stub.get_simulation(get_request)
        simulation = get_response.simulations
        # После двух запусков должно быть 2 результата (step=1 и step=2)
        assert (
            len(simulation.results) >= 2
        ), f"Ожидалось минимум 2 результата, получено {len(simulation.results)}"
        result_steps = [r.step for r in simulation.results]
        assert 1 in result_steps, f"Step 1 должен быть в результатах: {result_steps}"
        assert 2 in result_steps, f"Step 2 должен быть в результатах: {result_steps}"

        # Получаем метрики с явным указанием step=1 - должно работать
        metrics_response = simulation_stub.get_factory_metrics(
            GetMetricsRequest(simulation_id=simulation_id, step=1)
        )
        assert metrics_response.metrics

        # Получаем метрики с step=2 - должно работать
        # После двух запусков должен быть доступен step=2
        metrics_response_2 = simulation_stub.get_factory_metrics(
            GetMetricsRequest(simulation_id=simulation_id, step=2)
        )
        assert metrics_response_2.metrics

        # Все типы метрик должны работать с step
        simulation_stub.get_production_metrics(
            GetMetricsRequest(simulation_id=simulation_id, step=1)
        )
        simulation_stub.get_quality_metrics(
            GetMetricsRequest(simulation_id=simulation_id, step=1)
        )
        simulation_stub.get_engineering_metrics(
            GetMetricsRequest(simulation_id=simulation_id, step=1)
        )
        simulation_stub.get_commercial_metrics(
            GetMetricsRequest(simulation_id=simulation_id, step=1)
        )
        simulation_stub.get_procurement_metrics(
            GetMetricsRequest(simulation_id=simulation_id, step=1)
        )
        simulation_stub.get_all_metrics(
            GetAllMetricsRequest(simulation_id=simulation_id, step=1)
        )

    def test_get_metrics_step_not_provided_error(self, simulation_stub):
        """Тест получения метрик без указания step - должна возникать ошибка."""
        # Создаем симуляцию и выполняем шаг
        create_response = simulation_stub.create_simulation(CreateSimulationRquest())
        simulation_id = create_response.simulations.simulation_id

        # Запускаем симуляцию
        run_response = simulation_stub.run_simulation(
            RunSimulationRequest(simulation_id=simulation_id)
        )
        assert run_response.simulations

        # Попытка получить метрики без указания step должна завершиться ошибкой
        # step=0 считается как "не указан" в protobuf
        with pytest.raises(grpc.RpcError) as exc_info:
            simulation_stub.get_factory_metrics(
                GetMetricsRequest(simulation_id=simulation_id, step=0)
            )

        assert exc_info.value.code() in [
            grpc.StatusCode.INVALID_ARGUMENT,
            grpc.StatusCode.INTERNAL,
            grpc.StatusCode.NOT_FOUND,
        ]

    def test_get_metrics_invalid_step_error(self, simulation_stub):
        """Тест получения метрик с несуществующим step - должна возникать ошибка."""
        # Создаем симуляцию и выполняем только один шаг
        create_response = simulation_stub.create_simulation(CreateSimulationRquest())
        simulation_id = create_response.simulations.simulation_id

        # Запускаем симуляцию один раз (step=1)
        run_response = simulation_stub.run_simulation(
            RunSimulationRequest(simulation_id=simulation_id)
        )
        assert run_response.simulations

        # Попытка получить метрики для step=5 (несуществующего) должна завершиться ошибкой
        with pytest.raises(grpc.RpcError) as exc_info:
            simulation_stub.get_factory_metrics(
                GetMetricsRequest(simulation_id=simulation_id, step=5)
            )

        assert exc_info.value.code() in [
            grpc.StatusCode.INTERNAL,
            grpc.StatusCode.NOT_FOUND,
        ]

    def test_get_metrics_simulation_not_found(self, simulation_stub):
        """Тест получения метрик для несуществующей симуляции."""
        non_existent_id = "non-existent-simulation-id"

        with pytest.raises(grpc.RpcError) as exc_info:
            simulation_stub.get_factory_metrics(
                GetMetricsRequest(simulation_id=non_existent_id, step=1)
            )

        assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND

        # То же самое для всех типов метрик
        with pytest.raises(grpc.RpcError) as exc_info:
            simulation_stub.get_production_metrics(
                GetMetricsRequest(simulation_id=non_existent_id, step=1)
            )
        assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND

        with pytest.raises(grpc.RpcError) as exc_info:
            simulation_stub.get_all_metrics(
                GetAllMetricsRequest(simulation_id=non_existent_id, step=1)
            )
        assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND

    def test_get_metrics_no_simulation_data(self, simulation_stub):
        """Тест получения метрик для симуляции без данных (только создана, не запущена)."""
        # Создаем симуляцию, но не запускаем
        create_response = simulation_stub.create_simulation(CreateSimulationRquest())
        simulation_id = create_response.simulations.simulation_id

        # Попытка получить метрики должна завершиться ошибкой
        # так как симуляция не имеет данных после шагов
        with pytest.raises(grpc.RpcError) as exc_info:
            simulation_stub.get_factory_metrics(
                GetMetricsRequest(simulation_id=simulation_id, step=1)
            )

        # Код ошибки может быть INTERNAL или NOT_FOUND в зависимости от реализации
        assert exc_info.value.code() in [
            grpc.StatusCode.INTERNAL,
            grpc.StatusCode.NOT_FOUND,
        ]
