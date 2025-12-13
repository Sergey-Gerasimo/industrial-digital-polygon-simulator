# gRPC API Reference: Client Library Development Guide

## Общая Архитектура

### Двухсервисная Архитектура
Проект реализует два отдельных gRPC сервиса на разных портах:

- **SimulationService** (порт 50051) - управление симуляциями и бизнес-логикой
- **SimulationDatabaseManager** (порт 50052) - управление данными и CRUD операции

```python
# application/serve_functions.py
simulation_server = grpc.aio.server(...)  # порт 50051
db_manager_server = grpc.aio.server(...)  # порт 50052

add_SimulationServiceServicer_to_server(simulation_service, simulation_server)
add_SimulationDatabaseManagerServicer_to_server(db_manager_service, db_manager_server)
```

---

## API Reference для Клиентской Библиотеки

### Endpoints и Порты
- **SimulationService**: `localhost:50051` (бизнес-логика симуляций)
- **SimulationDatabaseManager**: `localhost:50052` (управление данными)

### Аутентификация и Авторизация
```python
# Использование room_id через metadata
metadata = [('room-id', 'your-room-id')]
response = stub.method_name(request, metadata=metadata)
```

### Connection Setup
```python
import grpc

# Создание канала
channel = grpc.aio.insecure_channel('localhost:50051')

# Создание stub'ов
simulation_stub = SimulationServiceStub(channel)
db_stub = SimulationDatabaseManagerStub(channel)
```

### Таймауты и Retry Policy
```python
# Таймаут для конкретного вызова
response = await stub.method_name(request, timeout=30.0)

# Retry policy (через channel options)
options = [
    ('grpc.enable_retries', 1),
    ('grpc.service_config', json.dumps({
        'methodConfig': [{
            'name': [{'service': 'SimulationService'}],
            'retryPolicy': {
                'maxAttempts': 3,
                'initialBackoff': '0.1s',
                'maxBackoff': '10s',
                'backoffMultiplier': 2.0,
                'retryableStatusCodes': ['UNAVAILABLE', 'DEADLINE_EXCEEDED']
            }
        }]
    }))
]
channel = grpc.aio.insecure_channel('localhost:50051', options=options)
```

---

## Ключевые Особенности Реализации

### 1. Асинхронная Архитектура
```python
# Все методы сервисов - async
async def create_simulation(self, request, context) -> SimulationResponse:
async def create_supplier(self, request, context) -> Supplier:
```

**Особенности:**
- Используется `grpc.aio.server` вместо синхронного `grpc.server`
- Все методы возвращают `Coroutine[Any, Any, Response]`
- Поддержка асинхронных операций с базой данных через SQLAlchemy AsyncSession

### 2. Dependency Injection через Session Factory
```python
# application/simulation_service.py
class SimulationServiceImpl(SimulationServiceServicer):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory
```

**Преимущества:**
- Легкое тестирование через mock session factories
- Отделение инфраструктурных зависимостей
- Возможность конфигурации пула соединений на уровне приложения

### 3. Domain-Driven Design (DDD) Интеграция
```python
# Преобразование proto -> domain -> proto
domain_supplier = proto_supplier_to_domain(proto_request)
saved_supplier = await repo.save(domain_supplier)
return domain_supplier_to_proto(saved_supplier)
```

**Особенности:**
- Все бизнес-логика находится в domain layer
- Proto сообщения используются только для транспорта
- Исключения domain layer пробрасываются в gRPC через ValueError

### 4. Комплексная Обработка Ошибок
```python
try:
    # бизнес-логика
    simulation = await self._load_simulation(session, simulation_id, context)
    if simulation is None:
        return SimulationResponse()
except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)
    context.set_code(grpc.StatusCode.INTERNAL)
    context.set_details(f"Ошибка: {str(e)}")
    return SimulationResponse()
```

**Особенности:**
- Использование gRPC status codes (NOT_FOUND, INTERNAL, INVALID_ARGUMENT, etc.)
- Детальное логирование с `exc_info=True`
- Graceful degradation - возврат пустых ответов вместо падения

### 5. Transaction Management
```python
async def _update_and_save(self, simulation_id, update_func, context):
    async with self.session_factory() as session:
        try:
            # загрузка и обновление
            simulation = await self._load_simulation(session, simulation_id, context)
            update_func(simulation)
            saved = await self._save_simulation(session, simulation, context)

            # commit только после успешного сохранения
            await session.commit()
            return await self._build_simulation_response(session, simulation_id)
        except ValueError:
            await session.rollback()
            raise  # проброс бизнес-ошибок
        except Exception as e:
            await session.rollback()
            # обработка системных ошибок
```

**Особенности:**
- Автоматический rollback при ошибках
- Отдельные сессии для каждого запроса
- Явное управление транзакциями через context managers

### 6. Proto Mapping Layer
```python
# application/proto_mappers.py
def domain_simulation_to_proto(domain_obj) -> Simulation:
def proto_simulation_to_domain(proto_obj) -> DomainSimulation:
```

**Особенности:**
- Отдельный слой мапперов для преобразования
- Поддержка сложных вложенных структур (ProcessGraph, Metrics, etc.)
- Обработка enum значений (Qualification, ConsumerType, etc.)

### 7. Service-Specific Patterns

#### SimulationService (Бизнес-Логика)
```python
async def run_simulation(self, request, context) -> SimulationResponse:
    # Делегирование бизнес-логике domain layer
    return await self._update_and_save(
        request.simulation_id,
        lambda sim: sim.run_simulation(),
        context,
    )
```

**Особенности:**
- Фокус на orchestration бизнес-процессов
- Минимальная логика валидации (делегируется domain)
- Сложные операции с множественными сущностями

#### SimulationDatabaseManager (CRUD Operations)
```python
async def create_supplier(self, request, context) -> Supplier:
    async with self.session_factory() as session:
        # Прямое использование репозиториев
        repo = SupplierRepository(session)
        saved = await repo.save(domain_supplier)
        return domain_supplier_to_proto(saved)
```

**Особенности:**
- Стандартные CRUD операции для всех сущностей
- Массовые операции (get_all_*)
- Справочные данные и типы

### 8. Server Configuration
```python
# application/serve_functions.py
grpc_options = [
    ("grpc.max_send_message_length", 50 * 1024 * 1024),  # 50 MB
    ("grpc.max_receive_message_length", 50 * 1024 * 1024),
    ("grpc.so_reuseport", 1),
    ("grpc.so_keepalive_time_ms", 10000),
    ("grpc.so_keepalive_timeout_ms", 5000),
    ("grpc.so_keepalive_permit_without_calls", 1),
]
```

**Особенности:**
- Увеличенные лимиты сообщений для сложных данных
- Оптимизация keep-alive для долгоживущих соединений
- Настройка ThreadPoolExecutor для асинхронной обработки

### 9. Health Checks и Monitoring
```python
async def ping(self, request, context) -> SuccessResponse:
    return SuccessResponse(
        success=True,
        message="Service is running",
        timestamp=datetime.now().isoformat(),
    )
```

**Особенности:**
- Ping методы для health checks
- Timestamp в каждом ответе
- Детальная информация о статусе сервисов

### 10. Graceful Shutdown
```python
# application/serve_functions.py
try:
    await stop_event.wait()  # Ожидание сигнала остановки
finally:
    # Graceful shutdown с таймаутом
    await simulation_server.stop(grace=5)
    await db_manager_server.stop(grace=5)
```

**Особенности:**
- Обработка сигналов SIGINT/SIGTERM
- Graceful shutdown с configurable timeout
- Правильная остановка обоих серверов

### 11. Data Serialization/Deserialization
```python
# Важные аспекты для клиентской библиотеки
# 1. Enum mapping
qualification_map = {
    1: "TRAINEE",
    2: "III",
    3: "II",
    4: "I"
}

# 2. Complex object handling (ProcessGraph, Metrics)
# Клиентская библиотека должна предоставлять удобные методы
# для работы с вложенными структурами

# 3. Timestamp handling
import datetime
timestamp = datetime.datetime.fromisoformat(response.timestamp)
```

### 12. Error Handling Patterns
```python
from grpc import RpcError, StatusCode

async def safe_call(stub_method, request):
    try:
        response = await stub_method(request)
        return response, None
    except RpcError as e:
        if e.code() == StatusCode.NOT_FOUND:
            return None, "Resource not found"
        elif e.code() == StatusCode.INVALID_ARGUMENT:
            return None, f"Invalid argument: {e.details()}"
        elif e.code() == StatusCode.INTERNAL:
            return None, f"Internal server error: {e.details()}"
        else:
            return None, f"gRPC error {e.code()}: {e.details()}"
```

### 13. Connection Pooling и Lifecycle
```python
class SimulationClient:
    def __init__(self, host="localhost", simulation_port=50051, db_port=50052):
        self.simulation_channel = grpc.aio.insecure_channel(f"{host}:{simulation_port}")
        self.db_channel = grpc.aio.insecure_channel(f"{host}:{db_port}")

        self.simulation_stub = SimulationServiceStub(self.simulation_channel)
        self.db_stub = SimulationDatabaseManagerStub(self.db_channel)

    async def close(self):
        await self.simulation_channel.close()
        await self.db_channel.close()
```

### 14. Batch Operations
```python
# Для массовых операций использовать asyncio.gather
async def create_multiple_suppliers(stub, suppliers_data):
    tasks = [
        stub.create_supplier(CreateSupplierRequest(**data))
        for data in suppliers_data
    ]
    return await asyncio.gather(*tasks, return_exceptions=True)
```

---

## Детальное API Reference

### SimulationService Methods

#### Core Simulation Operations
```python
# Create new simulation
request = CreateSimulationRquest()
response = await simulation_stub.create_simulation(request)
simulation_id = response.simulations.simulation_id

# Get simulation by ID
request = GetSimulationRequest(simulation_id=simulation_id)
response = await simulation_stub.get_simulation(request)

# Run simulation step
request = RunSimulationRequest(simulation_id=simulation_id)
response = await simulation_stub.run_simulation(request)
```

#### Personnel Management
```python
# Set logist
request = SetLogistRequest(simulation_id=sim_id, worker_id=worker_id)
response = await simulation_stub.set_logist(request)

# Set warehouse worker
request = SetWarehouseInventoryWorkerRequest(
    simulation_id=sim_id,
    worker_id=worker_id,
    warehouse_type=1  # WAREHOUSE_TYPE_MATERIALS
)
response = await simulation_stub.set_warehouse_inventory_worker(request)

# Assign worker to workplace
request = SetWorkerOnWorkerplaceRequest(
    simulation_id=sim_id,
    workplace_id=workplace_id,
    worker_id=worker_id
)
response = await simulation_stub.set_worker_on_workerplace(request)
```

#### Supplier Management
```python
# Add supplier to simulation
request = AddSupplierRequest(simulation_id=sim_id, supplier_id=supplier_id)
response = await simulation_stub.add_supplier(request)

# Remove supplier from simulation
request = DeleteSupplierRequest(simulation_id=sim_id, supplier_id=supplier_id)
response = await simulation_stub.delete_supplier(request)
```

#### Process Configuration
```python
# Update process graph
request = UpdateProcessGraphRequest(simulation_id=sim_id, process_graph=graph)
response = await simulation_stub.update_process_graph(request)

# Set production plan
request = SetProductionPlanRowRequest(simulation_id=sim_id, row=plan_row)
response = await simulation_stub.set_production_plan_row(request)
```

#### Tender Management
```python
# Add tender to simulation
request = AddTenderRequest(simulation_id=sim_id, tender_id=tender_id)
response = await simulation_stub.add_tender(request)
```

#### Settings
```python
# Set defect policy
request = SetDealingWithDefectsRequest(simulation_id=sim_id, dealing_with_defects=policy)
response = await simulation_stub.set_dealing_with_defects(request)

# Set sales strategy
request = SetSalesStrategyRequest(simulation_id=sim_id, strategy=strategy)
response = await simulation_stub.set_sales_strategy(request)

# Set LEAN improvements
request = SetLeanImprovementStatusRequest(
    simulation_id=sim_id,
    name=improvement_name,
    is_implemented=True
)
response = await simulation_stub.set_lean_improvement_status(request)
```

#### Metrics
```python
# Get factory metrics
request = GetMetricsRequest(simulation_id=sim_id)
metrics = await simulation_stub.get_factory_metrics(request)

# Get production metrics
production = await simulation_stub.get_production_metrics(request)

# Get all metrics at once
all_metrics = await simulation_stub.get_all_metrics(
    GetAllMetricsRequest(simulation_id=sim_id)
)
```

#### Data Retrieval
```python
# Get production schedule
schedule = await simulation_stub.get_production_schedule(
    GetProductionScheduleRequest(simulation_id=sim_id)
)

# Get workshop plan
workshop = await simulation_stub.get_workshop_plan(
    GetWorkshopPlanRequest(simulation_id=sim_id)
)

# Get warehouse load chart
chart = await simulation_stub.get_warehouse_load_chart(
    GetWarehouseLoadChartRequest(simulation_id=sim_id, warehouse_id="materials_1")
)

# Get required materials
materials = await simulation_stub.get_required_materials(
    GetRequiredMaterialsRequest(simulation_id=sim_id)
)

# Get available improvements
improvements = await simulation_stub.get_available_improvements(
    GetAvailableImprovementsRequest(simulation_id=sim_id)
)
```

### SimulationDatabaseManager Methods

#### CRUD Operations - Suppliers
```python
# Create supplier
supplier_data = {
    "name": "Supplier ABC",
    "product_name": "Steel",
    "material_type": "Raw Material",
    "delivery_period": 7,
    "reliability": 0.95,
    "product_quality": 0.9,
    "cost": 100.0,
    "special_delivery_period": 3,
    "special_delivery_cost": 150.0
}
request = CreateSupplierRequest(**supplier_data)
supplier = await db_stub.create_supplier(request)

# Update supplier
request = UpdateSupplierRequest(supplier_id=supplier.supplier_id, name="New Name")
updated = await db_stub.update_supplier(request)

# Delete supplier
request = DeleteSupplierRequest(supplier_id=supplier.supplier_id)
result = await db_stub.delete_supplier(request)

# Get all suppliers
suppliers = await db_stub.get_all_suppliers(GetAllSuppliersRequest())
```

#### CRUD Operations - Workers
```python
# Create worker
worker_data = {
    "name": "John Doe",
    "qualification": 3,  # III
    "specialty": "WELDER",
    "salary": 50000
}
request = CreateWorkerRequest(**worker_data)
worker = await db_stub.create_worker(request)

# Update worker
request = UpdateWorkerRequest(
    worker_id=worker.worker_id,
    salary=55000
)
updated = await db_stub.update_worker(request)

# Get all workers (non-logists)
workers = await db_stub.get_all_workers(GetAllWorkersRequest())
```

#### CRUD Operations - Logists
```python
# Create logist
logist_data = {
    "name": "Jane Smith",
    "qualification": 2,  # II
    "specialty": "LOGISTICS",
    "salary": 45000,
    "speed": 80,  # km/h
    "vehicle_type": "TRUCK"
}
request = CreateLogistRequest(**logist_data)
logist = await db_stub.create_logist(request)

# Update logist
request = UpdateLogistRequest(
    logist_id=logist.worker_id,
    speed=90
)
updated = await db_stub.update_logist(request)

# Get all logists
logists = await db_stub.get_all_logists(GetAllLogistsRequest())
```

#### CRUD Operations - Workplaces
```python
# Create workplace
workplace_data = {
    "workplace_name": "Welding Station 1",
    "required_speciality": "WELDER",
    "required_qualification": 3,
    "required_equipment": "WELDING_MACHINE",
    "required_stages": ["CUTTING", "WELDING", "GRINDING"]
}
request = CreateWorkplaceRequest(**workplace_data)
workplace = await db_stub.create_workplace(request)

# Get all workplaces
workplaces = await db_stub.get_all_workplaces(GetAllWorkplacesRequest())
```

#### CRUD Operations - Consumers
```python
# Create consumer
consumer_data = {
    "name": "ABC Corporation",
    "type": 1  # GOVERNMENT
}
request = CreateConsumerRequest(**consumer_data)
consumer = await db_stub.create_consumer(request)

# Get all consumers
consumers = await db_stub.get_all_consumers(GetAllConsumersRequest())
```

#### CRUD Operations - Tenders
```python
# Create tender
tender_data = {
    "consumer_id": consumer.consumer_id,
    "cost": 100000.0,
    "quantity_of_products": 1000,
    "penalty_per_day": 1000.0,
    "warranty_years": 2,
    "payment_form": "CASH"
}
request = CreateTenderRequest(**tender_data)
tender = await db_stub.create_tender(request)

# Get all tenders
tenders = await db_stub.get_all_tenders(GetAllTendersRequest())
```

#### CRUD Operations - Equipment
```python
# Create equipment
equipment_data = {
    "name": "CNC Machine",
    "equipment_type": "MACHINING",
    "reliability": 0.98,
    "maintenance_period": 30,
    "maintenance_cost": 500.0,
    "cost": 50000.0,
    "repair_cost": 2000.0,
    "repair_time": 8
}
request = CreateEquipmentRequest(**equipment_data)
equipment = await db_stub.create_equipment(request)

# Get all equipment
equipment_list = await db_stub.get_all_equipment(GetAllEquipmentRequest())
```

#### CRUD Operations - LEAN Improvements
```python
# Create LEAN improvement
improvement_data = {
    "name": "Just-in-Time Production",
    "is_implemented": False,
    "implementation_cost": 10000.0,
    "efficiency_gain": 0.15
}
request = CreateLeanImprovementRequest(**improvement_data)
improvement = await db_stub.create_lean_improvement(request)

# Get all LEAN improvements
improvements = await db_stub.get_all_lean_improvements(GetAllLeanImprovementsRequest())
```

#### Reference Data Methods
```python
# Get material types
material_types = await db_stub.get_available_material_types(
    GetMaterialTypesRequest()
)

# Get equipment types
equipment_types = await db_stub.get_available_equipment_types(
    GetEquipmentTypesRequest()
)

# Get workplace types
workplace_types = await db_stub.get_available_workplace_types(
    GetWorkplaceTypesRequest()
)

# Get defect policies
defect_policies = await db_stub.get_available_defect_policies(
    GetAvailableDefectPoliciesRequest()
)

# Get sales strategies
sales_strategies = await db_stub.get_available_sales_strategies(
    GetAvailableSalesStrategiesRequest()
)

# Get certifications
certifications = await db_stub.get_available_certifications(
    GetAvailableCertificationsRequest()
)
```

---

## Клиентская Библиотека: Рекомендации по Реализации

### 1. Высокоуровневые Клиентские Классы
```python
class SimulationServiceClient:
    def __init__(self, host="localhost", port=50051):
        self.channel = grpc.aio.insecure_channel(f"{host}:{port}")
        self.stub = SimulationServiceStub(self.channel)

    async def create_and_run_simulation(self, capital=10000000):
        """Высокоуровневый метод для создания и запуска симуляции"""
        # Create simulation
        sim_response = await self.stub.create_simulation(CreateSimulationRquest())

        # Run first step
        run_response = await self.stub.run_simulation(
            RunSimulationRequest(simulation_id=sim_response.simulations.simulation_id)
        )

        return sim_response.simulations.simulation_id

    async def get_simulation_status(self, simulation_id):
        """Получить полный статус симуляции"""
        # Get simulation data
        sim = await self.stub.get_simulation(
            GetSimulationRequest(simulation_id=simulation_id)
        )

        # Get metrics
        metrics = await self.stub.get_all_metrics(
            GetAllMetricsRequest(simulation_id=simulation_id)
        )

        return {
            'simulation': sim.simulations,
            'metrics': metrics
        }
```

### 2. Typed Exceptions
```python
class SimulationError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")

class SimulationNotFoundError(SimulationError):
    pass

class InvalidSimulationArgumentError(SimulationError):
    pass

# В клиентской библиотеке
def handle_grpc_error(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except RpcError as e:
            if e.code() == StatusCode.NOT_FOUND:
                raise SimulationNotFoundError(e.code(), e.details())
            elif e.code() == StatusCode.INVALID_ARGUMENT:
                raise InvalidSimulationArgumentError(e.code(), e.details())
            else:
                raise SimulationError(e.code(), e.details())
    return wrapper
```

### 3. Configuration Management
```python
@dataclass
class ClientConfig:
    host: str = "localhost"
    simulation_port: int = 50051
    db_port: int = 50052
    timeout: float = 30.0
    max_retries: int = 3
    room_id: Optional[str] = None

    @property
    def simulation_endpoint(self) -> str:
        return f"{self.host}:{self.simulation_port}"

    @property
    def db_endpoint(self) -> str:
        return f"{self.host}:{self.db_port}"

    def get_metadata(self) -> List[Tuple[str, str]]:
        metadata = []
        if self.room_id:
            metadata.append(("room-id", self.room_id))
        return metadata
```

### 4. Connection Pool и Circuit Breaker
```python
class PooledSimulationClient:
    def __init__(self, config: ClientConfig, pool_size: int = 10):
        self.config = config
        self.pool_size = pool_size
        self.channels: List[grpc.aio.Channel] = []
        self.stubs: List[SimulationServiceStub] = []
        self._lock = asyncio.Lock()

    async def _ensure_pool(self):
        async with self._lock:
            if not self.channels:
                for _ in range(self.pool_size):
                    channel = grpc.aio.insecure_channel(
                        self.config.simulation_endpoint,
                        options=self._get_channel_options()
                    )
                    self.channels.append(channel)
                    self.stubs.append(SimulationServiceStub(channel))

    def _get_channel_options(self) -> List[Tuple[str, Any]]:
        return [
            ('grpc.max_send_message_length', 50 * 1024 * 1024),
            ('grpc.max_receive_message_length', 50 * 1024 * 1024),
            ('grpc.keepalive_time_ms', 10000),
            ('grpc.keepalive_timeout_ms', 5000),
        ]

    async def get_stub(self) -> SimulationServiceStub:
        await self._ensure_pool()
        # Round-robin selection
        return random.choice(self.stubs)
```

### 5. Streaming и Batch Operations
```python
class BatchOperationsMixin:
    async def batch_create_suppliers(self, suppliers_data: List[Dict]) -> List[Supplier]:
        """Массовое создание поставщиков"""
        async with self.db_client_context() as db_stub:
            tasks = [
                db_stub.create_supplier(CreateSupplierRequest(**data))
                for data in suppliers_data
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Filter out exceptions and log them
            successful = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Failed to create supplier {i}: {result}")
                else:
                    successful.append(result)

            return successful

    async def stream_simulation_steps(self, simulation_id: str, max_steps: int = 4):
        """Потоковое выполнение шагов симуляции"""
        for step in range(1, max_steps + 1):
            try:
                response = await self.simulation_stub.run_simulation(
                    RunSimulationRequest(simulation_id=simulation_id)
                )
                yield response, step
            except RpcError as e:
                if "maximum steps reached" in str(e.details()):
                    break
                raise
```

### 6. Validation и Type Hints
```python
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, validator

class SupplierCreateRequest(BaseModel):
    name: str
    product_name: str
    material_type: str
    delivery_period: int = 7
    reliability: float = 0.9
    product_quality: float = 0.85
    cost: float
    special_delivery_period: Optional[int] = None
    special_delivery_cost: Optional[float] = None

    @validator('reliability', 'product_quality')
    def validate_percentage(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('Must be between 0 and 1')
        return v

    @validator('delivery_period', 'special_delivery_period')
    def validate_positive_int(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Must be positive')
        return v
```

### 7. Logging и Monitoring
```python
import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)

def log_grpc_call(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        start_time = time.time()
        method_name = func.__name__

        try:
            logger.debug(f"Calling {method_name}")
            result = await func(self, *args, **kwargs)
            duration = time.time() - start_time
            logger.debug(f"Completed {method_name} in {duration:.2f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed {method_name} in {duration:.2f}s: {e}")
            raise

    return wrapper

class MonitoredSimulationClient(SimulationServiceClient):
    @log_grpc_call
    async def create_simulation(self, request):
        return await self.stub.create_simulation(request)

    @log_grpc_call
    async def run_simulation(self, request):
        return await self.stub.run_simulation(request)
```

---

## Архитектурные Преимущества

### ✅ Separation of Concerns
- **SimulationService**: бизнес-логика симуляций
- **DatabaseManager**: управление данными
- **Proto Mappers**: преобразование данных
- **Domain Layer**: бизнес-правила

### ✅ Scalability
- Независимое масштабирование сервисов
- Разные порты позволяют гибкую маршрутизацию
- ThreadPoolExecutor для управления concurrency

### ✅ Maintainability
- Dependency injection упрощает тестирование
- DDD обеспечивает чистую архитектуру
- Комплексная обработка ошибок

### ✅ Performance
- Асинхронная обработка всех запросов
- Оптимизированные gRPC настройки
- Transaction management предотвращает deadlocks

---

## Производственные Аспекты

### Deployment
```yaml
# docker-compose.yaml
simulation_service:
  ports:
    - "50051:50051"  # SimulationService
    - "50052:50052"  # DatabaseManager
  healthcheck:
    test: ["CMD", "python", "-c", "import grpc; channel = grpc.insecure_channel('localhost:50051'); print('gRPC server is running')"]
```

### Monitoring
- Детальное логирование всех операций
- Health checks для каждого сервиса
- Transaction monitoring через session management

### Security
- Insecure channels (для development)
- Ready for TLS через grpc.ssl_channel_credentials()
- Authentication через metadata (room-id)

---

## Best Practices для Клиентской Библиотеки

### 1. Resource Management
```python
# Всегда используйте context managers для каналов
async with grpc.aio.insecure_channel(endpoint) as channel:
    stub = SimulationServiceStub(channel)
    # ваш код здесь
```

### 2. Error Handling Strategy
```python
# Определяйте expected errors и обрабатывайте их специфично
RETRYABLE_ERRORS = {StatusCode.UNAVAILABLE, StatusCode.DEADLINE_EXCEEDED}
CLIENT_ERRORS = {StatusCode.INVALID_ARGUMENT, StatusCode.NOT_FOUND}
SERVER_ERRORS = {StatusCode.INTERNAL, StatusCode.UNKNOWN}

def should_retry(error: RpcError) -> bool:
    return error.code() in RETRYABLE_ERRORS

def is_client_error(error: RpcError) -> bool:
    return error.code() in CLIENT_ERRORS
```

### 3. Connection Resilience
```python
class ResilientChannel:
    def __init__(self, endpoint: str, max_retries: int = 3):
        self.endpoint = endpoint
        self.max_retries = max_retries
        self._channel = None

    async def get_channel(self) -> grpc.aio.Channel:
        if self._channel is None:
            self._channel = await self._create_channel_with_retry()
        return self._channel

    async def _create_channel_with_retry(self) -> grpc.aio.Channel:
        for attempt in range(self.max_retries):
            try:
                channel = grpc.aio.insecure_channel(self.endpoint)
                # Test connection
                await channel.channel_ready()
                return channel
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

### 4. Request/Response Transformation
```python
# Создавайте удобные wrapper'ы для сложных запросов
def create_supplier_request(data: Dict[str, Any]) -> CreateSupplierRequest:
    """Transform dict to protobuf request with validation"""
    # Валидация данных
    if not data.get('name'):
        raise ValueError("Supplier name is required")

    # Преобразование типов если нужно
    if 'reliability' in data:
        data['reliability'] = float(data['reliability'])

    return CreateSupplierRequest(**data)

def supplier_to_dict(supplier: Supplier) -> Dict[str, Any]:
    """Transform protobuf response to dict"""
    return {
        'supplier_id': supplier.supplier_id,
        'name': supplier.name,
        'product_name': supplier.product_name,
        'material_type': supplier.material_type,
        'delivery_period': supplier.delivery_period,
        'reliability': supplier.reliability,
        'product_quality': supplier.product_quality,
        'cost': supplier.cost,
        'special_delivery_period': supplier.special_delivery_period,
        'special_delivery_cost': supplier.special_delivery_cost,
    }
```

### 5. Pagination Support (для будущих расширений)
```python
@dataclass
class PaginationParams:
    page: int = 1
    page_size: int = 50
    sort_by: Optional[str] = None
    sort_order: str = "asc"

async def get_all_with_pagination(
    self,
    request_factory,
    response_processor,
    pagination: PaginationParams
) -> List[Any]:
    """Generic pagination handler"""
    # Для будущих версий API с пагинацией
    all_items = []

    while True:
        request = request_factory(pagination)
        response = await self.stub.get_all_entities(request)

        items = response_processor(response)
        all_items.extend(items)

        # Проверка на наличие следующей страницы
        if len(items) < pagination.page_size:
            break

        pagination.page += 1

    return all_items
```

### 6. Version Compatibility
```python
# Управление версиями API
API_VERSIONS = {
    "v1": {
        "simulation_service": "50051",
        "db_service": "50052"
    }
}

class VersionedClient:
    def __init__(self, api_version: str = "v1"):
        if api_version not in API_VERSIONS:
            raise ValueError(f"Unsupported API version: {api_version}")

        self.version_config = API_VERSIONS[api_version]
        # Инициализация клиентов с учетом версии
```

### 7. Testing Support
```python
# Mock clients для тестирования
class MockSimulationStub:
    async def create_simulation(self, request):
        return SimulationResponse(
            simulations=Simulation(simulation_id="mock-sim-123"),
            timestamp=datetime.now().isoformat()
        )

    async def get_simulation(self, request):
        if request.simulation_id == "non-existent":
            raise RpcError("Simulation not found")
        return SimulationResponse(
            simulations=Simulation(simulation_id=request.simulation_id),
            timestamp=datetime.now().isoformat()
        )

# Использование в тестах
@pytest.fixture
async def mock_client():
    channel = MockChannel()
    stub = MockSimulationStub()
    client = SimulationServiceClient()
    client.stub = stub
    return client
```

---

## Migration Guide

### Для существующих клиентов
```python
# Старый код
import grpc
channel = grpc.insecure_channel('localhost:50051')
stub = SimulationServiceStub(channel)

# Новый код с клиентской библиотекой
from simulation_client import SimulationClient

client = SimulationClient(host="localhost")
simulation_id = await client.create_and_run_simulation()
```

### Breaking Changes
1. **Async only**: Все методы теперь асинхронные
2. **Channel management**: Клиентская библиотека управляет жизненным циклом каналов
3. **Error types**: Специфичные исключения вместо голых RpcError
4. **Type hints**: Строгая типизация для всех параметров

### Compatibility Matrix
| Feature | v1.0 | Future Versions |
|---------|------|-----------------|
| Basic CRUD | ✅ | ✅ |
| Batch operations | ❌ | ✅ |
| Streaming | ❌ | ✅ |
| Pagination | ❌ | ✅ |
| Circuit breaker | ❌ | ✅ |

---

## Заключение

Эта документация предоставляет полное руководство для разработки клиентской библиотеки gRPC сервисов промышленного симулятора. Реализация демонстрирует enterprise-grade подход с:

- **Чистой архитектурой** через DDD и separation of concerns
- **Масштабируемостью** через microservices и connection pooling
- **Надежностью** через comprehensive error handling и retry policies
- **Производительностью** через async processing и optimized gRPC settings
- **Удобством использования** через высокоуровневые клиентские классы и typed exceptions

Двухсервисная архитектура позволяет гибко масштабировать разные аспекты системы независимо, в то время как единая клиентская библиотека упрощает интеграцию и поддержку.
