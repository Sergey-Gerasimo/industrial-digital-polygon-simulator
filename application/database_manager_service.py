from typing import Dict
import uuid
from datetime import datetime
import grpc
from grpc_generated.simulator_pb2 import (
    CreateEquipmentRequest,
    DeleteEquipmentRequest,
    GetAllEquipmentRequest,
    GetAllEquipmentResopnse,
    Route,
    Supplier,
    UpdateEquipmentRequest,
    Warehouse,
    Worker,
    Logist,
    Equipment,
    Workplace,
    ProcessGraph,
    Consumer,
    Tender,
    SuccessResponse,
    GetAllSuppliersResponse,
    GetAllWorkersResponse,
    GetAllLogistsResponse,
    GetAllWorkplacesResponse,
    GetAllConsumersResponse,
    GetAllTendersResponse,
    PingRequest,
    # Requests
    CreateSupplierRequest,
    UpdateSupplierRequest,
    DeleteSupplierRequest,
    GetAllSuppliersRequest,
    GetWarehouseRequest,
    CreateWorkerRequest,
    UpdateWorkerRequest,
    DeleteWorkerRequest,
    GetAllWorkersRequest,
    CreateLogistRequest,
    UpdateLogistRequest,
    DeleteLogistRequest,
    GetAllLogistsRequest,
    CreateWorkplaceRequest,
    UpdateWorkplaceRequest,
    DeleteWorkplaceRequest,
    GetAllWorkplacesRequest,
    GetProcessGraphRequest,
    CreateConsumerRequest,
    UpdateConsumerRequest,
    DeleteConsumerRequest,
    GetAllConsumersRequest,
    CreateTenderRequest,
    UpdateTenderRequest,
    DeleteTenderRequest,
    GetAllTendersRequest,
)
from grpc_generated.simulator_pb2_grpc import SimulationDatabaseManagerServicer


class SimulationDatabaseManagerImpl(SimulationDatabaseManagerServicer):
    def __init__(self) -> None:
        self.suppliers: Dict[str, Supplier] = {}
        self.workers: Dict[str, Worker] = {}
        self.logists: Dict[str, Logist] = {}
        self.workplaces: Dict[str, Workplace] = {}
        self.consumers: Dict[str, Consumer] = {}
        self.tenders: Dict[str, Tender] = {}
        self.equipment: Dict[str, Equipment] = {}
        self._init_test_data()

    def _init_test_data(self):
        """Инициализация тестовых данных."""
        # Тестовые поставщики
        self.suppliers["supplier_001"] = Supplier(
            supplier_id="supplier_001",
            name="ООО 'МеталлПром'",
            product_name="Листовой металл",
            delivery_period=5,
            special_delivery_period=2,
            reliability=0.92,
            product_quality=0.88,
            cost=120000,
            special_delivery_cost=200000,
        )

        # Тестовые рабочие
        self.workers["worker_001"] = Worker(
            worker_id="worker_001",
            name="Иванов Иван Иванович",
            qualification=5,
            specialty="Слесарь-сборщик",
            salary=75000,
        )

        # Тестовые логисты
        self.logists["logist_001"] = Logist(
            worker_id="logist_001",
            name="Смирнов Александр Сергеевич",
            qualification=7,
            specialty="Логистика",
            salary=95000,
            speed=70,
            vehicle_type="Грузовой фургон",
        )

        # Тестовое оборудование
        self.equipment["equipment_001"] = Equipment(
            equipment_id="equipment_001",
            name="Токарный станок ЧПУ",
            reliability=0.95,
            maintenance_period=30,
            maintenance_cost=50000,
            cost=1500000,
            repair_cost=300000,
            repair_time=5,
        )

        # Тестовые рабочие места
        self.workplaces["workplace_001"] = Workplace(
            workplace_id="workplace_001",
            workplace_name="Слесарный участок №1",
            required_speciality="Слесарь",
            required_qualification=4,
            required_stages=["Склад", "Подготовка"],
        )

        # Тестовые заказчики
        self.consumers["consumer_001"] = Consumer(
            consumer_id="consumer_001",
            name="ООО 'Промышленные Технологии'",
            type="Государственная",
        )

        # Тестовые тендеры
        self.tenders["tender_001"] = Tender(
            tender_id="tender_001",
            consumer=self.consumers["consumer_001"],
            cost=3500000,
            quantity_of_products=15,
        )

    async def create_supplier(
        self, request: CreateSupplierRequest, context
    ) -> Supplier:
        supplier_id = f"supplier_{uuid.uuid4().hex[:8]}"

        supplier = Supplier(
            supplier_id=supplier_id,
            name=request.name,
            product_name=request.product_name,
            delivery_period=request.delivery_period,
            special_delivery_period=request.special_delivery_period,
            reliability=request.reliability,
            product_quality=request.product_quality,
            cost=request.cost,
            special_delivery_cost=request.special_delivery_cost,
        )

        self.suppliers[supplier_id] = supplier
        return supplier

    async def update_supplier(
        self, request: UpdateSupplierRequest, context
    ) -> Supplier:
        if request.supplier_id not in self.suppliers:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Поставщик с ID {request.supplier_id} не найден")
            return Supplier()

        supplier = self.suppliers[request.supplier_id]

        # Обновляем поля
        if request.name:
            supplier.name = request.name
        if request.product_name:
            supplier.product_name = request.product_name
        if request.delivery_period:
            supplier.delivery_period = request.delivery_period
        if request.special_delivery_period:
            supplier.special_delivery_period = request.special_delivery_period
        if request.reliability:
            supplier.reliability = request.reliability
        if request.product_quality:
            supplier.product_quality = request.product_quality
        if request.cost:
            supplier.cost = request.cost
        if request.special_delivery_cost:
            supplier.special_delivery_cost = request.special_delivery_cost

        return supplier

    async def delete_supplier(
        self, request: DeleteSupplierRequest, context
    ) -> SuccessResponse:
        if request.supplier_id not in self.suppliers:
            return SuccessResponse(
                success=False,
                message=f"Поставщик с ID {request.supplier_id} не найден",
                timestamp=datetime.now().isoformat(),
            )

        del self.suppliers[request.supplier_id]

        return SuccessResponse(
            success=True,
            message=f"Поставщик {request.supplier_id} успешно удален",
            timestamp=datetime.now().isoformat(),
        )

    async def get_all_suppliers(
        self, request: GetAllSuppliersRequest, context
    ) -> GetAllSuppliersResponse:
        return GetAllSuppliersResponse(
            suppliers=list(self.suppliers.values()),
            total_count=len(self.suppliers),
        )

    async def get_warehouse(self, request: GetWarehouseRequest, context) -> Warehouse:
        return Warehouse(
            warehouse_id=request.warehouse_id,
            inventory_worker=Worker(
                worker_id="worker_001",
                name="Сидоров Сидор Сидорович",
                qualification=3,
                specialty="Кладовщик",
                salary=45000,
            ),
            size=800,
            loading=320,
            materials={
                "Металл": 150,
                "Пластик": 100,
                "Электроника": 70,
            },
        )

    async def create_worker(self, request: CreateWorkerRequest, context) -> Worker:
        worker_id = f"worker_{uuid.uuid4().hex[:8]}"

        worker = Worker(
            worker_id=worker_id,
            name=request.name,
            qualification=request.qualification,
            specialty=request.specialty,
            salary=request.salary,
        )

        self.workers[worker_id] = worker
        return worker

    async def update_worker(self, request: UpdateWorkerRequest, context) -> Worker:
        if request.worker_id not in self.workers:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Рабочий с ID {request.worker_id} не найден")
            return Worker()

        worker = self.workers[request.worker_id]

        # Обновляем поля
        if request.name:
            worker.name = request.name
        if request.qualification:
            worker.qualification = request.qualification
        if request.specialty:
            worker.specialty = request.specialty
        if request.salary:
            worker.salary = request.salary

        return worker

    async def delete_worker(
        self, request: DeleteWorkerRequest, context
    ) -> SuccessResponse:
        if request.worker_id not in self.workers:
            return SuccessResponse(
                success=False,
                message=f"Рабочий с ID {request.worker_id} не найден",
                timestamp=datetime.now().isoformat(),
            )

        del self.workers[request.worker_id]

        return SuccessResponse(
            success=True,
            message=f"Рабочий {request.worker_id} успешно удален",
            timestamp=datetime.now().isoformat(),
        )

    async def get_all_workers(
        self, request: GetAllWorkersRequest, context
    ) -> GetAllWorkersResponse:
        return GetAllWorkersResponse(
            workers=list(self.workers.values()),
            total_count=len(self.workers),
        )

    async def create_logist(self, request: CreateLogistRequest, context) -> Logist:
        logist_id = f"logist_{uuid.uuid4().hex[:8]}"

        logist = Logist(
            worker_id=logist_id,
            name=request.name,
            qualification=request.qualification,
            specialty=request.specialty,
            salary=request.salary,
            speed=request.speed,
            vehicle_type=request.vehicle_type,
        )

        self.logists[logist_id] = logist
        return logist

    async def update_logist(self, request: UpdateLogistRequest, context) -> Logist:
        if request.worker_id not in self.logists:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Логист с ID {request.worker_id} не найден")
            return Logist()

        logist = self.logists[request.worker_id]

        # Обновляем поля
        if request.name:
            logist.name = request.name
        if request.qualification:
            logist.qualification = request.qualification
        if request.specialty:
            logist.specialty = request.specialty
        if request.salary:
            logist.salary = request.salary
        if request.speed:
            logist.speed = request.speed
        if request.vehicle_type:
            logist.vehicle_type = request.vehicle_type

        return logist

    async def delete_logist(
        self, request: DeleteLogistRequest, context
    ) -> SuccessResponse:
        if request.worker_id not in self.logists:
            return SuccessResponse(
                success=False,
                message=f"Логист с ID {request.worker_id} не найден",
                timestamp=datetime.now().isoformat(),
            )

        del self.logists[request.worker_id]

        return SuccessResponse(
            success=True,
            message=f"Логист {request.worker_id} успешно удален",
            timestamp=datetime.now().isoformat(),
        )

    async def get_all_logists(
        self, request: GetAllLogistsRequest, context
    ) -> GetAllLogistsResponse:
        return GetAllLogistsResponse(
            logists=list(self.logists.values()),
            total_count=len(self.logists),
        )

    async def create_workplace(
        self, request: CreateWorkplaceRequest, context
    ) -> Workplace:
        workplace_id = f"workplace_{uuid.uuid4().hex[:8]}"

        workplace = Workplace(
            workplace_id=workplace_id,
            workplace_name=request.workplace_name,
            required_speciality=request.required_speciality,
            required_qualification=(
                int(request.required_qualification)
                if request.required_qualification
                else 0
            ),
            required_stages=list(request.required_stages),
        )

        self.workplaces[workplace_id] = workplace
        return workplace

    async def update_workplace(
        self, request: UpdateWorkplaceRequest, context
    ) -> Workplace:
        if request.workplace_id not in self.workplaces:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Рабочее место с ID {request.workplace_id} не найден")
            return Workplace()

        workplace = self.workplaces[request.workplace_id]

        # Обновляем поля
        if request.workplace_name:
            workplace.workplace_name = request.workplace_name
        if request.required_speciality:
            workplace.required_speciality = request.required_speciality
        if request.required_qualification:
            workplace.required_qualification = int(request.required_qualification)
        if request.required_stages:
            workplace.required_stages[:] = request.required_stages

        return workplace

    async def delete_workplace(
        self, request: DeleteWorkplaceRequest, context
    ) -> SuccessResponse:
        if request.workplace_id not in self.workplaces:
            return SuccessResponse(
                success=False,
                message=f"Рабочее место с ID {request.workplace_id} не найден",
                timestamp=datetime.now().isoformat(),
            )

        del self.workplaces[request.workplace_id]

        return SuccessResponse(
            success=True,
            message=f"Рабочее место {request.workplace_id} успешно удалено",
            timestamp=datetime.now().isoformat(),
        )

    async def get_all_workplaces(
        self, request: GetAllWorkplacesRequest, context
    ) -> GetAllWorkplacesResponse:
        return GetAllWorkplacesResponse(
            workplaces=list(self.workplaces.values()),
            total_count=len(self.workplaces),
        )

    async def get_process_graph(
        self, request: GetProcessGraphRequest, context
    ) -> ProcessGraph:
        return ProcessGraph(
            process_graph_id=request.process_graph_id,
            workplaces=list(self.workplaces.values()),
            routes=[
                Route(
                    length=15,
                    from_workplace="workplace_001",
                    to_workplace="workplace_002",
                ),
                Route(
                    length=10,
                    from_workplace="workplace_002",
                    to_workplace="workplace_003",
                ),
            ],
        )

    async def create_consumer(
        self, request: CreateConsumerRequest, context
    ) -> Consumer:
        consumer_id = f"consumer_{uuid.uuid4().hex[:8]}"

        consumer = Consumer(
            consumer_id=consumer_id,
            name=request.name,
            type=request.type,
        )

        self.consumers[consumer_id] = consumer
        return consumer

    async def update_consumer(
        self, request: UpdateConsumerRequest, context
    ) -> Consumer:
        if request.consumer_id not in self.consumers:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Заказчик с ID {request.consumer_id} не найден")
            return Consumer()

        consumer = self.consumers[request.consumer_id]

        # Обновляем поля
        if request.name:
            consumer.name = request.name
        if request.type:
            consumer.type = request.type

        return consumer

    async def delete_consumer(
        self, request: DeleteConsumerRequest, context
    ) -> SuccessResponse:
        if request.consumer_id not in self.consumers:
            return SuccessResponse(
                success=False,
                message=f"Заказчик с ID {request.consumer_id} не найден",
                timestamp=datetime.now().isoformat(),
            )

        del self.consumers[request.consumer_id]

        return SuccessResponse(
            success=True,
            message=f"Заказчик {request.consumer_id} успешно удален",
            timestamp=datetime.now().isoformat(),
        )

    async def get_all_consumers(
        self, request: GetAllConsumersRequest, context
    ) -> GetAllConsumersResponse:
        return GetAllConsumersResponse(
            consumers=list(self.consumers.values()),
            total_count=len(self.consumers),
        )

    async def create_tender(self, request: CreateTenderRequest, context) -> Tender:
        tender_id = f"tender_{uuid.uuid4().hex[:8]}"

        # Получаем заказчика
        consumer = None
        if request.consumer_id in self.consumers:
            consumer = self.consumers[request.consumer_id]
        else:
            # Создаем временного заказчика
            consumer = Consumer(
                consumer_id=request.consumer_id,
                name="Временный заказчик",
                type="Коммерческая",
            )

        tender = Tender(
            tender_id=tender_id,
            consumer=consumer,
            cost=request.cost,
            quantity_of_products=request.quantity_of_products,
        )

        self.tenders[tender_id] = tender
        return tender

    async def update_tender(self, request: UpdateTenderRequest, context) -> Tender:
        if request.tender_id not in self.tenders:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Тендер с ID {request.tender_id} не найден")
            return Tender()

        tender = self.tenders[request.tender_id]

        # Обновляем поля
        if request.consumer_id:
            # Обновляем заказчика если есть
            if request.consumer_id in self.consumers:
                tender.consumer.CopyFrom(self.consumers[request.consumer_id])
        if request.cost:
            tender.cost = request.cost
        if request.quantity_of_products:
            tender.quantity_of_products = request.quantity_of_products

        return tender

    async def delete_tender(
        self, request: DeleteTenderRequest, context
    ) -> SuccessResponse:
        if request.tender_id not in self.tenders:
            return SuccessResponse(
                success=False,
                message=f"Тендер с ID {request.tender_id} не найден",
                timestamp=datetime.now().isoformat(),
            )

        del self.tenders[request.tender_id]

        return SuccessResponse(
            success=True,
            message=f"Тендер {request.tender_id} успешно удален",
            timestamp=datetime.now().isoformat(),
        )

    async def get_all_tenders(
        self, request: GetAllTendersRequest, context
    ) -> GetAllTendersResponse:
        return GetAllTendersResponse(
            tenders=list(self.tenders.values()),
            total_count=len(self.tenders),
        )

    async def create_equipment(
        self, request: CreateEquipmentRequest, context
    ) -> Equipment:
        equipment_id = f"equipment_{uuid.uuid4().hex[:8]}"

        equipment = Equipment(
            equipment_id=equipment_id,
            name=request.name,
            reliability=request.reliability,
            maintenance_period=request.maintenance_period,
            maintenance_cost=request.maintenance_cost,
            cost=request.cost,
            repair_cost=request.repair_cost,
            repair_time=request.repair_time,
        )

        self.equipment[equipment_id] = equipment
        return equipment

    async def update_equipment(
        self, request: UpdateEquipmentRequest, context
    ) -> Equipment:
        if request.equipment_id not in self.equipment:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Оборудование с ID {request.equipment_id} не найдено")
            return Equipment()

        equipment = self.equipment[request.equipment_id]

        # Обновляем поля
        if request.name:
            equipment.name = request.name
        if request.reliability:
            equipment.reliability = request.reliability
        if request.maintenance_period:
            equipment.maintenance_period = request.maintenance_period
        if request.maintenance_cost:
            equipment.maintenance_cost = request.maintenance_cost
        if request.cost:
            equipment.cost = request.cost
        if request.repair_cost:
            equipment.repair_cost = request.repair_cost
        if request.repair_time:
            equipment.repair_time = request.repair_time

        return equipment

    async def delete_equipment(
        self, request: DeleteEquipmentRequest, context
    ) -> SuccessResponse:
        if request.equipment_id not in self.equipment:
            return SuccessResponse(
                success=False,
                message=f"Оборудование с ID {request.equipment_id} не найдено",
                timestamp=datetime.now().isoformat(),
            )

        del self.equipment[request.equipment_id]

        return SuccessResponse(
            success=True,
            message=f"Оборудование {request.equipment_id} успешно удалено",
            timestamp=datetime.now().isoformat(),
        )

    async def get_all_equipment(
        self, request: GetAllEquipmentRequest, context
    ) -> GetAllEquipmentResopnse:
        return GetAllEquipmentResopnse(
            equipments=list(self.equipment.values()),
            total_count=len(self.equipment),
        )

    async def ping(self, request: PingRequest, context) -> SuccessResponse:
        return SuccessResponse(
            success=True,
            message="Database manager service is running",
            timestamp=datetime.now().isoformat(),
        )
