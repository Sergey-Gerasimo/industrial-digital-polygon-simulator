"""
Конфигурация для интеграционных тестов с Docker Compose.
"""

import sys
import time
import pytest
import pytest_asyncio
from pathlib import Path
from testcontainers.compose import DockerCompose
import asyncpg
import grpc
import warnings

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


@pytest.fixture(scope="session")
def docker_compose():
    """Фикстура для управления Docker Compose окружением."""
    compose = DockerCompose(
        str(PROJECT_ROOT),
        compose_file_name="docker-compose.yaml",
        pull=False,
        build=True,  # Собираем образ
    )

    with compose:
        # Ждем готовности PostgreSQL
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
        print("Ожидание запуска simulation_service...")
        max_retries = 120  # Увеличиваем время ожидания
        service_ready = False
        for i in range(max_retries):
            try:
                # Проверяем что контейнер запущен
                stdout, stderr, exit_code = compose.exec_in_container(
                    service_name="simulation_service",
                    command=["python", "-c", "import sys; sys.exit(0)"],
                )
                # Проверяем gRPC порты для обоих сервисов
                channel_db = grpc.insecure_channel("localhost:50052")
                channel_sim = grpc.insecure_channel("localhost:50051")
                try:
                    grpc.channel_ready_future(channel_db).result(timeout=2)
                    grpc.channel_ready_future(channel_sim).result(timeout=2)
                    channel_db.close()
                    channel_sim.close()
                    service_ready = True
                    print("gRPC сервисы готовы!")
                    break
                except Exception:
                    channel_db.close()
                    channel_sim.close()
            except Exception as e:
                if i % 10 == 0:  # Логируем каждые 10 попыток
                    print(f"Ожидание gRPC сервиса... попытка {i}/{max_retries}")
            if not service_ready:
                time.sleep(2)

        if not service_ready:
            # Пробуем получить логи сервиса для отладки
            try:
                stdout, stderr = compose.get_logs("simulation_service")
                print("Логи simulation_service:")
                print(stdout[:2000] if stdout else "Нет логов")
                if stderr:
                    print("Ошибки:")
                    print(stderr[:2000])
            except:
                pass
            raise RuntimeError("gRPC сервис не готов после ожидания")

        yield compose

        # Cleanup happens automatically when exiting context manager


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
    )
    from domain.workplace import Workplace
    from domain.lean_improvement import LeanImprovement
    from domain import Qualification, Specialization

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
        finally:
            # Явно закрываем сессию
            await session.close()

    yield  # Тест выполняется здесь

    # Закрываем engine после использования
    await test_engine.dispose()

    # Cleanup не нужен, так как cleanup_database уже очищает все таблицы
