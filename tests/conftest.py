"""
Конфигурация для интеграционных тестов с Docker Compose.
"""

import sys
import time
import pytest
import pytest_asyncio
from pathlib import Path
from typing import Iterable, List
import logging

from testcontainers.compose import DockerCompose
import asyncpg
import grpc

# Подавляем предупреждения SQLAlchemy о несовместимой полиморфной идентичности 'logist'
# Мы используем прямой SQL для обхода полиморфной загрузки, поэтому эти предупреждения не критичны
# Фильтр настроен в pyproject.toml в секции [tool.pytest.ini_options]

# Путь к корню проекта
PROJECT_ROOT = Path(__file__).parent.parent

# Добавляем корень проекта в sys.path для импорта модулей
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from grpc_generated.simulator_pb2_grpc import (
    SimulationDatabaseManagerStub,
    SimulationServiceStub,
)

from loguru import logger


@pytest.fixture(scope="session", autouse=True)
def configure_test_logging():
    """Прибираем шумные логи в успешных тестах."""
    # Подавляем debug/info от стандартного логгера
    logging.getLogger().setLevel(logging.WARNING)
    for noisy in ("infrastructure.repositories", "asyncio"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    # Настраиваем loguru только на предупреждения и выше
    logger.remove()
    logger.add(sys.stderr, level="WARNING")
    yield


def log_container_logs(
    compose: DockerCompose,
    services: Iterable[str],
    label: str,
    max_chars: int = 4000,
) -> None:
    """Выводит логи указанных контейнеров для отладки."""
    for service in services:
        try:
            stdout, stderr = compose.get_logs(service)
            if stdout:
                logger.info(f"[{label}] {service} stdout:\n{stdout[-max_chars:]}")
            if stderr:
                logger.warning(f"[{label}] {service} stderr:\n{stderr[-max_chars:]}")
        except Exception as exc:  # pragma: no cover - только для отладки
            logger.warning(f"[{label}] Не удалось получить логи {service}: {exc}")


def log_local_files(
    log_dir: Path, label: str, max_files: int = 5, max_chars: int = 4000
) -> None:
    """Выводит хвост локальных файлов логов (монтируются из контейнера)."""
    if not log_dir.exists():
        return

    files: List[Path] = [
        p
        for p in sorted(
            log_dir.rglob("*"), key=lambda p: p.stat().st_mtime, reverse=True
        )
        if p.is_file()
    ][:max_files]

    for file_path in files:
        try:
            content = file_path.read_text(errors="ignore")
            if content:
                logger.warning(
                    f"[{label}] {file_path.name} (tail):\n{content[-max_chars:]}"
                )
        except Exception as exc:  # pragma: no cover - только для отладки
            logger.warning(f"[{label}] Не удалось прочитать {file_path}: {exc}")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Сохраняем репорты этапов теста на item для последующего анализа."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture(autouse=True)
def log_containers_on_failure(request, docker_compose):
    """Если тест упал, выводим логи контейнеров для отладки."""
    yield
    rep_call = getattr(request.node, "rep_call", None)
    if rep_call and rep_call.failed:
        log_container_logs(
            docker_compose,
            services=("simulation_service", "db", "redis"),
            label=f"test-failed:{request.node.name}",
        )
        log_local_files(
            PROJECT_ROOT / "logs",
            label=f"test-failed:{request.node.name}",
        )


@pytest.fixture(scope="session")
def docker_compose():
    """Фикстура для управления Docker Compose окружением."""
    logger.debug("Запуск Docker Compose для тестирования...")

    compose = DockerCompose(
        str(PROJECT_ROOT),
        compose_file_name="docker-compose.yaml",
        pull=False,
        build=True,
    )

    with compose:
        max_retries = 60
        for i in range(max_retries):
            try:
                stdout, stderr, exit_code = compose.exec_in_container(
                    service_name="db",
                    command=["pg_isready", "-U", "user"],
                )
                if exit_code == 0:
                    break
            except Exception as e:
                if i == max_retries - 1:
                    raise RuntimeError(f"PostgreSQL не готов после ожидания: {e}")
            if i == max_retries - 1:
                raise RuntimeError("PostgreSQL не готов после ожидания")
            time.sleep(1)

        # Ждем запуска сервиса - проверяем логи
        logger.debug("Ожидание запуска simulation_service...")
        max_retries = 120  # Увеличиваем время ожидания
        service_ready = False
        for i in range(max_retries):
            try:
                # Проверяем что контейнер запущен
                stdout, stderr, exit_code = compose.exec_in_container(
                    service_name="simulation_service",
                    command=["python", "-c", "import sys; sys.exit(0)"],
                )
                channel_db = grpc.insecure_channel("localhost:50052")
                channel_sim = grpc.insecure_channel("localhost:50051")
                try:
                    grpc.channel_ready_future(channel_db).result(timeout=2)
                    grpc.channel_ready_future(channel_sim).result(timeout=2)
                    channel_db.close()
                    channel_sim.close()
                    service_ready = True
                    logger.debug("gRPC сервисы готовы!")
                    break
                except Exception:
                    channel_db.close()
                    channel_sim.close()
            except Exception as e:
                if i % 10 == 0:  # Логируем каждые 10 попыток
                    logger.debug(f"Ожидание gRPC сервиса... попытка {i}/{max_retries}")
            if not service_ready:
                time.sleep(2)

        if not service_ready:
            # Пробуем получить логи сервисов для отладки
            log_container_logs(
                compose,
                services=("simulation_service", "db", "redis"),
                label="startup-failed",
                max_chars=4000,
            )
            raise RuntimeError("gRPC сервис не готов после ожидания")

        yield compose


@pytest_asyncio.fixture(scope="function", autouse=True)
async def cleanup_database(docker_compose):
    """Очищает базу данных перед и после каждого теста."""
    # Используем прямые значения для подключения к тестовой БД
    db_host = "localhost"
    db_port = 5432
    db_user = "user"
    db_password = "password"
    db_name = "auth_db"

    async def cleanup_tables():
        """Вспомогательная функция для очистки таблиц."""
        conn = None
        try:
            conn = await asyncpg.connect(
                host=db_host,
                port=db_port,
                user=db_user,
                password=db_password,
                database=db_name,
                timeout=10,  # Таймаут для подключения
            )

            # Получаем список всех таблиц
            tables = await conn.fetch(
                """
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public'
                """
            )

            if tables:
                # Очищаем все таблицы
                table_names = [t["tablename"] for t in tables]
                # Используем безопасное форматирование через идентификаторы
                quoted_names = [f'"{name}"' for name in table_names]
                await conn.execute(
                    f"TRUNCATE TABLE {', '.join(quoted_names)} RESTART IDENTITY CASCADE"
                )
        except Exception as e:
            # Игнорируем ошибки если таблицы еще не созданы
            # (сервис создаст их при первом запуске)
            pass
        finally:
            if conn:
                try:
                    await conn.close()
                except Exception:
                    # Игнорируем ошибки при закрытии соединения
                    pass

    # Очищаем перед тестом
    await cleanup_tables()

    yield

    # Очищаем после теста
    await cleanup_tables()


@pytest.fixture(scope="session")
def grpc_channel(docker_compose):
    """Создает gRPC канал для подключения к db_manager сервису."""
    port = 50052  # Порт для db_manager сервиса
    channel = grpc.insecure_channel(f"localhost:{port}")

    # Ждем готовности канала
    max_retries = 30
    for i in range(max_retries):
        try:
            grpc.channel_ready_future(channel).result(timeout=5)
            break
        except Exception:
            if i < max_retries - 1:
                time.sleep(1)
            else:
                channel.close()
                raise

    yield channel
    channel.close()


@pytest.fixture(scope="session")
def grpc_simulation_channel(docker_compose):
    """Создает gRPC канал для подключения к simulation сервису."""
    port = 50051  # Порт для simulation сервиса
    channel = grpc.insecure_channel(f"localhost:{port}")

    # Ждем готовности канала
    max_retries = 30
    for i in range(max_retries):
        try:
            grpc.channel_ready_future(channel).result(timeout=5)
            break
        except Exception:
            if i < max_retries - 1:
                time.sleep(1)
            else:
                channel.close()
                raise

    yield channel
    channel.close()


@pytest.fixture(scope="function")
def db_manager_stub(grpc_channel):
    """Создает stub для SimulationDatabaseManager."""
    return SimulationDatabaseManagerStub(grpc_channel)


@pytest.fixture(scope="function")
def simulation_stub(grpc_simulation_channel):
    """Создает stub для SimulationService."""
    return SimulationServiceStub(grpc_simulation_channel)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def populate_test_data():
    """Заполняет БД тестовыми данными перед каждым тестом через репозитории.

    Эта фикстура выполняется автоматически после cleanup_database,
    чтобы заполнить БД необходимыми тестовыми данными:
    - Workplaces (нужны для factory при создании симуляции)
    - LeanImprovements (нужны для factory и теста set_lean_improvement_status)
    """
    from uuid import uuid4
    from sqlalchemy.ext.asyncio import (
        create_async_engine,
        async_sessionmaker,
        AsyncSession,
    )
    from infrastructure.repositories import (
        WorkplaceRepository,
        LeanImprovementRepository,
        WorkerRepository,
        SupplierRepository,
        EquipmentRepository,
        ConsumerRepository,
        TenderRepository,
    )
    from domain.workplace import Workplace
    from domain.lean_improvement import LeanImprovement
    from domain.worker import Worker, Qualification, Specialization
    from domain.supplier import Supplier
    from domain.equipment import Equipment
    from domain.consumer import Consumer, ConsumerType
    from domain.tender import Tender, PaymentForm
    from domain.logist import Logist, VehicleType

    # Используем те же параметры подключения, что и в cleanup_database
    db_host = "localhost"
    db_port = 5432
    db_user = "user"
    db_password = "password"
    db_name = "auth_db"

    # Создаем engine и session с тестовыми параметрами
    test_db_url = (
        f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )
    test_engine = create_async_engine(
        test_db_url,
        echo=False,
        pool_size=5,  # Ограничиваем размер пула
        max_overflow=10,  # Максимальное количество дополнительных соединений
        pool_pre_ping=True,  # Проверяем соединения перед использованием
    )
    TestSessionLocal = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )

    async with TestSessionLocal() as session:
        try:
            # Создаем рабочих (нужны для всех операций)
            worker_repo = WorkerRepository(session)

            worker1 = Worker(
                worker_id=str(uuid4()),
                name="Test Worker 1",
                qualification=Qualification.II.value,
                specialty=Specialization.ASSEMBLER.value,
                salary=50000,
            )
            try:
                await worker_repo.save(worker1)
                await session.commit()
            except Exception:
                await session.rollback()

            worker2 = Worker(
                worker_id=str(uuid4()),
                name="Test Worker 2",
                qualification=Qualification.III.value,
                specialty=Specialization.WAREHOUSE_KEEPER.value,
                salary=45000,
            )
            try:
                await worker_repo.save(worker2)
                await session.commit()
            except Exception:
                await session.rollback()

            worker3 = Worker(
                worker_id=str(uuid4()),
                name="Test Worker 3",
                qualification=Qualification.IV.value,
                specialty=Specialization.QUALITY_CONTROLLER.value,
                salary=55000,
            )
            try:
                await worker_repo.save(worker3)
                await session.commit()
            except Exception:
                await session.rollback()

            # Создаем логистов
            logist1 = Logist(
                worker_id=str(uuid4()),
                name="Test Logist 1",
                qualification=Qualification.III.value,
                specialty=Specialization.LOGIST.value,
                salary=60000,
                speed=80,
                vehicle_type=VehicleType.VAN.value,
            )
            try:
                await worker_repo.save(logist1)
                await session.commit()
            except Exception:
                await session.rollback()

            logist2 = Logist(
                worker_id=str(uuid4()),
                name="Test Logist 2",
                qualification=Qualification.IV.value,
                specialty=Specialization.LOGIST.value,
                salary=65000,
                speed=90,
                vehicle_type=VehicleType.TRUCK.value,
            )
            try:
                await worker_repo.save(logist2)
                await session.commit()
            except Exception:
                await session.rollback()

            logist3 = Logist(
                worker_id=str(uuid4()),
                name="Test Logist 3",
                qualification=Qualification.II.value,
                specialty=Specialization.LOGIST.value,
                salary=55000,
                speed=70,
                vehicle_type=VehicleType.ELECTRIC.value,
            )
            try:
                await worker_repo.save(logist3)
                await session.commit()
            except Exception:
                await session.rollback()

            # Создаем поставщиков
            supplier_repo = SupplierRepository(session)

            supplier1 = Supplier(
                supplier_id=str(uuid4()),
                name="Test Supplier 1",
                product_name="Steel Materials",
                material_type="raw_materials",
                delivery_period=7,
                special_delivery_period=3,
                reliability=0.95,
                product_quality=0.9,
                cost=1000,
                special_delivery_cost=1500,
            )
            try:
                await supplier_repo.save(supplier1)
                await session.commit()
            except Exception:
                await session.rollback()

            supplier2 = Supplier(
                supplier_id=str(uuid4()),
                name="Test Supplier 2",
                product_name="Electronic Components",
                material_type="components",
                delivery_period=10,
                special_delivery_period=5,
                reliability=0.9,
                product_quality=0.85,
                cost=2000,
                special_delivery_cost=3000,
            )
            try:
                await supplier_repo.save(supplier2)
                await session.commit()
            except Exception:
                await session.rollback()

            supplier3 = Supplier(
                supplier_id=str(uuid4()),
                name="Test Supplier 3",
                product_name="Packaging Materials",
                material_type="packaging",
                delivery_period=5,
                special_delivery_period=2,
                reliability=0.98,
                product_quality=0.95,
                cost=500,
                special_delivery_cost=800,
            )
            try:
                await supplier_repo.save(supplier3)
                await session.commit()
            except Exception:
                await session.rollback()

            # Создаем оборудование
            equipment_repo = EquipmentRepository(session)

            equipment1 = Equipment(
                equipment_id=str(uuid4()),
                name="Test CNC Machine 1",
                equipment_type="cnc_machine",
                reliability=0.95,
                maintenance_period=30,
                maintenance_cost=5000,
                cost=500000,
                repair_cost=10000,
                repair_time=8,
            )
            try:
                await equipment_repo.save(equipment1)
                await session.commit()
            except Exception:
                await session.rollback()

            equipment2 = Equipment(
                equipment_id=str(uuid4()),
                name="Test Assembly Line 1",
                equipment_type="assembly_line",
                reliability=0.92,
                maintenance_period=45,
                maintenance_cost=8000,
                cost=750000,
                repair_cost=15000,
                repair_time=12,
            )
            try:
                await equipment_repo.save(equipment2)
                await session.commit()
            except Exception:
                await session.rollback()

            equipment3 = Equipment(
                equipment_id=str(uuid4()),
                name="Test Quality Control Station 1",
                equipment_type="quality_station",
                reliability=0.98,
                maintenance_period=60,
                maintenance_cost=3000,
                cost=150000,
                repair_cost=5000,
                repair_time=4,
            )
            try:
                await equipment_repo.save(equipment3)
                await session.commit()
            except Exception:
                await session.rollback()

            # Создаем потребителей
            consumer_repo = ConsumerRepository(session)

            consumer1 = Consumer(
                consumer_id=uuid4(),
                name="Test Government Agency",
                type=ConsumerType.GOVERMANT.value,
            )
            try:
                await consumer_repo.save(consumer1)
                await session.commit()
            except Exception:
                await session.rollback()

            consumer2 = Consumer(
                consumer_id=uuid4(),
                name="Test Private Company",
                type=ConsumerType.NOT_GOVERMANT.value,
            )
            try:
                await consumer_repo.save(consumer2)
                await session.commit()
            except Exception:
                await session.rollback()

            consumer3 = Consumer(
                consumer_id=uuid4(),
                name="Test International Corp",
                type=ConsumerType.NOT_GOVERMANT.value,
            )
            try:
                await consumer_repo.save(consumer3)
                await session.commit()
            except Exception:
                await session.rollback()

            # Создаем тендеры
            tender_repo = TenderRepository(session)

            tender1 = Tender(
                tender_id=str(uuid4()),
                consumer=consumer1,
                cost=50000,
                quantity_of_products=100,
                penalty_per_day=500,
                warranty_years=2,
                payment_form=PaymentForm.FULL_ADVANCE.value,
            )
            try:
                await tender_repo.save(tender1)
                await session.commit()
            except Exception:
                await session.rollback()

            tender2 = Tender(
                tender_id=str(uuid4()),
                consumer=consumer2,
                cost=75000,
                quantity_of_products=150,
                penalty_per_day=750,
                warranty_years=3,
                payment_form=PaymentForm.PARTIAL_ADVANCE.value,
            )
            try:
                await tender_repo.save(tender2)
                await session.commit()
            except Exception:
                await session.rollback()

            tender3 = Tender(
                tender_id=str(uuid4()),
                consumer=consumer3,
                cost=100000,
                quantity_of_products=200,
                penalty_per_day=1000,
                warranty_years=5,
                payment_form=PaymentForm.ON_DELIVERY.value,
            )
            try:
                await tender_repo.save(tender3)
                await session.commit()
            except Exception:
                await session.rollback()

            # Создаем рабочие места (нужны для factory при создании симуляции)
            workplace_repo = WorkplaceRepository(session)

            workplace1 = Workplace(
                workplace_id=str(uuid4()),
                workplace_name="Test Workplace 1",
                required_speciality=Specialization.ASSEMBLER.value,
                required_qualification=Qualification.III.value,
                required_equipment="",
                is_start_node=True,
                is_end_node=False,
                # x и y по умолчанию None
            )
            try:
                await workplace_repo.save(workplace1)
                await session.commit()
            except Exception:
                await session.rollback()
                # Может уже существовать, игнорируем

            workplace2 = Workplace(
                workplace_id=str(uuid4()),
                workplace_name="Test Workplace 2",
                required_speciality=Specialization.ENGINEER_TECHNOLOGIST.value,
                required_qualification=Qualification.II.value,
                required_equipment="",
                is_start_node=False,
                is_end_node=True,
                # x и y по умолчанию None
            )
            try:
                await workplace_repo.save(workplace2)
                await session.commit()
            except Exception:
                await session.rollback()

            workplace3 = Workplace(
                workplace_id=str(uuid4()),
                workplace_name="Test Workplace 3",
                required_speciality=Specialization.QUALITY_CONTROLLER.value,
                required_qualification=Qualification.III.value,
                required_equipment="",
                is_start_node=False,
                is_end_node=False,
                # x и y по умолчанию None
            )
            try:
                await workplace_repo.save(workplace3)
                await session.commit()
            except Exception:
                await session.rollback()

            # Создаем LEAN улучшения (нужны для factory и теста set_lean_improvement_status)
            improvement_repo = LeanImprovementRepository(session)

            improvement1 = LeanImprovement(
                improvement_id=str(uuid4()),
                name="Test Improvement",
                is_implemented=False,
                implementation_cost=10000,
                efficiency_gain=0.15,
            )
            try:
                await improvement_repo.save(improvement1)
                await session.commit()
            except Exception:
                await session.rollback()

            improvement2 = LeanImprovement(
                improvement_id=str(uuid4()),
                name="Another Improvement",
                is_implemented=False,
                implementation_cost=15000,
                efficiency_gain=0.20,
            )
            try:
                await improvement_repo.save(improvement2)
                await session.commit()
            except Exception:
                await session.rollback()

            improvement3 = LeanImprovement(
                improvement_id=str(uuid4()),
                name="Third Improvement",
                is_implemented=False,
                implementation_cost=20000,
                efficiency_gain=0.25,
            )
            try:
                await improvement_repo.save(improvement3)
                await session.commit()
            except Exception:
                await session.rollback()
        finally:
            # Явно закрываем сессию
            await session.close()

    yield  # Тест выполняется здесь

    # Закрываем engine после использования
    await test_engine.dispose()

    # Cleanup не нужен, так как cleanup_database уже очищает все таблицы
