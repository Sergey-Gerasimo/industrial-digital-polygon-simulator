from datetime import datetime, timezone
from typing import Optional
from uuid import UUID as PyUUID, uuid4
from sqlalchemy.dialects.postgresql import UUID as SAUUID
from sqlalchemy import String, Enum as SQLEnum, ForeignKey
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base
from domain import (
    ConsumerType,
    VehicleType,
    DealingWithDefects,
    ProductImpruvement,
    Qualification,
    Specialization,
)

get_current_time = lambda: datetime.now(timezone.utc).replace(tzinfo=None)


class Worker(Base):
    __tablename__ = "workers"

    worker_id: Mapped[PyUUID] = mapped_column(
        SAUUID(as_uuid=True), default=uuid4, primary_key=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    qualification: Mapped[Qualification] = mapped_column(
        SQLEnum(Qualification, name="qualification_enum"), nullable=False
    )
    specialization: Mapped[Specialization] = mapped_column(
        SQLEnum(Specialization, name="specialization_enum"), nullable=False
    )
    salary: Mapped[int] = mapped_column(nullable=False)

    type: Mapped[str] = mapped_column(String(20), nullable=False, default="worker")

    speed: Mapped[Optional[int]] = mapped_column(nullable=True, default=0)
    vehicle_type: Mapped[Optional[VehicleType]] = mapped_column(
        SQLEnum(VehicleType, name="vehicle_type_enum"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        default=get_current_time, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=get_current_time, onupdate=get_current_time, nullable=False
    )

    __mapper_args__ = {
        "polymorphic_on": type,
        "polymorphic_identity": "worker",
        "with_polymorphic": "*",
    }


async def create_tables(async_engine: AsyncEngine):
    """Создает все таблицы в базе данных."""

    async with async_engine.begin() as conn:
        # Создаем все таблицы (включая enum типы)
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables(async_engine: AsyncEngine):
    """Удаляет все таблицы из базы данных."""

    async with async_engine.begin() as conn:
        # Удаляем все таблицы и enum типы
        await conn.run_sync(Base.metadata.drop_all)
