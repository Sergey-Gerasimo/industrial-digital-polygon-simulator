from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID as PyUUID, uuid4
from sqlalchemy.dialects.postgresql import UUID as SAUUID, JSONB as SAJSONB

from sqlalchemy import ARRAY, String, Enum as SQLEnum, ForeignKey, BigInteger, Integer
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base
from domain import (
    ConsumerType,
    VehicleType,
    PaymentForm,
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
    salary: Mapped[int] = mapped_column(BigInteger, nullable=False)

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


class Supplier(Base):
    __tablename__ = "suppliers"

    supplier_id: Mapped[PyUUID] = mapped_column(
        SAUUID(as_uuid=True), default=uuid4, primary_key=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    product_name: Mapped[str] = mapped_column(String(100), nullable=False)
    material_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    delivery_period: Mapped[int] = mapped_column(BigInteger, nullable=False)
    special_delivery_period: Mapped[int] = mapped_column(BigInteger, nullable=False)
    reliability: Mapped[float] = mapped_column(nullable=False)
    product_quality: Mapped[float] = mapped_column(nullable=False)
    cost: Mapped[int] = mapped_column(BigInteger, nullable=False)
    special_delivery_cost: Mapped[int] = mapped_column(BigInteger, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        default=get_current_time, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=get_current_time, onupdate=get_current_time, nullable=False
    )


class Equipment(Base):
    __tablename__ = "equipment"
    equipment_id: Mapped[PyUUID] = mapped_column(
        SAUUID(as_uuid=True), default=uuid4, primary_key=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    equipment_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    reliability: Mapped[float] = mapped_column(nullable=False)
    maintenance_period: Mapped[int] = mapped_column(BigInteger, nullable=False)
    maintenance_cost: Mapped[int] = mapped_column(BigInteger, nullable=False)
    cost: Mapped[int] = mapped_column(BigInteger, nullable=False)
    repair_cost: Mapped[int] = mapped_column(BigInteger, nullable=False)
    repair_time: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        default=get_current_time, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=get_current_time, onupdate=get_current_time, nullable=False
    )


class Workplace(Base):
    __tablename__ = "workplaces"
    workplace_id: Mapped[PyUUID] = mapped_column(
        SAUUID(as_uuid=True), default=uuid4, primary_key=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    required_speciality: Mapped[Specialization] = mapped_column(
        SQLEnum(Specialization, name="specialization_enum"), nullable=False
    )
    required_qualification: Mapped[Qualification] = mapped_column(
        SQLEnum(Qualification, name="qualification_enum"), nullable=False
    )
    required_equipment: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )
    required_stages: Mapped[List[str]] = mapped_column(
        ARRAY(String(100)), nullable=False, default=list
    )
    is_start_node: Mapped[bool] = mapped_column(nullable=False, default=False)
    is_end_node: Mapped[bool] = mapped_column(nullable=False, default=False)
    next_workplace_ids: Mapped[List[PyUUID]] = mapped_column(
        ARRAY(SAUUID(as_uuid=True)), nullable=False, default=list
    )
    x: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=None)  # координата X на площадке 7x7 (0-6), null если не установлена
    y: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=None)  # координата Y на площадке 7x7 (0-6), null если не установлена
    created_at: Mapped[datetime] = mapped_column(
        default=get_current_time, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=get_current_time, onupdate=get_current_time, nullable=False
    )


class Consumer(Base):
    __tablename__ = "consumers"
    consumer_id: Mapped[PyUUID] = mapped_column(
        SAUUID(as_uuid=True), default=uuid4, primary_key=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[ConsumerType] = mapped_column(
        SQLEnum(ConsumerType, name="consumer_type_enum"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        default=get_current_time, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=get_current_time, onupdate=get_current_time, nullable=False
    )


class Tender(Base):
    __tablename__ = "tenders"
    tender_id: Mapped[PyUUID] = mapped_column(
        SAUUID(as_uuid=True), default=uuid4, primary_key=True
    )
    consumer_id: Mapped[PyUUID] = mapped_column(
        SAUUID(as_uuid=True), ForeignKey("consumers.consumer_id"), nullable=False
    )
    cost: Mapped[int] = mapped_column(BigInteger, nullable=False)
    quantity_of_products: Mapped[int] = mapped_column(nullable=False)
    penalty_per_day: Mapped[int] = mapped_column(BigInteger, nullable=False)
    warranty_years: Mapped[int] = mapped_column(nullable=False)
    payment_form: Mapped[PaymentForm] = mapped_column(
        SQLEnum(PaymentForm, name="payment_form_enum"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        default=get_current_time, nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        default=get_current_time, onupdate=get_current_time, nullable=False
    )


class LeanImprovement(Base):
    __tablename__ = "lean_improvements"

    improvement_id: Mapped[PyUUID] = mapped_column(
        SAUUID(as_uuid=True), default=uuid4, primary_key=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    is_implemented: Mapped[bool] = mapped_column(nullable=False, default=False)
    implementation_cost: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0
    )
    efficiency_gain: Mapped[float] = mapped_column(nullable=False, default=0.0)

    created_at: Mapped[datetime] = mapped_column(
        default=get_current_time, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=get_current_time, onupdate=get_current_time, nullable=False
    )


async def create_tables(async_engine: AsyncEngine):
    """Создает все таблицы в базе данных."""

    async with async_engine.begin() as conn:
        # Создаем все таблицы (включая enum типы)
        await conn.run_sync(Base.metadata.create_all)


class Simulation(Base):
    __tablename__ = "simulations"

    simulation_id: Mapped[PyUUID] = mapped_column(
        SAUUID(as_uuid=True), default=uuid4, primary_key=True
    )
    capital: Mapped[int] = mapped_column(BigInteger, nullable=False)
    step: Mapped[int] = mapped_column(nullable=False, default=0)

    # Храним сложные объекты как JSONB
    simulation_parameters: Mapped[dict] = mapped_column(
        SAJSONB, nullable=False, default=lambda: {}
    )
    simulation_results: Mapped[dict] = mapped_column(
        SAJSONB, nullable=False, default=lambda: {}
    )

    created_at: Mapped[datetime] = mapped_column(
        default=get_current_time, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=get_current_time, onupdate=get_current_time, nullable=False
    )


async def drop_tables(async_engine: AsyncEngine):
    """Удаляет все таблицы из базы данных."""

    async with async_engine.begin() as conn:
        # Удаляем все таблицы и enum типы
        await conn.run_sync(Base.metadata.drop_all)
