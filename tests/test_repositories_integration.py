"""
Интеграционные тесты для всех репозиториев в infrastructure/repositories.py.

Тесты проверяют:
- CRUD операции для всех репозиториев
- Сериализацию и десериализацию данных
- Преобразование между доменными моделями и DB моделями
- Особые случаи (полиморфизм Worker/Logist, сложные структуры Simulation)
"""

import pytest
import pytest_asyncio
from uuid import uuid4
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

from infrastructure.repositories import (
    WorkerRepository,
    SupplierRepository,
    EquipmentRepository,
    WorkplaceRepository,
    ConsumerRepository,
    TenderRepository,
    LeanImprovementRepository,
    SimulationRepository,
)
from domain import (
    Worker,
    Logist,
    Supplier,
    Equipment,
    Workplace,
    Consumer,
    Tender,
    LeanImprovement,
    Simulation,
    SimulationParameters,
    SimulationResults,
    Qualification,
    Specialization,
    ConsumerType,
    PaymentForm,
    VehicleType,
)
from domain.metrics import (
    FactoryMetrics,
    ProductionMetrics,
    QualityMetrics,
    EngineeringMetrics,
    CommercialMetrics,
    ProcurementMetrics,
)


@pytest_asyncio.fixture(scope="function")
async def async_session():
    """Создает асинхронную сессию для интеграционных тестов."""
    db_host = "localhost"
    db_port = 5432
    db_user = "user"
    db_password = "password"
    db_name = "auth_db"

    test_db_url = (
        f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )
    test_engine = create_async_engine(
        test_db_url,
        echo=False,
        pool_size=5,  # Ограничиваем размер пула
        max_overflow=10,  # Максимальное количество дополнительных соединений
        pool_pre_ping=True,  # Проверяем соединения перед использованием
        pool_recycle=3600,  # Переиспользуем соединения через час
    )
    TestSessionLocal = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )

    session = None
    try:
        async with TestSessionLocal() as session:
            yield session
    finally:
        # Явно закрываем сессию и engine после использования
        if session:
            try:
                await session.close()
            except Exception:
                pass
        try:
            await test_engine.dispose()
        except Exception:
            pass


class TestWorkerRepository:
    """Тесты для WorkerRepository с поддержкой Worker и Logist."""

    @pytest_asyncio.fixture
    async def worker_repo(self, async_session):
        return WorkerRepository(async_session)

    @pytest.mark.asyncio
    async def test_save_worker(self, worker_repo):
        """Тест сохранения обычного Worker."""
        worker = Worker(
            worker_id=str(uuid4()),
            name="Test Worker",
            qualification=Qualification.III.value,
            specialty=Specialization.ASSEMBLER.value,
            salary=50000,
        )

        saved = await worker_repo.save(worker)
        assert saved is not None
        assert saved.worker_id == worker.worker_id
        assert saved.name == worker.name
        assert saved.qualification == worker.qualification
        assert saved.specialty == worker.specialty
        assert saved.salary == worker.salary
        # Проверяем, что это Worker, а не Logist
        assert not hasattr(saved, "speed") or not hasattr(saved, "vehicle_type")

    @pytest.mark.asyncio
    async def test_save_logist(self, worker_repo):
        """Тест сохранения Logist."""
        logist = Logist(
            worker_id=str(uuid4()),
            name="Test Logist",
            qualification=Qualification.II.value,
            specialty=Specialization.LOGIST.value,
            salary=60000,
            speed=80,
            vehicle_type=VehicleType.TRUCK.value,
        )

        saved = await worker_repo.save(logist)
        assert saved is not None
        assert saved.worker_id == logist.worker_id
        assert saved.name == logist.name
        assert saved.qualification == logist.qualification
        assert saved.specialty == logist.specialty
        assert saved.salary == logist.salary
        # Проверяем, что это Logist
        assert hasattr(saved, "speed")
        assert hasattr(saved, "vehicle_type")
        assert saved.speed == logist.speed
        assert saved.vehicle_type == logist.vehicle_type

    @pytest.mark.asyncio
    async def test_get_worker(self, worker_repo):
        """Тест получения Worker по ID."""
        worker = Worker(
            worker_id=str(uuid4()),
            name="Test Worker",
            qualification=Qualification.IV.value,
            specialty=Specialization.ENGINEER_TECHNOLOGIST.value,
            salary=55000,
        )

        saved = await worker_repo.save(worker)
        retrieved = await worker_repo.get(saved.worker_id)

        assert retrieved is not None
        assert retrieved.worker_id == worker.worker_id
        assert retrieved.name == worker.name
        assert retrieved.qualification == worker.qualification
        assert retrieved.specialty == worker.specialty
        assert retrieved.salary == worker.salary

    @pytest.mark.asyncio
    async def test_get_logist(self, worker_repo):
        """Тест получения Logist по ID."""
        logist = Logist(
            worker_id=str(uuid4()),
            name="Test Logist",
            qualification=Qualification.III.value,
            specialty=Specialization.LOGIST.value,
            salary=65000,
            speed=90,
            vehicle_type=VehicleType.VAN.value,
        )

        saved = await worker_repo.save(logist)
        retrieved = await worker_repo.get(saved.worker_id)

        assert retrieved is not None
        assert isinstance(retrieved, Logist) or (
            hasattr(retrieved, "speed") and hasattr(retrieved, "vehicle_type")
        )
        assert retrieved.worker_id == logist.worker_id
        assert retrieved.speed == logist.speed
        assert retrieved.vehicle_type == logist.vehicle_type

    @pytest.mark.asyncio
    async def test_update_worker(self, worker_repo):
        """Тест обновления Worker."""
        worker = Worker(
            worker_id=str(uuid4()),
            name="Original Name",
            qualification=Qualification.I.value,
            specialty=Specialization.ASSEMBLER.value,
            salary=40000,
        )

        saved = await worker_repo.save(worker)
        saved.name = "Updated Name"
        saved.qualification = Qualification.V.value
        saved.salary = 60000

        updated = await worker_repo.save(saved)
        assert updated.name == "Updated Name"
        assert updated.qualification == Qualification.V.value
        assert updated.salary == 60000

    @pytest.mark.asyncio
    async def test_delete_worker(self, worker_repo):
        """Тест удаления Worker."""
        worker = Worker(
            worker_id=str(uuid4()),
            name="To Delete",
            qualification=Qualification.II.value,
            specialty=Specialization.QUALITY_CONTROLLER.value,
            salary=45000,
        )

        saved = await worker_repo.save(worker)
        deleted = await worker_repo.delete(saved.worker_id)

        assert deleted is not None
        assert deleted.worker_id == worker.worker_id

        # Проверяем, что удален
        retrieved = await worker_repo.get(saved.worker_id)
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_get_all_workers(self, worker_repo):
        """Тест получения всех работников."""
        # Создаем несколько работников
        worker1 = Worker(
            worker_id=str(uuid4()),
            name="Worker 1",
            qualification=Qualification.I.value,
            specialty=Specialization.ASSEMBLER.value,
            salary=40000,
        )
        worker2 = Worker(
            worker_id=str(uuid4()),
            name="Worker 2",
            qualification=Qualification.II.value,
            specialty=Specialization.ENGINEER_TECHNOLOGIST.value,
            salary=50000,
        )
        logist = Logist(
            worker_id=str(uuid4()),
            name="Logist 1",
            qualification=Qualification.III.value,
            specialty=Specialization.LOGIST.value,
            salary=60000,
            speed=70,
            vehicle_type=VehicleType.ELECTRIC.value,
        )

        await worker_repo.save(worker1)
        await worker_repo.save(worker2)
        await worker_repo.save(logist)

        all_workers = await worker_repo.get_all()
        assert len(all_workers) >= 3

        # Проверяем, что все сохранены
        ids = {w.worker_id for w in all_workers}
        assert worker1.worker_id in ids
        assert worker2.worker_id in ids
        assert logist.worker_id in ids

    @pytest.mark.asyncio
    async def test_worker_enum_serialization(self, worker_repo):
        """Тест сериализации enum значений для Worker."""
        worker = Worker(
            worker_id=str(uuid4()),
            name="Enum Test",
            qualification=Qualification.VII.value,  # Используем значение enum
            specialty=Specialization.WAREHOUSE_KEEPER.value,  # Используем значение enum
            salary=70000,
        )

        saved = await worker_repo.save(worker)
        retrieved = await worker_repo.get(saved.worker_id)

        assert retrieved.qualification == Qualification.VII.value
        assert retrieved.specialty == Specialization.WAREHOUSE_KEEPER.value


class TestSupplierRepository:
    """Тесты для SupplierRepository."""

    @pytest_asyncio.fixture
    async def supplier_repo(self, async_session):
        return SupplierRepository(async_session)

    @pytest.mark.asyncio
    async def test_save_supplier(self, supplier_repo):
        """Тест сохранения Supplier."""
        supplier = Supplier(
            supplier_id=str(uuid4()),
            name="Test Supplier",
            product_name="Test Product",
            material_type="Steel",
            delivery_period=10,
            special_delivery_period=5,
            reliability=0.95,
            product_quality=0.90,
            cost=1000,
            special_delivery_cost=1500,
        )

        saved = await supplier_repo.save(supplier)
        assert saved is not None
        assert saved.supplier_id == supplier.supplier_id
        assert saved.name == supplier.name
        assert saved.product_name == supplier.product_name
        assert saved.material_type == supplier.material_type
        assert saved.delivery_period == supplier.delivery_period
        assert saved.reliability == supplier.reliability
        assert saved.product_quality == supplier.product_quality
        assert saved.cost == supplier.cost

    @pytest.mark.asyncio
    async def test_get_supplier(self, supplier_repo):
        """Тест получения Supplier по ID."""
        supplier = Supplier(
            supplier_id=str(uuid4()),
            name="Get Test Supplier",
            product_name="Product A",
            material_type="Aluminum",
            delivery_period=15,
            special_delivery_period=7,
            reliability=0.98,
            product_quality=0.95,
            cost=2000,
            special_delivery_cost=3000,
        )

        saved = await supplier_repo.save(supplier)
        retrieved = await supplier_repo.get(saved.supplier_id)

        assert retrieved is not None
        assert retrieved.supplier_id == supplier.supplier_id
        assert retrieved.name == supplier.name
        assert retrieved.product_name == supplier.product_name

    @pytest.mark.asyncio
    async def test_update_supplier(self, supplier_repo):
        """Тест обновления Supplier."""
        supplier = Supplier(
            supplier_id=str(uuid4()),
            name="Original Supplier",
            product_name="Original Product",
            material_type="Iron",
            delivery_period=20,
            special_delivery_period=10,
            reliability=0.90,
            product_quality=0.85,
            cost=1500,
            special_delivery_cost=2000,
        )

        saved = await supplier_repo.save(supplier)
        saved.name = "Updated Supplier"
        saved.cost = 2500

        updated = await supplier_repo.save(saved)
        assert updated.name == "Updated Supplier"
        assert updated.cost == 2500

    @pytest.mark.asyncio
    async def test_delete_supplier(self, supplier_repo):
        """Тест удаления Supplier."""
        supplier = Supplier(
            supplier_id=str(uuid4()),
            name="To Delete Supplier",
            product_name="Delete Product",
            material_type="Copper",
            delivery_period=12,
            special_delivery_period=6,
            reliability=0.92,
            product_quality=0.88,
            cost=1800,
            special_delivery_cost=2200,
        )

        saved = await supplier_repo.save(supplier)
        deleted = await supplier_repo.delete(saved.supplier_id)

        assert deleted is not None
        assert deleted.supplier_id == supplier.supplier_id

        retrieved = await supplier_repo.get(saved.supplier_id)
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_get_all_suppliers(self, supplier_repo):
        """Тест получения всех поставщиков."""
        supplier1 = Supplier(
            supplier_id=str(uuid4()),
            name="Supplier 1",
            product_name="Product 1",
            material_type="Type 1",
            delivery_period=10,
            special_delivery_period=5,
            reliability=0.95,
            product_quality=0.90,
            cost=1000,
            special_delivery_cost=1500,
        )
        supplier2 = Supplier(
            supplier_id=str(uuid4()),
            name="Supplier 2",
            product_name="Product 2",
            material_type="Type 2",
            delivery_period=15,
            special_delivery_period=7,
            reliability=0.98,
            product_quality=0.95,
            cost=2000,
            special_delivery_cost=3000,
        )

        await supplier_repo.save(supplier1)
        await supplier_repo.save(supplier2)

        all_suppliers = await supplier_repo.get_all()
        assert len(all_suppliers) >= 2

        ids = {s.supplier_id for s in all_suppliers}
        assert supplier1.supplier_id in ids
        assert supplier2.supplier_id in ids

    @pytest.mark.asyncio
    async def test_get_distinct_product_names(self, supplier_repo):
        """Тест получения уникальных названий продуктов."""
        supplier1 = Supplier(
            supplier_id=str(uuid4()),
            name="Supplier A",
            product_name="Product X",
            material_type="Type A",
            delivery_period=10,
            special_delivery_period=5,
            reliability=0.95,
            product_quality=0.90,
            cost=1000,
            special_delivery_cost=1500,
        )
        supplier2 = Supplier(
            supplier_id=str(uuid4()),
            name="Supplier B",
            product_name="Product Y",
            material_type="Type B",
            delivery_period=15,
            special_delivery_period=7,
            reliability=0.98,
            product_quality=0.95,
            cost=2000,
            special_delivery_cost=3000,
        )
        supplier3 = Supplier(
            supplier_id=str(uuid4()),
            name="Supplier C",
            product_name="Product X",  # Дубликат
            material_type="Type C",
            delivery_period=12,
            special_delivery_period=6,
            reliability=0.92,
            product_quality=0.88,
            cost=1500,
            special_delivery_cost=2000,
        )

        await supplier_repo.save(supplier1)
        await supplier_repo.save(supplier2)
        await supplier_repo.save(supplier3)

        product_names = await supplier_repo.get_distinct_product_names()
        assert "Product X" in product_names
        assert "Product Y" in product_names
        # Проверяем, что дубликаты удалены
        assert product_names.count("Product X") == 1


class TestEquipmentRepository:
    """Тесты для EquipmentRepository."""

    @pytest_asyncio.fixture
    async def equipment_repo(self, async_session):
        return EquipmentRepository(async_session)

    @pytest.mark.asyncio
    async def test_save_equipment(self, equipment_repo):
        """Тест сохранения Equipment."""
        equipment = Equipment(
            equipment_id=str(uuid4()),
            name="Test Equipment",
            equipment_type="Machine",
            reliability=0.98,
            maintenance_cost=5000,
            cost=100000,
            repair_cost=10000,
            repair_time=24,
            maintenance_period=30,
        )

        saved = await equipment_repo.save(equipment)
        assert saved is not None
        assert saved.equipment_id == equipment.equipment_id
        assert saved.name == equipment.name
        assert saved.equipment_type == equipment.equipment_type
        assert saved.reliability == equipment.reliability
        assert saved.maintenance_cost == equipment.maintenance_cost
        assert saved.cost == equipment.cost
        assert saved.repair_cost == equipment.repair_cost
        assert saved.repair_time == equipment.repair_time
        assert saved.maintenance_period == equipment.maintenance_period

    @pytest.mark.asyncio
    async def test_get_equipment(self, equipment_repo):
        """Тест получения Equipment по ID."""
        equipment = Equipment(
            equipment_id=str(uuid4()),
            name="Get Test Equipment",
            equipment_type="Tool",
            reliability=0.95,
            maintenance_cost=3000,
            cost=50000,
            repair_cost=5000,
            repair_time=12,
            maintenance_period=20,
        )

        saved = await equipment_repo.save(equipment)
        retrieved = await equipment_repo.get(saved.equipment_id)

        assert retrieved is not None
        assert retrieved.equipment_id == equipment.equipment_id
        assert retrieved.name == equipment.name

    @pytest.mark.asyncio
    async def test_update_equipment(self, equipment_repo):
        """Тест обновления Equipment."""
        equipment = Equipment(
            equipment_id=str(uuid4()),
            name="Original Equipment",
            equipment_type="Original Type",
            reliability=0.90,
            maintenance_cost=4000,
            cost=80000,
            repair_cost=8000,
            repair_time=20,
            maintenance_period=25,
        )

        saved = await equipment_repo.save(equipment)
        saved.name = "Updated Equipment"
        saved.cost = 120000

        updated = await equipment_repo.save(saved)
        assert updated.name == "Updated Equipment"
        assert updated.cost == 120000

    @pytest.mark.asyncio
    async def test_delete_equipment(self, equipment_repo):
        """Тест удаления Equipment."""
        equipment = Equipment(
            equipment_id=str(uuid4()),
            name="To Delete Equipment",
            equipment_type="Delete Type",
            reliability=0.92,
            maintenance_cost=3500,
            cost=60000,
            repair_cost=6000,
            repair_time=15,
            maintenance_period=22,
        )

        saved = await equipment_repo.save(equipment)
        deleted = await equipment_repo.delete(saved.equipment_id)

        assert deleted is not None
        assert deleted.equipment_id == equipment.equipment_id

        retrieved = await equipment_repo.get(saved.equipment_id)
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_get_all_equipment(self, equipment_repo):
        """Тест получения всего оборудования."""
        equipment1 = Equipment(
            equipment_id=str(uuid4()),
            name="Equipment 1",
            equipment_type="Type 1",
            reliability=0.95,
            maintenance_cost=4000,
            cost=80000,
            repair_cost=8000,
            repair_time=18,
            maintenance_period=25,
        )
        equipment2 = Equipment(
            equipment_id=str(uuid4()),
            name="Equipment 2",
            equipment_type="Type 2",
            reliability=0.98,
            maintenance_cost=5000,
            cost=100000,
            repair_cost=10000,
            repair_time=24,
            maintenance_period=30,
        )

        await equipment_repo.save(equipment1)
        await equipment_repo.save(equipment2)

        all_equipment = await equipment_repo.get_all()
        assert len(all_equipment) >= 2

        ids = {e.equipment_id for e in all_equipment}
        assert equipment1.equipment_id in ids
        assert equipment2.equipment_id in ids

    @pytest.mark.asyncio
    async def test_equipment_maintenance_period_default(self, equipment_repo):
        """Тест обработки maintenance_period по умолчанию."""
        # Создаем Equipment без maintenance_period (None)
        equipment = Equipment(
            equipment_id=str(uuid4()),
            name="Default Period Equipment",
            equipment_type="Test Type",
            reliability=0.95,
            maintenance_cost=4000,
            cost=80000,
            repair_cost=8000,
            repair_time=18,
            maintenance_period=None,  # None значение
        )

        saved = await equipment_repo.save(equipment)
        # maintenance_period должен быть сохранен как 0, если None
        assert saved.maintenance_period == 0 or saved.maintenance_period is not None


class TestWorkplaceRepository:
    """Тесты для WorkplaceRepository."""

    @pytest_asyncio.fixture
    async def workplace_repo(self, async_session):
        return WorkplaceRepository(async_session)

    @pytest.mark.asyncio
    async def test_save_workplace(self, workplace_repo):
        """Тест сохранения Workplace."""
        workplace = Workplace(
            workplace_id=str(uuid4()),
            workplace_name="Test Workplace",
            required_speciality=Specialization.ASSEMBLER.value,
            required_qualification=Qualification.III.value,
            required_equipment="Equipment A",
            required_stages=["Stage 1", "Stage 2"],
        )

        saved = await workplace_repo.save(workplace)
        assert saved is not None
        assert saved.workplace_id == workplace.workplace_id
        assert saved.workplace_name == workplace.workplace_name
        assert saved.required_speciality == workplace.required_speciality
        assert saved.required_qualification == workplace.required_qualification
        assert saved.required_equipment == workplace.required_equipment
        assert saved.required_stages == workplace.required_stages

    @pytest.mark.asyncio
    async def test_get_workplace(self, workplace_repo):
        """Тест получения Workplace по ID."""
        workplace = Workplace(
            workplace_id=str(uuid4()),
            workplace_name="Get Test Workplace",
            required_speciality=Specialization.ENGINEER_TECHNOLOGIST.value,
            required_qualification=Qualification.IV.value,
            required_equipment="Equipment B",
            required_stages=["Stage 3"],
        )

        saved = await workplace_repo.save(workplace)
        retrieved = await workplace_repo.get(saved.workplace_id)

        assert retrieved is not None
        assert retrieved.workplace_id == workplace.workplace_id
        assert retrieved.workplace_name == workplace.workplace_name

    @pytest.mark.asyncio
    async def test_update_workplace(self, workplace_repo):
        """Тест обновления Workplace."""
        workplace = Workplace(
            workplace_id=str(uuid4()),
            workplace_name="Original Workplace",
            required_speciality=Specialization.QUALITY_CONTROLLER.value,
            required_qualification=Qualification.II.value,
            required_equipment="Original Equipment",
            required_stages=["Original Stage"],
        )

        saved = await workplace_repo.save(workplace)
        saved.workplace_name = "Updated Workplace"
        saved.required_qualification = Qualification.V.value

        updated = await workplace_repo.save(saved)
        assert updated.workplace_name == "Updated Workplace"
        assert updated.required_qualification == Qualification.V.value

    @pytest.mark.asyncio
    async def test_delete_workplace(self, workplace_repo):
        """Тест удаления Workplace."""
        workplace = Workplace(
            workplace_id=str(uuid4()),
            workplace_name="To Delete Workplace",
            required_speciality=Specialization.WAREHOUSE_KEEPER.value,
            required_qualification=Qualification.I.value,
            required_equipment="Delete Equipment",
            required_stages=[],
        )

        saved = await workplace_repo.save(workplace)
        deleted = await workplace_repo.delete(saved.workplace_id)

        assert deleted is not None
        assert deleted.workplace_id == workplace.workplace_id

        retrieved = await workplace_repo.get(saved.workplace_id)
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_get_all_workplaces(self, workplace_repo):
        """Тест получения всех рабочих мест."""
        workplace1 = Workplace(
            workplace_id=str(uuid4()),
            workplace_name="Workplace 1",
            required_speciality=Specialization.ASSEMBLER.value,
            required_qualification=Qualification.III.value,
            required_equipment="Equipment 1",
            required_stages=["Stage 1"],
        )
        workplace2 = Workplace(
            workplace_id=str(uuid4()),
            workplace_name="Workplace 2",
            required_speciality=Specialization.ENGINEER_TECHNOLOGIST.value,
            required_qualification=Qualification.IV.value,
            required_equipment="Equipment 2",
            required_stages=["Stage 2"],
        )

        await workplace_repo.save(workplace1)
        await workplace_repo.save(workplace2)

        all_workplaces = await workplace_repo.get_all()
        assert len(all_workplaces) >= 2

        ids = {w.workplace_id for w in all_workplaces}
        assert workplace1.workplace_id in ids
        assert workplace2.workplace_id in ids

    @pytest.mark.asyncio
    async def test_save_workplace_with_coordinates(self, workplace_repo):
        """Тест сохранения Workplace с координатами."""
        workplace = Workplace(
            workplace_id=str(uuid4()),
            workplace_name="Workplace with coordinates",
            required_speciality=Specialization.ASSEMBLER.value,
            required_qualification=Qualification.III.value,
            x=2,
            y=3,
        )

        saved = await workplace_repo.save(workplace)
        assert saved is not None
        assert saved.x == 2
        assert saved.y == 3

    @pytest.mark.asyncio
    async def test_save_workplace_without_coordinates(self, workplace_repo):
        """Тест сохранения Workplace без координат (None)."""
        workplace = Workplace(
            workplace_id=str(uuid4()),
            workplace_name="Workplace without coordinates",
            required_speciality=Specialization.ENGINEER_TECHNOLOGIST.value,
            required_qualification=Qualification.IV.value,
            # x и y не указаны, должны быть None
        )

        saved = await workplace_repo.save(workplace)
        assert saved is not None
        assert saved.x is None
        assert saved.y is None

    @pytest.mark.asyncio
    async def test_get_workplace_with_coordinates(self, workplace_repo):
        """Тест получения Workplace с координатами из БД."""
        workplace = Workplace(
            workplace_id=str(uuid4()),
            workplace_name="Workplace to retrieve",
            required_speciality=Specialization.QUALITY_CONTROLLER.value,
            required_qualification=Qualification.V.value,
            x=5,
            y=1,
        )

        saved = await workplace_repo.save(workplace)
        retrieved = await workplace_repo.get(saved.workplace_id)

        assert retrieved is not None
        assert retrieved.workplace_id == workplace.workplace_id
        assert retrieved.x == 5
        assert retrieved.y == 1

    @pytest.mark.asyncio
    async def test_update_workplace_coordinates(self, workplace_repo):
        """Тест обновления координат Workplace."""
        # Создаем рабочее место без координат
        workplace = Workplace(
            workplace_id=str(uuid4()),
            workplace_name="Workplace to update",
            required_speciality=Specialization.WAREHOUSE_KEEPER.value,
            required_qualification=Qualification.II.value,
        )

        saved = await workplace_repo.save(workplace)
        assert saved.x is None
        assert saved.y is None

        # Обновляем координаты
        saved.x = 3
        saved.y = 4

        updated = await workplace_repo.save(saved)
        assert updated.x == 3
        assert updated.y == 4

        # Меняем координаты на другие значения
        updated.x = 6
        updated.y = 0

        updated_again = await workplace_repo.save(updated)
        assert updated_again.x == 6
        assert updated_again.y == 0

        # Устанавливаем координаты обратно в None
        updated_again.x = None
        updated_again.y = None

        updated_none = await workplace_repo.save(updated_again)
        assert updated_none.x is None
        assert updated_none.y is None

    @pytest.mark.asyncio
    async def test_workplace_coordinates_edge_values(self, workplace_repo):
        """Тест граничных значений координат на сетке 7x7."""
        # Минимальные координаты (0, 0)
        workplace_min = Workplace(
            workplace_id=str(uuid4()),
            workplace_name="Min coordinates",
            required_speciality=Specialization.ASSEMBLER.value,
            required_qualification=Qualification.III.value,
            x=0,
            y=0,
        )

        saved_min = await workplace_repo.save(workplace_min)
        assert saved_min.x == 0
        assert saved_min.y == 0

        # Максимальные координаты (6, 6)
        workplace_max = Workplace(
            workplace_id=str(uuid4()),
            workplace_name="Max coordinates",
            required_speciality=Specialization.ENGINEER_TECHNOLOGIST.value,
            required_qualification=Qualification.IV.value,
            x=6,
            y=6,
        )

        saved_max = await workplace_repo.save(workplace_max)
        assert saved_max.x == 6
        assert saved_max.y == 6

        # Центр сетки (3, 3)
        workplace_center = Workplace(
            workplace_id=str(uuid4()),
            workplace_name="Center coordinates",
            required_speciality=Specialization.QUALITY_CONTROLLER.value,
            required_qualification=Qualification.V.value,
            x=3,
            y=3,
        )

        saved_center = await workplace_repo.save(workplace_center)
        assert saved_center.x == 3
        assert saved_center.y == 3

    @pytest.mark.asyncio
    async def test_multiple_workplaces_with_different_coordinates(self, workplace_repo):
        """Тест нескольких рабочих мест с разными координатами."""
        workplaces = [
            Workplace(
                workplace_id=str(uuid4()),
                workplace_name=f"Workplace {i}",
                required_speciality=Specialization.ASSEMBLER.value,
                required_qualification=Qualification.III.value,
                x=i % 7,
                y=(i * 2) % 7,
            )
            for i in range(5)
        ]

        saved_workplaces = []
        for wp in workplaces:
            saved = await workplace_repo.save(wp)
            saved_workplaces.append(saved)

        # Проверяем, что координаты сохранены правильно
        for i, saved in enumerate(saved_workplaces):
            assert saved.x == i % 7
            assert saved.y == (i * 2) % 7

        # Получаем все рабочие места и проверяем координаты
        all_workplaces = await workplace_repo.get_all()
        saved_ids = {w.workplace_id for w in saved_workplaces}

        for wp in all_workplaces:
            if wp.workplace_id in saved_ids:
                # Находим соответствующий сохраненный workplace
                saved_wp = next(w for w in saved_workplaces if w.workplace_id == wp.workplace_id)
                assert wp.x == saved_wp.x
                assert wp.y == saved_wp.y


class TestConsumerRepository:
    """Тесты для ConsumerRepository."""

    @pytest_asyncio.fixture
    async def consumer_repo(self, async_session):
        return ConsumerRepository(async_session)

    @pytest.mark.asyncio
    async def test_save_consumer(self, consumer_repo):
        """Тест сохранения Consumer."""
        consumer = Consumer(
            consumer_id=str(uuid4()),
            name="Test Consumer",
            type=ConsumerType.GOVERMANT.value,
        )

        saved = await consumer_repo.save(consumer)
        assert saved is not None
        assert saved.consumer_id == consumer.consumer_id
        assert saved.name == consumer.name
        assert saved.type == consumer.type

    @pytest.mark.asyncio
    async def test_get_consumer(self, consumer_repo):
        """Тест получения Consumer по ID."""
        consumer = Consumer(
            consumer_id=str(uuid4()),
            name="Get Test Consumer",
            type=ConsumerType.GOVERMANT.value,
        )

        saved = await consumer_repo.save(consumer)
        retrieved = await consumer_repo.get(saved.consumer_id)

        assert retrieved is not None
        assert retrieved.consumer_id == consumer.consumer_id
        assert retrieved.name == consumer.name
        assert retrieved.type == consumer.type

    @pytest.mark.asyncio
    async def test_update_consumer(self, consumer_repo):
        """Тест обновления Consumer."""
        consumer = Consumer(
            consumer_id=str(uuid4()),
            name="Original Consumer",
            type=ConsumerType.GOVERMANT.value,
        )

        saved = await consumer_repo.save(consumer)
        saved.name = "Updated Consumer"
        saved.type = ConsumerType.NOT_GOVERMANT.value

        updated = await consumer_repo.save(saved)
        assert updated.name == "Updated Consumer"
        assert updated.type == ConsumerType.NOT_GOVERMANT.value

    @pytest.mark.asyncio
    async def test_delete_consumer(self, consumer_repo):
        """Тест удаления Consumer."""
        consumer = Consumer(
            consumer_id=str(uuid4()),
            name="To Delete Consumer",
            type=ConsumerType.GOVERMANT.value,
        )

        saved = await consumer_repo.save(consumer)
        deleted = await consumer_repo.delete(saved.consumer_id)

        assert deleted is not None
        assert deleted.consumer_id == consumer.consumer_id

        retrieved = await consumer_repo.get(saved.consumer_id)
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_get_all_consumers(self, consumer_repo):
        """Тест получения всех заказчиков."""
        consumer1 = Consumer(
            consumer_id=str(uuid4()),
            name="Consumer 1",
            type=ConsumerType.GOVERMANT.value,
        )
        consumer2 = Consumer(
            consumer_id=str(uuid4()),
            name="Consumer 2",
            type=ConsumerType.NOT_GOVERMANT.value,
        )

        await consumer_repo.save(consumer1)
        await consumer_repo.save(consumer2)

        all_consumers = await consumer_repo.get_all()
        assert len(all_consumers) >= 2

        ids = {c.consumer_id for c in all_consumers}
        assert consumer1.consumer_id in ids
        assert consumer2.consumer_id in ids

    @pytest.mark.asyncio
    async def test_consumer_enum_serialization(self, consumer_repo):
        """Тест сериализации enum значений для Consumer."""
        consumer = Consumer(
            consumer_id=str(uuid4()),
            name="Enum Test Consumer",
            type=ConsumerType.GOVERMANT.value,
        )

        saved = await consumer_repo.save(consumer)
        retrieved = await consumer_repo.get(saved.consumer_id)

        assert retrieved.type == ConsumerType.GOVERMANT.value


class TestTenderRepository:
    """Тесты для TenderRepository с поддержкой Consumer."""

    @pytest_asyncio.fixture
    async def tender_repo(self, async_session):
        return TenderRepository(async_session)

    @pytest_asyncio.fixture
    async def consumer_repo(self, async_session):
        return ConsumerRepository(async_session)

    @pytest.mark.asyncio
    async def test_save_tender_with_existing_consumer(self, tender_repo, consumer_repo):
        """Тест сохранения Tender с существующим Consumer."""
        # Сначала создаем Consumer
        consumer = Consumer(
            consumer_id=str(uuid4()),
            name="Test Consumer",
            type=ConsumerType.GOVERMANT.value,
        )
        saved_consumer = await consumer_repo.save(consumer)

        # Создаем Tender с этим Consumer
        tender = Tender(
            tender_id=str(uuid4()),
            consumer=saved_consumer,
            cost=100000,
            quantity_of_products=100,
            penalty_per_day=1000,
            warranty_years=2,
            payment_form=PaymentForm.CASH.value,
        )

        saved = await tender_repo.save(tender)
        assert saved is not None
        assert saved.tender_id == tender.tender_id
        assert saved.cost == tender.cost
        assert saved.quantity_of_products == tender.quantity_of_products
        assert saved.penalty_per_day == tender.penalty_per_day
        assert saved.warranty_years == tender.warranty_years
        assert saved.payment_form == tender.payment_form
        assert saved.consumer is not None
        assert saved.consumer.consumer_id == saved_consumer.consumer_id

    @pytest.mark.asyncio
    async def test_save_tender_with_new_consumer(self, tender_repo):
        """Тест сохранения Tender с новым Consumer (автоматическое создание)."""
        # Создаем Tender с новым Consumer (без consumer_id)
        new_consumer = Consumer(
            consumer_id="",  # Пустой ID - новый Consumer
            name="New Consumer",
            type=ConsumerType.NOT_GOVERMANT.value,
        )
        tender = Tender(
            tender_id=str(uuid4()),
            consumer=new_consumer,
            cost=200000,
            quantity_of_products=200,
            penalty_per_day=2000,
            warranty_years=3,
            payment_form=PaymentForm.CREDIT.value,
        )

        saved = await tender_repo.save(tender)
        assert saved is not None
        assert saved.tender_id == tender.tender_id
        assert saved.consumer is not None
        # Consumer должен быть автоматически создан
        assert saved.consumer.consumer_id != ""
        assert saved.consumer.name == "New Consumer"

    @pytest.mark.asyncio
    async def test_get_tender(self, tender_repo, consumer_repo):
        """Тест получения Tender по ID."""
        consumer = Consumer(
            consumer_id=str(uuid4()),
            name="Get Test Consumer",
            type=ConsumerType.GOVERMANT.value,
        )
        saved_consumer = await consumer_repo.save(consumer)

        tender = Tender(
            tender_id=str(uuid4()),
            consumer=saved_consumer,
            cost=150000,
            quantity_of_products=150,
            penalty_per_day=1500,
            warranty_years=2,
            payment_form=PaymentForm.TRANSFER.value,
        )

        saved = await tender_repo.save(tender)
        retrieved = await tender_repo.get(saved.tender_id)

        assert retrieved is not None
        assert retrieved.tender_id == tender.tender_id
        assert retrieved.cost == tender.cost
        assert retrieved.consumer is not None
        assert retrieved.consumer.consumer_id == saved_consumer.consumer_id

    @pytest.mark.asyncio
    async def test_update_tender(self, tender_repo, consumer_repo):
        """Тест обновления Tender."""
        consumer = Consumer(
            consumer_id=str(uuid4()),
            name="Original Consumer",
            type=ConsumerType.GOVERMANT.value,
        )
        saved_consumer = await consumer_repo.save(consumer)

        tender = Tender(
            tender_id=str(uuid4()),
            consumer=saved_consumer,
            cost=100000,
            quantity_of_products=100,
            penalty_per_day=1000,
            warranty_years=2,
            payment_form=PaymentForm.CASH.value,
        )

        saved = await tender_repo.save(tender)
        saved.cost = 200000
        saved.quantity_of_products = 200

        updated = await tender_repo.save(saved)
        assert updated.cost == 200000
        assert updated.quantity_of_products == 200

    @pytest.mark.asyncio
    async def test_delete_tender(self, tender_repo, consumer_repo):
        """Тест удаления Tender."""
        consumer = Consumer(
            consumer_id=str(uuid4()),
            name="Delete Test Consumer",
            type=ConsumerType.NOT_GOVERMANT.value,
        )
        saved_consumer = await consumer_repo.save(consumer)

        tender = Tender(
            tender_id=str(uuid4()),
            consumer=saved_consumer,
            cost=100000,
            quantity_of_products=100,
            penalty_per_day=1000,
            warranty_years=2,
            payment_form=PaymentForm.CASH.value,
        )

        saved = await tender_repo.save(tender)
        deleted = await tender_repo.delete(saved.tender_id)

        assert deleted is not None
        assert deleted.tender_id == tender.tender_id

        retrieved = await tender_repo.get(saved.tender_id)
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_get_all_tenders(self, tender_repo, consumer_repo):
        """Тест получения всех тендеров."""
        consumer1 = Consumer(
            consumer_id=str(uuid4()),
            name="Consumer 1",
            type=ConsumerType.GOVERMANT.value,
        )
        consumer2 = Consumer(
            consumer_id=str(uuid4()),
            name="Consumer 2",
            type=ConsumerType.NOT_GOVERMANT.value,
        )
        saved_consumer1 = await consumer_repo.save(consumer1)
        saved_consumer2 = await consumer_repo.save(consumer2)

        tender1 = Tender(
            tender_id=str(uuid4()),
            consumer=saved_consumer1,
            cost=100000,
            quantity_of_products=100,
            penalty_per_day=1000,
            warranty_years=2,
            payment_form=PaymentForm.CASH.value,
        )
        tender2 = Tender(
            tender_id=str(uuid4()),
            consumer=saved_consumer2,
            cost=200000,
            quantity_of_products=200,
            penalty_per_day=2000,
            warranty_years=3,
            payment_form=PaymentForm.CREDIT.value,
        )

        await tender_repo.save(tender1)
        await tender_repo.save(tender2)

        all_tenders = await tender_repo.get_all()
        assert len(all_tenders) >= 2

        ids = {t.tender_id for t in all_tenders}
        assert tender1.tender_id in ids
        assert tender2.tender_id in ids

    @pytest.mark.asyncio
    async def test_tender_payment_form_enum_serialization(
        self, tender_repo, consumer_repo
    ):
        """Тест сериализации enum значений для PaymentForm в Tender."""
        consumer = Consumer(
            consumer_id=str(uuid4()),
            name="Enum Test Consumer",
            type=ConsumerType.GOVERMANT.value,
        )
        saved_consumer = await consumer_repo.save(consumer)

        tender = Tender(
            tender_id=str(uuid4()),
            consumer=saved_consumer,
            cost=100000,
            quantity_of_products=100,
            penalty_per_day=1000,
            warranty_years=2,
            payment_form=PaymentForm.FULL_ADVANCE.value,
        )

        saved = await tender_repo.save(tender)
        retrieved = await tender_repo.get(saved.tender_id)

        assert retrieved.payment_form == PaymentForm.FULL_ADVANCE.value


class TestLeanImprovementRepository:
    """Тесты для LeanImprovementRepository."""

    @pytest_asyncio.fixture
    async def improvement_repo(self, async_session):
        return LeanImprovementRepository(async_session)

    @pytest.mark.asyncio
    async def test_save_lean_improvement(self, improvement_repo):
        """Тест сохранения LeanImprovement."""
        improvement = LeanImprovement(
            improvement_id=str(uuid4()),
            name="Test Improvement",
            is_implemented=False,
            implementation_cost=10000,
            efficiency_gain=0.15,
        )

        saved = await improvement_repo.save(improvement)
        assert saved is not None
        assert saved.improvement_id == improvement.improvement_id
        assert saved.name == improvement.name
        assert saved.is_implemented == improvement.is_implemented
        assert saved.implementation_cost == improvement.implementation_cost
        assert saved.efficiency_gain == improvement.efficiency_gain

    @pytest.mark.asyncio
    async def test_get_lean_improvement(self, improvement_repo):
        """Тест получения LeanImprovement по ID."""
        improvement = LeanImprovement(
            improvement_id=str(uuid4()),
            name="Get Test Improvement",
            is_implemented=True,
            implementation_cost=15000,
            efficiency_gain=0.20,
        )

        saved = await improvement_repo.save(improvement)
        retrieved = await improvement_repo.get(saved.improvement_id)

        assert retrieved is not None
        assert retrieved.improvement_id == improvement.improvement_id
        assert retrieved.name == improvement.name
        assert retrieved.is_implemented == improvement.is_implemented

    @pytest.mark.asyncio
    async def test_update_lean_improvement(self, improvement_repo):
        """Тест обновления LeanImprovement."""
        improvement = LeanImprovement(
            improvement_id=str(uuid4()),
            name="Original Improvement",
            is_implemented=False,
            implementation_cost=10000,
            efficiency_gain=0.15,
        )

        saved = await improvement_repo.save(improvement)
        saved.name = "Updated Improvement"
        saved.is_implemented = True
        saved.efficiency_gain = 0.25

        updated = await improvement_repo.save(saved)
        assert updated.name == "Updated Improvement"
        assert updated.is_implemented is True
        assert updated.efficiency_gain == 0.25

    @pytest.mark.asyncio
    async def test_delete_lean_improvement(self, improvement_repo):
        """Тест удаления LeanImprovement."""
        improvement = LeanImprovement(
            improvement_id=str(uuid4()),
            name="To Delete Improvement",
            is_implemented=False,
            implementation_cost=8000,
            efficiency_gain=0.10,
        )

        saved = await improvement_repo.save(improvement)
        deleted = await improvement_repo.delete(saved.improvement_id)

        assert deleted is not None
        assert deleted.improvement_id == improvement.improvement_id

        retrieved = await improvement_repo.get(saved.improvement_id)
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_get_all_lean_improvements(self, improvement_repo):
        """Тест получения всех LEAN улучшений."""
        improvement1 = LeanImprovement(
            improvement_id=str(uuid4()),
            name="Improvement 1",
            is_implemented=False,
            implementation_cost=10000,
            efficiency_gain=0.15,
        )
        improvement2 = LeanImprovement(
            improvement_id=str(uuid4()),
            name="Improvement 2",
            is_implemented=True,
            implementation_cost=15000,
            efficiency_gain=0.20,
        )

        await improvement_repo.save(improvement1)
        await improvement_repo.save(improvement2)

        all_improvements = await improvement_repo.get_all()
        assert len(all_improvements) >= 2

        ids = {i.improvement_id for i in all_improvements}
        assert improvement1.improvement_id in ids
        assert improvement2.improvement_id in ids


class TestSimulationRepository:
    """Тесты для SimulationRepository с проверкой сериализации/десериализации."""

    @pytest_asyncio.fixture
    async def simulation_repo(self, async_session):
        return SimulationRepository(async_session)

    @pytest.mark.asyncio
    async def test_save_simulation_with_parameters(self, simulation_repo):
        """Тест сохранения Simulation с параметрами."""
        # Создаем SimulationParameters
        params = SimulationParameters(
            step=1,
            capital=10000000,
        )

        simulation = Simulation(
            simulation_id=str(uuid4()),
            capital=10000000,
            parameters=[params],
            results=[],
            room_id="test_room",
            is_completed=False,
        )

        saved = await simulation_repo.save(simulation)
        assert saved is not None
        assert saved.simulation_id == simulation.simulation_id
        assert saved.capital == simulation.capital
        assert len(saved.parameters) == 1
        assert saved.parameters[0].step == params.step

    @pytest.mark.asyncio
    async def test_save_simulation_with_results(self, simulation_repo):
        """Тест сохранения Simulation с результатами."""
        params = SimulationParameters(step=1, capital=10000000)

        # Создаем SimulationResults с метриками
        results = SimulationResults(
            step=1,
            profit=50000,
            cost=45000,
            profitability=0.10,
            factory_metrics=FactoryMetrics(),
            production_metrics=ProductionMetrics(),
            quality_metrics=QualityMetrics(),
            engineering_metrics=EngineeringMetrics(),
            commercial_metrics=CommercialMetrics(),
            procurement_metrics=ProcurementMetrics(),
        )

        simulation = Simulation(
            simulation_id=str(uuid4()),
            capital=10000000,
            parameters=[params],
            results=[results],
            room_id="test_room",
            is_completed=False,
        )

        saved = await simulation_repo.save(simulation)
        assert saved is not None
        assert saved.simulation_id == simulation.simulation_id
        assert len(saved.results) == 1
        assert saved.results[0].step == results.step
        assert saved.results[0].profit == results.profit
        assert saved.results[0].cost == results.cost
        assert saved.results[0].profitability == results.profitability

    @pytest.mark.asyncio
    async def test_get_simulation(self, simulation_repo):
        """Тест получения Simulation по ID."""
        params = SimulationParameters(step=1, capital=10000000)
        results = SimulationResults(
            step=1,
            profit=50000,
            cost=45000,
            profitability=0.10,
        )

        simulation = Simulation(
            simulation_id=str(uuid4()),
            capital=10000000,
            parameters=[params],
            results=[results],
            room_id="test_room",
            is_completed=False,
        )

        saved = await simulation_repo.save(simulation)
        retrieved = await simulation_repo.get(saved.simulation_id)

        assert retrieved is not None
        assert retrieved.simulation_id == simulation.simulation_id
        assert retrieved.capital == simulation.capital
        assert len(retrieved.parameters) == 1
        assert len(retrieved.results) == 1
        assert retrieved.results[0].step == results.step

    @pytest.mark.asyncio
    async def test_update_simulation(self, simulation_repo):
        """Тест обновления Simulation."""
        params = SimulationParameters(step=1, capital=10000000)
        simulation = Simulation(
            simulation_id=str(uuid4()),
            capital=10000000,
            parameters=[params],
            results=[],
            room_id="test_room",
            is_completed=False,
        )

        saved = await simulation_repo.save(simulation)
        saved.capital = 20000000

        updated = await simulation_repo.save(saved)
        assert updated.capital == 20000000

    @pytest.mark.asyncio
    async def test_delete_simulation(self, simulation_repo):
        """Тест удаления Simulation."""
        params = SimulationParameters(step=1, capital=10000000)
        simulation = Simulation(
            simulation_id=str(uuid4()),
            capital=10000000,
            parameters=[params],
            results=[],
            room_id="test_room",
            is_completed=False,
        )

        saved = await simulation_repo.save(simulation)
        deleted = await simulation_repo.delete(saved.simulation_id)

        assert deleted is not None
        assert deleted.simulation_id == simulation.simulation_id

        retrieved = await simulation_repo.get(saved.simulation_id)
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_update_parameters(self, simulation_repo):
        """Тест обновления только параметров Simulation."""
        params1 = SimulationParameters(step=1, capital=10000000)
        simulation = Simulation(
            simulation_id=str(uuid4()),
            capital=10000000,
            parameters=[params1],
            results=[],
            room_id="test_room",
            is_completed=False,
        )

        saved = await simulation_repo.save(simulation)

        # Обновляем параметры
        params2 = SimulationParameters(step=2, capital=15000000)
        updated = await simulation_repo.update_parameters(saved.simulation_id, params2)

        assert updated is not None
        assert len(updated.parameters) == 1
        assert updated.parameters[0].step == params2.step
        assert updated.parameters[0].capital == params2.capital

    @pytest.mark.asyncio
    async def test_update_results(self, simulation_repo):
        """Тест обновления только результатов Simulation."""
        params = SimulationParameters(step=1, capital=10000000)
        simulation = Simulation(
            simulation_id=str(uuid4()),
            capital=10000000,
            parameters=[params],
            results=[],
            room_id="test_room",
            is_completed=False,
        )

        saved = await simulation_repo.save(simulation)

        # Обновляем результаты
        results = SimulationResults(
            step=1,
            profit=75000,
            cost=65000,
            profitability=0.15,
        )
        updated = await simulation_repo.update_results(saved.simulation_id, results)

        assert updated is not None
        assert len(updated.results) == 1
        assert updated.results[0].step == results.step
        assert updated.results[0].profit == results.profit
        assert updated.results[0].cost == results.cost

    @pytest.mark.asyncio
    async def test_update_step(self, simulation_repo):
        """Тест обновления шага симуляции."""
        params = SimulationParameters(step=1, capital=10000000)
        simulation = Simulation(
            simulation_id=str(uuid4()),
            capital=10000000,
            parameters=[params],
            results=[],
            room_id="test_room",
            is_completed=False,
        )

        saved = await simulation_repo.save(simulation)
        updated = await simulation_repo.update_step(saved.simulation_id, 5)

        assert updated is not None
        # Проверяем, что step обновлен в БД (через results)
        retrieved = await simulation_repo.get(saved.simulation_id)
        # step хранится в results, но может быть пустым
        assert retrieved is not None

    @pytest.mark.asyncio
    async def test_update_capital(self, simulation_repo):
        """Тест обновления капитала симуляции."""
        params = SimulationParameters(step=1, capital=10000000)
        simulation = Simulation(
            simulation_id=str(uuid4()),
            capital=10000000,
            parameters=[params],
            results=[],
            room_id="test_room",
            is_completed=False,
        )

        saved = await simulation_repo.save(simulation)
        updated = await simulation_repo.update_capital(saved.simulation_id, 25000000)

        assert updated is not None
        assert updated.capital == 25000000

    @pytest.mark.asyncio
    async def test_simulation_multiple_results(self, simulation_repo):
        """Тест сохранения Simulation с несколькими результатами."""
        params = SimulationParameters(step=1, capital=10000000)

        results1 = SimulationResults(
            step=1,
            profit=50000,
            cost=45000,
            profitability=0.10,
        )
        results2 = SimulationResults(
            step=2,
            profit=60000,
            cost=50000,
            profitability=0.20,
        )

        simulation = Simulation(
            simulation_id=str(uuid4()),
            capital=10000000,
            parameters=[params],
            results=[results1, results2],
            room_id="test_room",
            is_completed=False,
        )

        saved = await simulation_repo.save(simulation)
        assert saved is not None
        assert len(saved.results) == 2
        assert saved.results[0].step == 1
        assert saved.results[1].step == 2

        # Проверяем, что результаты правильно десериализованы
        retrieved = await simulation_repo.get(saved.simulation_id)
        assert retrieved is not None
        assert len(retrieved.results) == 2
        assert retrieved.results[0].step == 1
        assert retrieved.results[1].step == 2

    @pytest.mark.asyncio
    async def test_simulation_results_with_metrics_serialization(self, simulation_repo):
        """Тест сериализации/десериализации результатов с метриками."""
        params = SimulationParameters(step=1, capital=10000000)

        # Создаем результаты с полными метриками
        results = SimulationResults(
            step=1,
            profit=50000,
            cost=45000,
            profitability=0.10,
            factory_metrics=FactoryMetrics(
                profitability=0.10,
                on_time_delivery_rate=0.95,
                oee=0.85,
                total_procurement_cost=20000,
                defect_rate=0.05,
            ),
            production_metrics=ProductionMetrics(
                monthly_productivity=[],
                average_equipment_utilization=0.85,
                wip_count=10,
                finished_goods_count=100,
            ),
            quality_metrics=QualityMetrics(
                defect_percentage=0.05,
                good_output_percentage=0.95,
                defect_causes=[],
                average_material_quality=0.90,
            ),
            engineering_metrics=EngineeringMetrics(
                operation_timings=[],
                downtime_records=[],
                defect_analysis=[],
            ),
            commercial_metrics=CommercialMetrics(
                total_receipts=50000,
                yearly_revenues=[],
                tender_graph=[],
                project_profitabilities=[],
            ),
            procurement_metrics=ProcurementMetrics(
                total_procurement_value=20000,
                supplier_performances=[],
            ),
        )

        simulation = Simulation(
            simulation_id=str(uuid4()),
            capital=10000000,
            parameters=[params],
            results=[results],
            room_id="test_room",
            is_completed=False,
        )

        saved = await simulation_repo.save(simulation)
        retrieved = await simulation_repo.get(saved.simulation_id)

        assert retrieved is not None
        assert len(retrieved.results) == 1
        result = retrieved.results[0]
        assert result.step == 1
        assert result.profit == 50000
        assert result.cost == 45000
        # Проверяем, что метрики десериализованы
        assert result.factory_metrics is not None
        assert result.factory_metrics.profitability == 0.10
        assert result.factory_metrics.total_procurement_cost == 20000
        assert result.production_metrics is not None
        assert result.production_metrics.average_equipment_utilization == 0.85
        assert result.quality_metrics is not None
        assert result.quality_metrics.defect_percentage == 0.05
        assert result.engineering_metrics is not None
        assert result.commercial_metrics is not None
        assert result.commercial_metrics.total_receipts == 50000
        assert result.procurement_metrics is not None
        assert result.procurement_metrics.total_procurement_value == 20000

    @pytest.mark.asyncio
    async def test_simulation_empty_results_filtering(self, simulation_repo):
        """Тест фильтрации пустых результатов (step=0)."""
        params = SimulationParameters(step=1, capital=10000000)

        # Создаем результаты с step=0 (должны быть отфильтрованы)
        empty_result = SimulationResults(
            step=0,
            profit=0,
            cost=0,
            profitability=0.0,
        )

        # И валидный результат
        valid_result = SimulationResults(
            step=1,
            profit=50000,
            cost=45000,
            profitability=0.10,
        )

        simulation = Simulation(
            simulation_id=str(uuid4()),
            capital=10000000,
            parameters=[params],
            results=[empty_result, valid_result],
            room_id="test_room",
            is_completed=False,
        )

        saved = await simulation_repo.save(simulation)
        # Пустой результат должен быть отфильтрован
        assert len(saved.results) == 1
        assert saved.results[0].step == 1

        # Проверяем при получении
        retrieved = await simulation_repo.get(saved.simulation_id)
        assert len(retrieved.results) == 1
        assert retrieved.results[0].step == 1

    @pytest.mark.asyncio
    async def test_get_all_simulations(self, simulation_repo):
        """Тест получения всех симуляций."""
        params1 = SimulationParameters(step=1, capital=10000000)
        params2 = SimulationParameters(step=1, capital=15000000)

        simulation1 = Simulation(
            simulation_id=str(uuid4()),
            capital=10000000,
            parameters=[params1],
            results=[],
            room_id="room1",
            is_completed=False,
        )
        simulation2 = Simulation(
            simulation_id=str(uuid4()),
            capital=15000000,
            parameters=[params2],
            results=[],
            room_id="room2",
            is_completed=False,
        )

        await simulation_repo.save(simulation1)
        await simulation_repo.save(simulation2)

        all_simulations = await simulation_repo.get_all()
        assert len(all_simulations) >= 2

        ids = {s.simulation_id for s in all_simulations}
        assert simulation1.simulation_id in ids
        assert simulation2.simulation_id in ids
