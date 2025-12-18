"""
Интеграционные тесты для SimulationService сервиса.

Тесты проверяют все методы сервиса через gRPC, используя реальную базу данных
в Docker контейнере. Особое внимание уделено методам обновления состояния.
"""

import pytest
import uuid
import grpc

from grpc_generated.simulator_pb2 import (
    WAREHOUSE_TYPE_MATERIALS,
    CreateSimulationRquest,
    GetAllSuppliersRequest,
    GetAllWorkersRequest,
    GetAllWorkplacesRequest,
    GetAllTendersRequest,
    GetAllLeanImprovementsRequest,
    GetAllConsumersRequest,
    GetAllEquipmentRequest,
    GetAvailableDefectPoliciesRequest,
    GetAvailableSalesStrategiesRequest,
    GetAvailableCertificationsRequest,
    GetAvailableImprovementsListRequest,
    GetProcessGraphRequest,
    GetSimulationRequest,
    PingRequest,
    RunSimulationRequest,
    GetProductionScheduleRequest,
    GetWorkshopPlanRequest,
    GetUnplannedRepairRequest,
    GetWarehouseLoadChartRequest,
    GetRequiredMaterialsRequest,
    GetAvailableImprovementsRequest,
    GetDefectPoliciesRequest,
    GetMaterialTypesRequest,
    GetEquipmentTypesRequest,
    GetWorkplaceTypesRequest,
    ValidateConfigurationRequest,
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
    Workplace,
    Route,
    # Распределение плана (Производство)
    SetProductionPlanRowRequest,
    ProductionPlanRow,
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
    SetEquipmentMaintenanceIntervalRequest,
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


@pytest.fixture(scope="function")
def some_simulation(simulation_stub):
    request = CreateSimulationRquest()
    response = simulation_stub.create_simulation(request)
    return response


@pytest.fixture(scope="function")
def some_simulation_id(some_simulation):
    return some_simulation.simulations.simulation_id


@pytest.fixture(scope="function")
def simulation_with_results(
    simulation_stub, db_manager_stub, some_configuared_simulation
):
    """Фикстура, которая возвращает симуляцию с уже запущенными результатами."""
    simulation_id = some_configuared_simulation.simulations.simulation_id

    # Запускаем симуляцию
    run_request = RunSimulationRequest(simulation_id=simulation_id)
    response = simulation_stub.run_simulation(run_request)

    return response


@pytest.fixture(scope="function")
def some_configuared_simulation(simulation_stub, db_manager_stub, some_simulation_id):
    # Получаем логиста из базы данных
    from grpc_generated.simulator_pb2 import GetAllLogistsRequest

    logists_response = db_manager_stub.get_all_logists(GetAllLogistsRequest())
    assert len(logists_response.logists) > 0
    logist_id = logists_response.logists[0].worker_id

    # Устанавливаем логиста
    logist_request = SetLogistRequest(
        simulation_id=some_simulation_id, worker_id=logist_id
    )
    response = simulation_stub.set_logist(logist_request)
    assert response.simulations.simulation_id == some_simulation_id

    # Получаем поставщиков из базы данных
    suppliers_response = db_manager_stub.get_all_suppliers(GetAllSuppliersRequest())
    assert len(suppliers_response.suppliers) > 0

    # Добавляем первого поставщика
    supplier_request = AddSupplierRequest(
        simulation_id=some_simulation_id,
        supplier_id=suppliers_response.suppliers[0].supplier_id,
        is_backup=False,
    )
    response = simulation_stub.add_supplier(supplier_request)
    assert response.simulations.simulation_id == some_simulation_id

    # Добавляем второго поставщика как резервного
    if len(suppliers_response.suppliers) > 1:
        backup_supplier_request = AddSupplierRequest(
            simulation_id=some_simulation_id,
            supplier_id=suppliers_response.suppliers[1].supplier_id,
            is_backup=True,
        )
        response = simulation_stub.add_supplier(backup_supplier_request)
        assert response.simulations.simulation_id == some_simulation_id

    # Получаем рабочих из базы данных
    workers_response = db_manager_stub.get_all_workers(GetAllWorkersRequest())
    assert len(workers_response.workers) >= 2

    # Устанавливаем кладовщиков на склады
    material_worker_request = SetWarehouseInventoryWorkerRequest(
        simulation_id=some_simulation_id,
        warehouse_type=WarehouseType.WAREHOUSE_TYPE_MATERIALS,
        worker_id=workers_response.workers[0].worker_id,
    )
    response = simulation_stub.set_warehouse_inventory_worker(material_worker_request)
    assert response.simulations.simulation_id == some_simulation_id

    product_worker_request = SetWarehouseInventoryWorkerRequest(
        simulation_id=some_simulation_id,
        warehouse_type=WarehouseType.WAREHOUSE_TYPE_PRODUCTS,
        worker_id=workers_response.workers[1].worker_id,
    )
    response = simulation_stub.set_warehouse_inventory_worker(product_worker_request)
    assert response.simulations.simulation_id == some_simulation_id

    # Получаем рабочие места из базы данных
    workplaces_response = db_manager_stub.get_all_workplaces(GetAllWorkplacesRequest())
    assert len(workplaces_response.workplaces) >= 3

    # Получаем граф процесса из базы данных

    process_graph_response = db_manager_stub.get_process_graph(
        GetProcessGraphRequest(simulation_id=some_simulation_id, step=1)
    )
    assert process_graph_response.process_graph_id

    # Устанавливаем граф процесса
    process_graph_request = UpdateProcessGraphRequest(
        simulation_id=some_simulation_id,
        process_graph=process_graph_response,
    )
    response = simulation_stub.update_process_graph(process_graph_request)
    assert response.simulations.simulation_id == some_simulation_id

    # Получаем тендеры из базы данных
    tenders_response = db_manager_stub.get_all_tenders(GetAllTendersRequest())
    assert len(tenders_response.tenders) > 0

    # Получаем потребителей из базы данных
    consumers_response = db_manager_stub.get_all_consumers(GetAllConsumersRequest())
    assert len(consumers_response.consumers) > 0

    # Добавляем тендер
    tender = tenders_response.tenders[0]
    consumer = consumers_response.consumers[0]

    tender_request = AddTenderRequest(
        simulation_id=some_simulation_id,
        tender_id=tender.tender_id,
    )
    response = simulation_stub.add_tender(tender_request)
    assert response.simulations.simulation_id == some_simulation_id

    # Получаем доступные политики работы с дефектами
    defect_policies = db_manager_stub.get_available_defect_policies(
        GetAvailableDefectPoliciesRequest()
    )
    assert len(defect_policies.policies) > 0

    # Устанавливаем политику работы с дефектами
    defects_request = SetDealingWithDefectsRequest(
        simulation_id=some_simulation_id,
        dealing_with_defects=defect_policies.policies[0],
    )
    response = simulation_stub.set_dealing_with_defects(defects_request)
    assert response.simulations.simulation_id == some_simulation_id

    # Получаем LEAN улучшения из базы данных
    lean_improvements_response = db_manager_stub.get_all_lean_improvements(
        GetAllLeanImprovementsRequest()
    )
    assert len(lean_improvements_response.improvements) > 0

    # Активируем LEAN улучшения
    for lean_improvement in lean_improvements_response.improvements:
        lean_request = SetLeanImprovementStatusRequest(
            simulation_id=some_simulation_id,
            name=lean_improvement.name,
            is_implemented=True,
        )
        response = simulation_stub.set_lean_improvement_status(lean_request)
        assert response.simulations.simulation_id == some_simulation_id

    # Получаем доступные стратегии продаж
    sales_strategies = db_manager_stub.get_available_sales_strategies(
        GetAvailableSalesStrategiesRequest()
    )
    assert len(sales_strategies.strategies) > 0

    # Устанавливаем стратегию продаж
    sales_request = SetSalesStrategyRequest(
        simulation_id=some_simulation_id, strategy=sales_strategies.strategies[0]
    )
    response = simulation_stub.set_sales_strategy(sales_request)
    assert response.simulations.simulation_id == some_simulation_id

    # Получаем доступные сертификации
    certifications = db_manager_stub.get_available_certifications(
        GetAvailableCertificationsRequest()
    )
    assert len(certifications.certifications) > 0

    # Устанавливаем сертификацию
    cert_request = SetCertificationStatusRequest(
        simulation_id=some_simulation_id,
        certificate_type=certifications.certifications[0],
        is_obtained=True,
    )
    response = simulation_stub.set_certification_status(cert_request)
    assert response.simulations.simulation_id == some_simulation_id

    return response


@pytest.mark.smoke
@pytest.mark.integration
class TestSimulationServiceSmoke:
    """Тесты для базовых методов работы с симуляцией."""

    # TODO: добавить тесты для других методов

    def test_smoke(self, simulation_stub, db_manager_stub):
        """Тестsmoke."""
        request = CreateSimulationRquest()
        response = simulation_stub.create_simulation(request)
        assert response.HasField("simulations")
        assert response.simulations.simulation_id
        assert response.simulations.capital == 10000000
        assert len(response.simulations.parameters) == 1
        assert response.simulations.parameters[0].step == 1

    def test_ping(self, simulation_stub, db_manager_stub):
        """Тест ping."""
        request = PingRequest()
        response = simulation_stub.ping(request)
        assert response.success

    def test_create_simulation(self, simulation_stub, db_manager_stub):
        """Тест создания симуляции."""
        request = CreateSimulationRquest()
        response = simulation_stub.create_simulation(request)

        assert response.HasField("simulations")
        assert response.simulations.simulation_id
        assert len(response.simulations.parameters) == 1
        assert response.simulations.parameters[0].step == 1

    def test_get_simulation(self, simulation_stub, db_manager_stub, some_simulation_id):
        """Тест получения симуляции."""
        request = GetSimulationRequest(simulation_id=some_simulation_id)
        response = simulation_stub.get_simulation(request)
        assert response.HasField("simulations")
        assert response.simulations.simulation_id
        assert len(response.simulations.parameters) == 1
        assert response.simulations.parameters[0].step == 1

    def test_run_simulation(
        self, simulation_stub, db_manager_stub, some_configuared_simulation
    ):
        """Тест запуска симуляции."""
        simulation_id = some_configuared_simulation.simulations.simulation_id
        request = RunSimulationRequest(simulation_id=simulation_id)
        response = simulation_stub.run_simulation(request)
        assert response.simulations.simulation_id == simulation_id
        assert len(response.simulations.results) > 0

    def test_set_worker_on_workplace(
        self, simulation_stub, db_manager_stub, some_configuared_simulation
    ):
        """Тест установки работника на рабочее место."""
        simulation_id = some_configuared_simulation.simulations.simulation_id

        # Получаем рабочего и рабочее место из базы
        workers_response = db_manager_stub.get_all_workers(GetAllWorkersRequest())
        workplaces_response = db_manager_stub.get_all_workplaces(
            GetAllWorkplacesRequest()
        )

        request = SetWorkerOnWorkerplaceRequest(
            simulation_id=simulation_id,
            workplace_id=workplaces_response.workplaces[0].workplace_id,
            worker_id=workers_response.workers[0].worker_id,
        )
        response = simulation_stub.set_worker_on_workerplace(request)
        assert response.simulations.simulation_id == simulation_id

    def test_unset_worker_on_workplace(
        self, simulation_stub, db_manager_stub, some_configuared_simulation
    ):
        """Тест снятия работника с рабочего места."""
        simulation_id = some_configuared_simulation.simulations.simulation_id

        # Сначала устанавливаем работника на рабочее место
        workers_response = db_manager_stub.get_all_workers(GetAllWorkersRequest())
        workplaces_response = db_manager_stub.get_all_workplaces(
            GetAllWorkplacesRequest()
        )

        set_request = SetWorkerOnWorkerplaceRequest(
            simulation_id=simulation_id,
            workplace_id=workplaces_response.workplaces[0].workplace_id,
            worker_id=workers_response.workers[0].worker_id,
        )
        simulation_stub.set_worker_on_workerplace(set_request)

        # Теперь снимаем работника
        unset_request = UnSetWorkerOnWorkerplaceRequest(
            simulation_id=simulation_id,
            worker_id=workers_response.workers[0].worker_id,
        )
        response = simulation_stub.unset_worker_on_workerplace(unset_request)
        assert response.simulations.simulation_id == simulation_id

    def test_delete_supplier(
        self, simulation_stub, db_manager_stub, simulation_with_results
    ):
        """Тест удаления поставщика."""
        simulation_id = simulation_with_results.simulations.simulation_id

        # Получаем поставщика из базы
        suppliers_response = db_manager_stub.get_all_suppliers(GetAllSuppliersRequest())

        request = DeleteSupplierRequest(
            simulation_id=simulation_id,
            supplier_id=suppliers_response.suppliers[0].supplier_id,
        )
        response = simulation_stub.delete_supplier(request)
        assert response.simulations.simulation_id == simulation_id

    def test_increase_warehouse_size(
        self, simulation_stub, db_manager_stub, simulation_with_results
    ):
        """Тест увеличения размера склада."""
        simulation_id = simulation_with_results.simulations.simulation_id

        request = IncreaseWarehouseSizeRequest(
            simulation_id=simulation_id,
            warehouse_type=WarehouseType.WAREHOUSE_TYPE_MATERIALS,
            size=500,
        )
        response = simulation_stub.increase_warehouse_size(request)
        assert response.simulations.simulation_id == simulation_id

    def test_set_production_plan_row(
        self, simulation_stub, db_manager_stub, simulation_with_results
    ):
        """Тест установки строки производственного плана."""
        simulation_id = simulation_with_results.simulations.simulation_id

        # Получаем тендер из базы
        tenders_response = db_manager_stub.get_all_tenders(GetAllTendersRequest())

        # Создаем ProductionPlanRow объект
        production_plan_row = ProductionPlanRow(
            tender_id=tenders_response.tenders[0].tender_id,
            planned_quantity=50,
        )

        request = SetProductionPlanRowRequest(
            simulation_id=simulation_id,
            row=production_plan_row,
        )
        response = simulation_stub.set_production_plan_row(request)
        assert response.simulations.simulation_id == simulation_id

    def test_delete_tender(
        self, simulation_stub, db_manager_stub, simulation_with_results
    ):
        """Тест удаления тендера."""
        simulation_id = simulation_with_results.simulations.simulation_id

        # Получаем тендер из базы
        tenders_response = db_manager_stub.get_all_tenders(GetAllTendersRequest())

        request = RemoveTenderRequest(
            simulation_id=simulation_id,
            tender_id=tenders_response.tenders[0].tender_id,
        )
        response = simulation_stub.delete_tender(request)
        assert response.simulations.simulation_id == simulation_id

    def test_set_quality_inspection(
        self, simulation_stub, db_manager_stub, simulation_with_results
    ):
        """Тест установки контроля качества."""
        simulation_id = simulation_with_results.simulations.simulation_id

        # Получаем поставщика из базы
        suppliers_response = db_manager_stub.get_all_suppliers(GetAllSuppliersRequest())

        request = SetQualityInspectionRequest(
            simulation_id=simulation_id,
            supplier_id=suppliers_response.suppliers[0].supplier_id,
            inspection_enabled=True,
        )
        response = simulation_stub.set_quality_inspection(request)
        assert response.simulations.simulation_id == simulation_id

    def test_set_delivery_period(
        self, simulation_stub, db_manager_stub, simulation_with_results
    ):
        """Тест установки периода поставок."""
        simulation_id = simulation_with_results.simulations.simulation_id

        # Получаем поставщика из базы
        suppliers_response = db_manager_stub.get_all_suppliers(GetAllSuppliersRequest())

        request = SetDeliveryPeriodRequest(
            simulation_id=simulation_id,
            supplier_id=suppliers_response.suppliers[0].supplier_id,
            delivery_period_days=14,
        )
        response = simulation_stub.set_delivery_period(request)
        assert response.simulations.simulation_id == simulation_id

    def test_set_equipment_maintenance_interval(
        self, simulation_stub, db_manager_stub, some_configuared_simulation
    ):
        """Тест установки интервала обслуживания оборудования через ProcessGraph."""
        simulation_id = some_configuared_simulation.simulations.simulation_id

        # Получаем текущий ProcessGraph
        process_graph_response = db_manager_stub.get_process_graph(
            GetProcessGraphRequest(simulation_id=simulation_id, step=1)
        )

        # Модифицируем интервал обслуживания первого оборудования
        workplace = process_graph_response.workplaces[0]
        if workplace.equipment:
            workplace.equipment.maintenance_period = 45

            # Обновляем ProcessGraph
            process_graph_request = UpdateProcessGraphRequest(
                simulation_id=simulation_id,
                process_graph=process_graph_response,
            )
            response = simulation_stub.update_process_graph(process_graph_request)
            assert response.simulations.simulation_id == simulation_id

    def test_get_factory_metrics(
        self, simulation_stub, db_manager_stub, simulation_with_results
    ):
        """Тест получения метрик завода."""
        simulation_id = simulation_with_results.simulations.simulation_id

        request = GetMetricsRequest(simulation_id=simulation_id, step=1)
        response = simulation_stub.get_factory_metrics(request)
        assert hasattr(response, "metrics")

    def test_get_production_metrics(
        self, simulation_stub, db_manager_stub, simulation_with_results
    ):
        """Тест получения метрик производства."""
        simulation_id = simulation_with_results.simulations.simulation_id

        request = GetMetricsRequest(simulation_id=simulation_id, step=1)
        response = simulation_stub.get_production_metrics(request)
        assert hasattr(response, "metrics")

    def test_get_quality_metrics(
        self, simulation_stub, db_manager_stub, simulation_with_results
    ):
        """Тест получения метрик качества."""
        simulation_id = simulation_with_results.simulations.simulation_id

        request = GetMetricsRequest(simulation_id=simulation_id, step=1)
        response = simulation_stub.get_quality_metrics(request)
        assert hasattr(response, "metrics")

    def test_get_engineering_metrics(
        self, simulation_stub, db_manager_stub, simulation_with_results
    ):
        """Тест получения инженерных метрик."""
        simulation_id = simulation_with_results.simulations.simulation_id

        request = GetMetricsRequest(simulation_id=simulation_id, step=1)
        response = simulation_stub.get_engineering_metrics(request)
        assert hasattr(response, "metrics")

    def test_get_commercial_metrics(
        self, simulation_stub, db_manager_stub, simulation_with_results
    ):
        """Тест получения коммерческих метрик."""
        simulation_id = simulation_with_results.simulations.simulation_id

        request = GetMetricsRequest(simulation_id=simulation_id, step=1)
        response = simulation_stub.get_commercial_metrics(request)
        assert hasattr(response, "metrics")

    def test_get_procurement_metrics(
        self, simulation_stub, db_manager_stub, simulation_with_results
    ):
        """Тест получения метрик закупок."""
        simulation_id = simulation_with_results.simulations.simulation_id

        request = GetMetricsRequest(simulation_id=simulation_id, step=1)
        response = simulation_stub.get_procurement_metrics(request)
        assert hasattr(response, "metrics")

    def test_get_all_metrics(
        self, simulation_stub, db_manager_stub, simulation_with_results
    ):
        """Тест получения всех метрик."""
        simulation_id = simulation_with_results.simulations.simulation_id

        request = GetAllMetricsRequest(simulation_id=simulation_id, step=1)
        response = simulation_stub.get_all_metrics(request)
        assert (
            hasattr(response, "factory")
            and hasattr(response, "production")
            and hasattr(response, "quality")
        )

    def test_get_production_schedule(
        self, simulation_stub, db_manager_stub, simulation_with_results
    ):
        """Тест получения производственного плана."""
        simulation_id = simulation_with_results.simulations.simulation_id

        request = GetProductionScheduleRequest(simulation_id=simulation_id)
        response = simulation_stub.get_production_schedule(request)
        assert hasattr(response, "schedule")

    def test_get_workshop_plan(
        self, simulation_stub, db_manager_stub, simulation_with_results
    ):
        """Тест получения плана цеха."""
        simulation_id = simulation_with_results.simulations.simulation_id

        request = GetWorkshopPlanRequest(simulation_id=simulation_id)
        response = simulation_stub.get_workshop_plan(request)
        assert hasattr(response, "workshop_plan")

    def test_get_unplanned_repair(
        self, simulation_stub, db_manager_stub, simulation_with_results
    ):
        """Тест получения информации о внеплановых ремонтах."""
        simulation_id = simulation_with_results.simulations.simulation_id

        request = GetUnplannedRepairRequest(simulation_id=simulation_id)
        response = simulation_stub.get_unplanned_repair(request)
        assert hasattr(response, "unplanned_repair")

    def test_get_warehouse_load_chart(
        self, simulation_stub, db_manager_stub, simulation_with_results
    ):
        """Тест получения графика загрузки склада."""
        simulation_id = simulation_with_results.simulations.simulation_id

        request = GetWarehouseLoadChartRequest(
            simulation_id=simulation_id, warehouse_id="materials"
        )
        response = simulation_stub.get_warehouse_load_chart(request)
        assert hasattr(response, "chart")

    def test_get_required_materials(
        self, simulation_stub, db_manager_stub, simulation_with_results
    ):
        """Тест получения списка требуемых материалов."""
        simulation_id = simulation_with_results.simulations.simulation_id

        request = GetRequiredMaterialsRequest(simulation_id=simulation_id)
        response = simulation_stub.get_required_materials(request)
        assert hasattr(response, "materials")

    def test_get_available_improvements(
        self, simulation_stub, db_manager_stub, simulation_with_results
    ):
        """Тест получения доступных улучшений."""
        simulation_id = simulation_with_results.simulations.simulation_id

        request = GetAvailableImprovementsRequest(simulation_id=simulation_id)
        response = simulation_stub.get_available_improvements(request)
        assert hasattr(response, "improvements")

    def test_get_defect_policies(
        self, simulation_stub, db_manager_stub, simulation_with_results
    ):
        """Тест получения политик работы с дефектами."""
        simulation_id = simulation_with_results.simulations.simulation_id

        request = GetDefectPoliciesRequest(simulation_id=simulation_id)
        response = simulation_stub.get_defect_policies(request)
        assert hasattr(response, "available_policies") and hasattr(
            response, "current_policy"
        )

    def test_get_material_types(self, simulation_stub, db_manager_stub):
        """Тест получения типов материалов."""
        request = GetMaterialTypesRequest()
        response = simulation_stub.get_material_types(request)
        assert hasattr(response, "material_types")

    def test_get_equipment_types(self, simulation_stub, db_manager_stub):
        """Тест получения типов оборудования."""
        request = GetEquipmentTypesRequest()
        response = simulation_stub.get_equipment_types(request)
        assert hasattr(response, "equipment_types")

    def test_get_workplace_types(self, simulation_stub, db_manager_stub):
        """Тест получения типов рабочих мест."""
        request = GetWorkplaceTypesRequest()
        response = simulation_stub.get_workplace_types(request)
        assert hasattr(response, "workplace_types")

    def test_get_available_improvements_list(self, simulation_stub, db_manager_stub):
        """Тест получения списка доступных улучшений."""
        request = GetAvailableImprovementsListRequest()
        response = simulation_stub.get_available_improvements_list(request)
        assert hasattr(response, "improvements")

    def test_validate_configuration(
        self, simulation_stub, db_manager_stub, simulation_with_results
    ):
        """Тест валидации конфигурации."""
        simulation_id = simulation_with_results.simulations.simulation_id

        request = ValidateConfigurationRequest(simulation_id=simulation_id)
        response = simulation_stub.validate_configuration(request)
        assert hasattr(response, "is_valid")

    def test_configure_simulation(
        self, simulation_stub, db_manager_stub, some_configuared_simulation
    ):
        assert some_configuared_simulation.simulations.simulation_id
        assert len(some_configuared_simulation.simulations.parameters) == 1
        assert some_configuared_simulation.simulations.parameters[0].step == 1
