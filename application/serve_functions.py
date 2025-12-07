import asyncio
from concurrent import futures
from dataclasses import dataclass, field
from logging import Logger, getLogger
import signal
from typing import Optional

import grpc

from grpc_generated.simulator_pb2 import DESCRIPTOR as SIMULATION_DESCRIPTOR
from grpc_generated.simulator_pb2_grpc import (
    add_SimulationServiceServicer_to_server,
    add_SimulationDatabaseManagerServicer_to_server,
)

from .simulation_service import SimulationServiceImpl
from .database_manager_service import SimulationDatabaseManagerImpl


async def serve(
    simulation_service: SimulationServiceImpl,
    db_manager_service: SimulationDatabaseManagerImpl,
    logger: Optional[Logger] = None,
    host: str = "0.0.0.0",
    simulation_port: int = 50051,
    db_manager_port: int = 50052,
    max_workers: int = 10,
    max_message_length: int = 50 * 1024 * 1024,  # 50 MB
):
    if not logger:
        logger = getLogger(name="GRPC")

    logger.info(
        f"Start up gRPC servers with {host=}, {simulation_port=}, {db_manager_port=}, {max_workers=}, {max_message_length=}"
    )
    grpc_options = [
        ("grpc.max_send_message_length", max_message_length),
        ("grpc.max_receive_message_length", max_message_length),
        ("grpc.so_reuseport", 1),
        ("grpc.so_keepalive_time_ms", 10000),
        ("grpc.so_keepalive_timeout_ms", 5000),
        ("grpc.so_keepalive_permit_without_calls", 1),
    ]

    simulation_server = grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers=max_workers),
        options=grpc_options,
    )

    db_manager_server = grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers=max_workers),
        options=grpc_options,
    )

    add_SimulationServiceServicer_to_server(simulation_service, simulation_server)
    add_SimulationDatabaseManagerServicer_to_server(
        db_manager_service, db_manager_server
    )

    simulation_address = f"{host}:{simulation_port}"
    db_manager_address = f"{host}:{db_manager_port}"

    simulation_server.add_insecure_port(simulation_address)
    db_manager_server.add_insecure_port(db_manager_address)

    await simulation_server.start()
    await db_manager_server.start()

    logger.info("Sucseccfull start up!")

    logger.info("Creating stop event")
    stop_event = asyncio.Event()

    def signal_handler():
        logger.info("Got an stop envent")
        stop_event.set()

    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)

    try:
        # Ждем события остановки
        await stop_event.wait()
    finally:
        # Graceful shutdown
        logger.info("Stopping services")

        await simulation_server.stop(grace=5)
        await db_manager_server.stop(grace=5)

        print("Servers succseccfull stoped!")
