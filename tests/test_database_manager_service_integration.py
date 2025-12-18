"""
Интеграционные тесты для SimulationDatabaseManager сервиса.

Тесты проверяют все методы сервиса через gRPC, используя реальную базу данных
в Docker контейнере.
"""

import pytest
import uuid

from grpc_generated.simulator_pb2 import (
    # Supplier
    CreateSimulationRquest,
    CreateSupplierRequest,
    UpdateSupplierRequest,
    DeleteSupplierRequest,
    GetAllSuppliersRequest,
    # Warehouse
    GetWarehouseRequest,
    # Worker
    CreateWorkerRequest,
    UpdateWorkerRequest,
    DeleteWorkerRequest,
    GetAllWorkersRequest,
    # Logist
    CreateLogistRequest,
    UpdateLogistRequest,
    DeleteLogistRequest,
    GetAllLogistsRequest,
    # Workplace
    CreateWorkplaceRequest,
    UpdateWorkplaceRequest,
    DeleteWorkplaceRequest,
    GetAllWorkplacesRequest,
    # Process Graph
    GetProcessGraphRequest,
    # Consumer
    CreateConsumerRequest,
    UpdateConsumerRequest,
    DeleteConsumerRequest,
    GetAllConsumersRequest,
    # Tender
    CreateTenderRequest,
    UpdateTenderRequest,
    DeleteTenderRequest,
    GetAllTendersRequest,
    # Equipment
    CreateEquipmentRequest,
    UpdateEquipmentRequest,
    DeleteEquipmentRequest,
    GetAllEquipmentRequest,
    # Lean Improvement
    CreateLeanImprovementRequest,
    UpdateLeanImprovementRequest,
    DeleteLeanImprovementRequest,
    GetAllLeanImprovementsRequest,
    # Reference Data
    GetMaterialTypesRequest,
    GetEquipmentTypesRequest,
    GetWorkplaceTypesRequest,
    GetAvailableDefectPoliciesRequest,
    GetAvailableImprovementsListRequest,
    GetAvailableCertificationsRequest,
    GetAvailableSalesStrategiesRequest,
    GetAvailableLeanImprovementsRequest,
    # Ping
    PingRequest,
)
from domain import (
    Qualification,
    ConsumerType,
    Specialization,
    VehicleType,
    PaymentForm,
)


@pytest.fixture(scope="function")
def some_simulation(simulation_stub):
    request = CreateSimulationRquest()
    response = simulation_stub.create_simulation(request)
    return response


@pytest.fixture(scope="function")
def some_simulation_id(some_simulation):
    return some_simulation.simulations.simulation_id


class TestSupplierMethods:
    """Тесты для методов работы с поставщиками."""

    def test_create_supplier(self, db_manager_stub):
        """Тест создания поставщика."""
        request = CreateSupplierRequest(
            name="Test Supplier",
            product_name="Test Product",
            material_type="Metal",
            delivery_period=30,
            special_delivery_period=15,
            reliability=0.95,
            product_quality=0.90,
            cost=1000,
            special_delivery_cost=1500,
        )

        response = db_manager_stub.create_supplier(request)

        assert response.supplier_id
        assert response.name == "Test Supplier"
        assert response.product_name == "Test Product"
        assert response.cost == 1000

    def test_update_supplier(self, db_manager_stub):
        """Тест обновления поставщика."""
        # Создаем поставщика
        create_request = CreateSupplierRequest(
            name="Original Supplier",
            product_name="Original Product",
            material_type="Metal",
            delivery_period=30,
            reliability=0.95,
            product_quality=0.90,
            cost=1000,
        )
        created = db_manager_stub.create_supplier(create_request)

        # Обновляем
        update_request = UpdateSupplierRequest(
            supplier_id=created.supplier_id,
            name="Updated Supplier",
            cost=2000,
        )

        response = db_manager_stub.update_supplier(update_request)

        assert response.supplier_id == created.supplier_id
        assert response.name == "Updated Supplier"
        assert response.cost == 2000

    def test_delete_supplier(self, db_manager_stub):
        """Тест удаления поставщика."""
        # Создаем поставщика
        create_request = CreateSupplierRequest(
            name="To Delete",
            product_name="Product",
            material_type="Metal",
            delivery_period=30,
            reliability=0.95,
            product_quality=0.90,
            cost=1000,
        )
        created = db_manager_stub.create_supplier(create_request)

        # Удаляем
        delete_request = DeleteSupplierRequest(supplier_id=created.supplier_id)
        response = db_manager_stub.delete_supplier(delete_request)

        assert response.success is True

    def test_get_all_suppliers(self, db_manager_stub):
        """Тест получения всех поставщиков."""
        # Создаем несколько поставщиков
        for i in range(3):
            create_request = CreateSupplierRequest(
                name=f"Supplier {i}",
                product_name=f"Product {i}",
                material_type="Metal",
                delivery_period=30,
                reliability=0.95,
                product_quality=0.90,
                cost=1000 + i,
            )
            db_manager_stub.create_supplier(create_request)

        # Получаем всех
        request = GetAllSuppliersRequest()
        response = db_manager_stub.get_all_suppliers(request)

        assert response.total_count >= 3
        assert len(response.suppliers) >= 3


class TestWarehouseMethods:
    """Тесты для методов работы со складом."""

    def test_get_warehouse(self, db_manager_stub):
        """Тест получения информации о складе."""
        request = GetWarehouseRequest(warehouse_id="test_warehouse")
        response = db_manager_stub.get_warehouse(request)

        assert response.warehouse_id == "test_warehouse"
        assert response.size > 0


class TestWorkerMethods:
    """Тесты для методов работы с рабочими."""

    def test_create_worker(self, db_manager_stub):
        """Тест создания рабочего."""
        request = CreateWorkerRequest(
            name="Test Worker",
            qualification=Qualification.III.value,  # int в proto
            specialty=Specialization.ASSEMBLER.value,  # string в proto
            salary=50000,
        )

        response = db_manager_stub.create_worker(request)

        assert response.worker_id
        assert response.name == "Test Worker"
        assert response.qualification == Qualification.III.value  # int в proto
        assert response.salary == 50000

    def test_update_worker(self, db_manager_stub):
        """Тест обновления рабочего."""
        # Создаем рабочего
        create_request = CreateWorkerRequest(
            name="Original Worker",
            qualification=Qualification.III.value,  # int в proto
            specialty=Specialization.ASSEMBLER.value,  # string в proto
            salary=50000,
        )
        created = db_manager_stub.create_worker(create_request)

        # Обновляем
        update_request = UpdateWorkerRequest(
            worker_id=created.worker_id,
            name="Updated Worker",
            salary=60000,
        )

        response = db_manager_stub.update_worker(update_request)

        assert response.worker_id == created.worker_id
        assert response.name == "Updated Worker"
        assert response.salary == 60000

    def test_delete_worker(self, db_manager_stub):
        """Тест удаления рабочего."""
        # Создаем рабочего
        create_request = CreateWorkerRequest(
            name="To Delete",
            qualification=Qualification.III.value,  # int в proto
            specialty=Specialization.ASSEMBLER.value,  # string в proto
            salary=50000,
        )
        created = db_manager_stub.create_worker(create_request)

        # Удаляем
        delete_request = DeleteWorkerRequest(worker_id=created.worker_id)
        response = db_manager_stub.delete_worker(delete_request)

        assert response.success is True

    def test_get_all_workers(self, db_manager_stub):
        """Тест получения всех рабочих."""
        # Создаем несколько рабочих
        for i in range(3):
            create_request = CreateWorkerRequest(
                name=f"Worker {i}",
                qualification=Qualification.III.value,  # int в proto
                specialty=Specialization.ASSEMBLER.value,  # string в proto
                salary=50000 + i * 1000,
            )
            db_manager_stub.create_worker(create_request)

        # Получаем всех
        request = GetAllWorkersRequest()
        response = db_manager_stub.get_all_workers(request)

        assert response.total_count >= 3
        assert len(response.workers) >= 3


class TestLogistMethods:
    """Тесты для методов работы с логистами."""

    def test_create_logist(self, db_manager_stub):
        """Тест создания логиста."""
        request = CreateLogistRequest(
            name="Test Logist",
            qualification=Qualification.III.value,  # int в proto
            specialty=Specialization.LOGIST.value,  # string в proto
            salary=60000,
            speed=50,
            vehicle_type=VehicleType.TRUCK.value,
        )

        response = db_manager_stub.create_logist(request)

        assert response.worker_id
        assert response.name == "Test Logist"
        assert response.speed == 50
        assert response.vehicle_type == VehicleType.TRUCK.value

    def test_update_logist(self, db_manager_stub):
        """Тест обновления логиста."""
        # Создаем логиста
        create_request = CreateLogistRequest(
            name="Original Logist",
            qualification=Qualification.III.value,  # int в proto
            specialty=Specialization.LOGIST.value,  # string в proto
            salary=60000,
            speed=50,
            vehicle_type=VehicleType.TRUCK.value,
        )
        created = db_manager_stub.create_logist(create_request)

        # Проверяем что логист создан
        assert (
            created.worker_id
        ), f"Логист не создан, получен worker_id: {created.worker_id}"

        # Обновляем
        update_request = UpdateLogistRequest(
            worker_id=created.worker_id,
            name="Updated Logist",
            speed=60,
        )

        response = db_manager_stub.update_logist(update_request)

        assert response.worker_id == created.worker_id
        assert response.name == "Updated Logist"
        assert response.speed == 60

    def test_delete_logist(self, db_manager_stub):
        """Тест удаления логиста."""
        # Создаем логиста
        create_request = CreateLogistRequest(
            name="To Delete",
            qualification=Qualification.III.value,  # int в proto
            specialty=Specialization.LOGIST.value,  # string в proto
            salary=60000,
            speed=50,
            vehicle_type=VehicleType.TRUCK.value,
        )
        created = db_manager_stub.create_logist(create_request)

        # Проверяем что логист создан
        assert (
            created.worker_id
        ), f"Логист не создан, получен worker_id: {created.worker_id}"

        # Удаляем
        delete_request = DeleteLogistRequest(worker_id=created.worker_id)
        response = db_manager_stub.delete_logist(delete_request)

        assert response.success is True, f"Удаление не удалось: {response.message}"

    def test_get_all_logists(self, db_manager_stub):
        """Тест получения всех логистов."""
        # Создаем несколько логистов
        for i in range(3):
            create_request = CreateLogistRequest(
                name=f"Logist {i}",
                qualification=Qualification.III.value,  # int в proto
                specialty=Specialization.LOGIST.value,  # string в proto
                salary=60000 + i * 1000,
                speed=50 + i,
                vehicle_type=VehicleType.TRUCK.value,
            )
            db_manager_stub.create_logist(create_request)

        # Получаем всех
        request = GetAllLogistsRequest()
        response = db_manager_stub.get_all_logists(request)

        assert response.total_count >= 3
        assert len(response.logists) >= 3


class TestWorkplaceMethods:
    """Тесты для методов работы с рабочими местами."""

    def test_create_workplace(self, db_manager_stub):
        """Тест создания рабочего места."""
        request = CreateWorkplaceRequest(
            workplace_name="Test Workplace",
            required_speciality=Specialization.ASSEMBLER.value,
            required_qualification=Qualification.III.value,  # int в proto
            required_equipment="Equipment Type",
            required_stages=["Stage 1", "Stage 2"],
        )

        response = db_manager_stub.create_workplace(request)

        assert response.workplace_id
        assert response.workplace_name == "Test Workplace"
        assert len(response.required_stages) == 2

    def test_update_workplace(self, db_manager_stub):
        """Тест обновления рабочего места."""
        # Создаем рабочее место
        create_request = CreateWorkplaceRequest(
            workplace_name="Original Workplace",
            required_speciality=Specialization.ASSEMBLER.value,
            required_qualification=Qualification.III.value,  # int в proto
            required_stages=["Stage 1"],
        )
        created = db_manager_stub.create_workplace(create_request)

        # Обновляем
        update_request = UpdateWorkplaceRequest(
            workplace_id=created.workplace_id,
            workplace_name="Updated Workplace",
            required_stages=["Stage 1", "Stage 2", "Stage 3"],
        )

        response = db_manager_stub.update_workplace(update_request)

        assert response.workplace_id == created.workplace_id
        assert response.workplace_name == "Updated Workplace"
        assert len(response.required_stages) == 3

    def test_delete_workplace(self, db_manager_stub):
        """Тест удаления рабочего места."""
        # Создаем рабочее место
        create_request = CreateWorkplaceRequest(
            workplace_name="To Delete",
            required_speciality=Specialization.ASSEMBLER.value,
            required_qualification=Qualification.III.value,  # int в proto
        )
        created = db_manager_stub.create_workplace(create_request)

        # Удаляем
        delete_request = DeleteWorkplaceRequest(workplace_id=created.workplace_id)
        response = db_manager_stub.delete_workplace(delete_request)

        assert response.success is True

    def test_get_all_workplaces(self, db_manager_stub):
        """Тест получения всех рабочих мест."""
        # Создаем несколько рабочих мест
        for i in range(3):
            create_request = CreateWorkplaceRequest(
                workplace_name=f"Workplace {i}",
                required_speciality=Specialization.ASSEMBLER.value,
                required_qualification=Qualification.III.value,  # int в proto
            )
            db_manager_stub.create_workplace(create_request)

        # Получаем все
        request = GetAllWorkplacesRequest()
        response = db_manager_stub.get_all_workplaces(request)

        assert response.total_count >= 3
        assert len(response.workplaces) >= 3


class TestProcessGraphMethods:
    """Тесты для методов работы с графом процесса."""

    def test_get_process_graph(self, db_manager_stub, some_simulation_id):
        """Тест получения графа процесса."""
        request = GetProcessGraphRequest(simulation_id=some_simulation_id, step=1)
        response = db_manager_stub.get_process_graph(request)

        assert response.process_graph_id


class TestConsumerMethods:
    """Тесты для методов работы с заказчиками."""

    def test_create_consumer(self, db_manager_stub):
        """Тест создания заказчика."""
        request = CreateConsumerRequest(
            name="Test Consumer",
            type=ConsumerType.NOT_GOVERMANT.value,
        )

        response = db_manager_stub.create_consumer(request)

        assert response.consumer_id
        assert response.name == "Test Consumer"
        assert response.type == ConsumerType.NOT_GOVERMANT.value

    def test_update_consumer(self, db_manager_stub):
        """Тест обновления заказчика."""
        # Создаем заказчика
        create_request = CreateConsumerRequest(
            name="Original Consumer",
            type=ConsumerType.NOT_GOVERMANT.value,
        )
        created = db_manager_stub.create_consumer(create_request)

        # Обновляем
        update_request = UpdateConsumerRequest(
            consumer_id=created.consumer_id,
            name="Updated Consumer",
        )

        response = db_manager_stub.update_consumer(update_request)

        assert response.consumer_id == created.consumer_id
        assert response.name == "Updated Consumer"

    def test_delete_consumer(self, db_manager_stub):
        """Тест удаления заказчика."""
        # Создаем заказчика
        create_request = CreateConsumerRequest(
            name="To Delete",
            type=ConsumerType.NOT_GOVERMANT.value,
        )
        created = db_manager_stub.create_consumer(create_request)

        # Удаляем
        delete_request = DeleteConsumerRequest(consumer_id=created.consumer_id)
        response = db_manager_stub.delete_consumer(delete_request)

        assert response.success is True

    def test_get_all_consumers(self, db_manager_stub):
        """Тест получения всех заказчиков."""
        # Создаем несколько заказчиков
        for i in range(3):
            create_request = CreateConsumerRequest(
                name=f"Consumer {i}",
                type=ConsumerType.NOT_GOVERMANT.value,
            )
            db_manager_stub.create_consumer(create_request)

        # Получаем всех
        request = GetAllConsumersRequest()
        response = db_manager_stub.get_all_consumers(request)

        assert response.total_count >= 3
        assert len(response.consumers) >= 3


class TestTenderMethods:
    """Тесты для методов работы с тендерами."""

    def test_create_tender(self, db_manager_stub):
        """Тест создания тендера."""
        # Сначала создаем заказчика
        consumer_request = CreateConsumerRequest(
            name="Tender Consumer",
            type=ConsumerType.NOT_GOVERMANT.value,
        )
        consumer = db_manager_stub.create_consumer(consumer_request)

        request = CreateTenderRequest(
            consumer_id=consumer.consumer_id,
            cost=100000,
            quantity_of_products=100,
            penalty_per_day=1000,
            warranty_years=2,
            payment_form=PaymentForm.FULL_ADVANCE.value,
        )

        response = db_manager_stub.create_tender(request)

        assert response.tender_id
        assert response.cost == 100000
        assert response.quantity_of_products == 100

    def test_update_tender(self, db_manager_stub):
        """Тест обновления тендера."""
        # Создаем заказчика и тендер
        consumer_request = CreateConsumerRequest(
            name="Tender Consumer",
            type=ConsumerType.NOT_GOVERMANT.value,
        )
        consumer = db_manager_stub.create_consumer(consumer_request)

        create_request = CreateTenderRequest(
            consumer_id=consumer.consumer_id,
            cost=100000,
            quantity_of_products=100,
        )
        created = db_manager_stub.create_tender(create_request)

        # Обновляем
        update_request = UpdateTenderRequest(
            tender_id=created.tender_id,
            cost=200000,
            quantity_of_products=200,
        )

        response = db_manager_stub.update_tender(update_request)

        assert response.tender_id == created.tender_id
        assert response.cost == 200000
        assert response.quantity_of_products == 200

    def test_delete_tender(self, db_manager_stub):
        """Тест удаления тендера."""
        # Создаем заказчика и тендер
        consumer_request = CreateConsumerRequest(
            name="Tender Consumer",
            type=ConsumerType.NOT_GOVERMANT.value,
        )
        consumer = db_manager_stub.create_consumer(consumer_request)

        create_request = CreateTenderRequest(
            consumer_id=consumer.consumer_id,
            cost=100000,
            quantity_of_products=100,
        )
        created = db_manager_stub.create_tender(create_request)

        # Удаляем
        delete_request = DeleteTenderRequest(tender_id=created.tender_id)
        response = db_manager_stub.delete_tender(delete_request)

        assert response.success is True

    def test_get_all_tenders(self, db_manager_stub):
        """Тест получения всех тендеров."""
        # Создаем заказчика
        consumer_request = CreateConsumerRequest(
            name="Tender Consumer",
            type=ConsumerType.NOT_GOVERMANT.value,
        )
        consumer = db_manager_stub.create_consumer(consumer_request)

        # Создаем несколько тендеров
        for i in range(3):
            create_request = CreateTenderRequest(
                consumer_id=consumer.consumer_id,
                cost=100000 + i * 10000,
                quantity_of_products=100 + i * 10,
            )
            db_manager_stub.create_tender(create_request)

        # Получаем все
        request = GetAllTendersRequest()
        response = db_manager_stub.get_all_tenders(request)

        assert response.total_count >= 3
        assert len(response.tenders) >= 3


class TestEquipmentMethods:
    """Тесты для методов работы с оборудованием."""

    def test_create_equipment(self, db_manager_stub):
        """Тест создания оборудования."""
        request = CreateEquipmentRequest(
            name="Test Equipment",
            equipment_type="Machine",
            reliability=0.95,
            maintenance_period=30,
            maintenance_cost=5000,
            cost=50000,
            repair_cost=10000,
            repair_time=24,
        )

        response = db_manager_stub.create_equipment(request)

        assert response.equipment_id
        assert response.name == "Test Equipment"
        assert response.cost == 50000

    def test_update_equipment(self, db_manager_stub):
        """Тест обновления оборудования."""
        # Создаем оборудование
        create_request = CreateEquipmentRequest(
            name="Original Equipment",
            equipment_type="Machine",
            reliability=0.95,
            cost=50000,
        )
        created = db_manager_stub.create_equipment(create_request)

        # Обновляем
        update_request = UpdateEquipmentRequest(
            equipment_id=created.equipment_id,
            name="Updated Equipment",
            cost=60000,
        )

        response = db_manager_stub.update_equipment(update_request)

        assert response.equipment_id == created.equipment_id
        assert response.name == "Updated Equipment"
        assert response.cost == 60000

    def test_delete_equipment(self, db_manager_stub):
        """Тест удаления оборудования."""
        # Создаем оборудование
        create_request = CreateEquipmentRequest(
            name="To Delete",
            equipment_type="Machine",
            reliability=0.95,
            cost=50000,
        )
        created = db_manager_stub.create_equipment(create_request)

        # Удаляем
        delete_request = DeleteEquipmentRequest(equipment_id=created.equipment_id)
        response = db_manager_stub.delete_equipment(delete_request)

        assert response.success is True

    def test_get_all_equipment(self, db_manager_stub):
        """Тест получения всего оборудования."""
        # Создаем несколько единиц оборудования
        for i in range(3):
            create_request = CreateEquipmentRequest(
                name=f"Equipment {i}",
                equipment_type="Machine",
                reliability=0.95,
                cost=50000 + i * 1000,
            )
            db_manager_stub.create_equipment(create_request)

        # Получаем все
        request = GetAllEquipmentRequest()
        response = db_manager_stub.get_all_equipment(request)

        assert response.total_count >= 3
        assert len(response.equipments) >= 3


class TestLeanImprovementMethods:
    """Тесты для методов работы с LEAN улучшениями."""

    def test_create_lean_improvement(self, db_manager_stub):
        """Тест создания LEAN улучшения."""
        request = CreateLeanImprovementRequest(
            name="Test Improvement",
            is_implemented=False,
            implementation_cost=10000,
            efficiency_gain=0.15,
        )

        response = db_manager_stub.create_lean_improvement(request)

        assert response.improvement_id
        assert response.name == "Test Improvement"
        assert response.efficiency_gain == 0.15

    def test_update_lean_improvement(self, db_manager_stub):
        """Тест обновления LEAN улучшения."""
        # Создаем улучшение
        create_request = CreateLeanImprovementRequest(
            name="Original Improvement",
            is_implemented=False,
            implementation_cost=10000,
            efficiency_gain=0.15,
        )
        created = db_manager_stub.create_lean_improvement(create_request)

        # Обновляем
        update_request = UpdateLeanImprovementRequest(
            improvement_id=created.improvement_id,
            name="Updated Improvement",
            is_implemented=True,
            efficiency_gain=0.20,
        )

        response = db_manager_stub.update_lean_improvement(update_request)

        assert response.improvement_id == created.improvement_id
        assert response.name == "Updated Improvement"
        assert response.is_implemented is True
        assert response.efficiency_gain == 0.20

    def test_delete_lean_improvement(self, db_manager_stub):
        """Тест удаления LEAN улучшения."""
        # Создаем улучшение
        create_request = CreateLeanImprovementRequest(
            name="To Delete",
            is_implemented=False,
            implementation_cost=10000,
            efficiency_gain=0.15,
        )
        created = db_manager_stub.create_lean_improvement(create_request)

        # Удаляем
        delete_request = DeleteLeanImprovementRequest(
            improvement_id=created.improvement_id
        )
        response = db_manager_stub.delete_lean_improvement(delete_request)

        assert response.success is True

    def test_get_all_lean_improvements(self, db_manager_stub):
        """Тест получения всех LEAN улучшений."""
        # Создаем несколько улучшений
        for i in range(3):
            create_request = CreateLeanImprovementRequest(
                name=f"Improvement {i}",
                is_implemented=False,
                implementation_cost=10000 + i * 1000,
                efficiency_gain=0.15 + i * 0.01,
            )
            db_manager_stub.create_lean_improvement(create_request)

        # Получаем все
        request = GetAllLeanImprovementsRequest()
        response = db_manager_stub.get_all_lean_improvements(request)

        assert response.total_count >= 3
        assert len(response.improvements) >= 3


class TestReferenceDataMethods:
    """Тесты для методов работы со справочными данными."""

    # Примечание: GetReferenceDataRequest больше не существует в proto
    # Используйте отдельные методы для получения справочных данных (см. ниже)

    def test_get_available_material_types(self, db_manager_stub):
        """Тест получения типов материалов."""
        request = GetMaterialTypesRequest()
        response = db_manager_stub.get_available_material_types(request)

        assert response.timestamp

    def test_get_available_equipment_types(self, db_manager_stub):
        """Тест получения типов оборудования."""
        request = GetEquipmentTypesRequest()
        response = db_manager_stub.get_available_equipment_types(request)

        assert response.timestamp

    def test_get_available_workplace_types(self, db_manager_stub):
        """Тест получения типов рабочих мест."""
        request = GetWorkplaceTypesRequest()
        response = db_manager_stub.get_available_workplace_types(request)

        assert response.timestamp
        assert len(response.workplace_types) > 0

    def test_get_available_defect_policies(self, db_manager_stub):
        """Тест получения политик работы с браком."""
        request = GetAvailableDefectPoliciesRequest()
        response = db_manager_stub.get_available_defect_policies(request)

        assert response.timestamp
        assert len(response.policies) > 0

    def test_get_available_improvements_list(self, db_manager_stub):
        """Тест получения списка доступных улучшений."""
        request = GetAvailableImprovementsListRequest()
        response = db_manager_stub.get_available_improvements_list(request)

        assert response.timestamp
        assert len(response.improvements) > 0

    def test_get_available_certifications(self, db_manager_stub):
        """Тест получения доступных сертификаций."""
        request = GetAvailableCertificationsRequest()
        response = db_manager_stub.get_available_certifications(request)

        assert response.timestamp
        assert len(response.certifications) > 0

    def test_get_available_sales_strategies(self, db_manager_stub):
        """Тест получения доступных стратегий продаж."""
        request = GetAvailableSalesStrategiesRequest()
        response = db_manager_stub.get_available_sales_strategies(request)

        assert response.timestamp
        assert len(response.strategies) > 0

    # Примечание: get_available_dealing_with_defects не существует в stub
    # Используйте test_get_available_defect_policies вместо этого

    def test_get_available_lean_improvements(self, db_manager_stub):
        """Тест получения доступных LEAN улучшений из БД."""
        request = GetAvailableLeanImprovementsRequest()
        response = db_manager_stub.get_available_lean_improvements(request)

        assert response.timestamp


class TestPingMethod:
    """Тесты для метода ping."""

    def test_ping(self, db_manager_stub):
        """Тест ping метода."""
        request = PingRequest()
        response = db_manager_stub.ping(request)

        assert response.success is True
        assert response.message
        assert response.timestamp
