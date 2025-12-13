import asyncio
from contextlib import asynccontextmanager
import sys
from infrastructure.config import app_logger, app_settings
from infrastructure.models import create_tables, drop_tables
from infrastructure.database import create_async_engine, async_engine

from application import SimulationDatabaseManagerImpl, SimulationServiceImpl, serve


@asynccontextmanager
async def lifespan():
    app_logger.info("Start application")

    try:
        app_logger.info("Creating tables")
        await create_tables(async_engine)
        app_logger.info("Succseccfull created tables")
    except Exception as e:
        app_logger.error(f"Fatal error: {e}")
        raise

    yield

    app_logger.info("Stopping application")

    try:
        app_logger.info("Dropping tables")
        await drop_tables(async_engine)
        app_logger.info("Succsessfull dropped tables")

    except Exception as e:
        app_logger.error(f"Fatal error: {e}")
        raise


async def main():
    from infrastructure.config import app_logger
    from infrastructure.database import AsyncSessionLocal

    simulation_service = SimulationServiceImpl(session_factory=AsyncSessionLocal)
    db_manager_service = SimulationDatabaseManagerImpl(
        session_factory=AsyncSessionLocal
    )

    async with lifespan():
        try:
            await serve(
                simulation_service=simulation_service,
                db_manager_service=db_manager_service,
                host=app_settings.grpc.host,
                simulation_port=int(app_settings.grpc.simulation_port),
                db_manager_port=int(app_settings.grpc.db_manager_port),
                max_workers=app_settings.grpc.max_workers,
                max_message_length=app_settings.grpc.max_message_length,
            )

        except KeyboardInterrupt:
            app_logger.info("Got a stop signal")
            raise

        except Exception as e:
            app_logger.error(f"Fatal error: {e}")
            raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        app_logger.info("Greasfull shutdown...")
        sys.exit(0)
    except Exception as e:
        app_logger.error(f"Fatal error: {e}")
        sys.exit(1)
