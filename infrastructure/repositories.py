from typing import Union, Optional, List, TYPE_CHECKING
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

if TYPE_CHECKING:
    from domain import Logist

from .abstract_repository import AbstractRepository
from .models import (
    Worker as WorkerDB,
    Supplier as SupplierDB,
    Equipment as EquipmentDB,
    Workplace as WorkplaceDB,
    Consumer as ConsumerDB,
    Tender as TenderDB,
    Simulation as SimulationDB,
    LeanImprovement as LeanImprovementDB,
)
from domain import (
    Worker,
    Supplier,
    Equipment,
    Workplace,
    Consumer,
    Tender,
    Simulation,
    SimulationParameters,
    SimulationResults,
    Specialization,
    ConsumerType,
    LeanImprovement,
)
import json

logger = logging.getLogger(__name__)


# Mapper functions for converting between domain entities and DB models


def worker_db_to_domain(db_model: WorkerDB) -> Worker:
    """Преобразует SQLAlchemy модель Worker в доменную сущность."""
    from domain import Qualification

    # В БД qualification - это enum Qualification, в домене - int
    # qualification может быть enum, int, или строкой (например 'I' из SQL)
    if hasattr(db_model.qualification, "value"):
        qualification_value = db_model.qualification.value
    elif isinstance(db_model.qualification, str):
        # Если это строка, пытаемся преобразовать через enum
        try:
            qual_enum = Qualification[db_model.qualification]
            qualification_value = qual_enum.value
        except (ValueError, KeyError):
            try:
                qual_enum = Qualification(int(db_model.qualification))
                qualification_value = qual_enum.value
            except (ValueError, TypeError):
                qualification_value = Qualification.I.value
    elif isinstance(db_model.qualification, int):
        qualification_value = db_model.qualification
    else:
        qualification_value = Qualification.I.value

    # В БД specialization - это enum Specialization, в домене specialty - строка (значение enum)
    # specialization может быть enum, строкой (имя enum 'ASSEMBLER') или строкой (значение enum 'Слесарь-сборщик')
    from domain import Specialization
    
    if isinstance(db_model.specialization, Specialization):
        specialty_value = db_model.specialization.value
    elif isinstance(db_model.specialization, str):
        # Если это строка, пытаемся найти enum по имени или по значению
        try:
            # Пробуем найти по имени enum (например 'ASSEMBLER')
            spec_enum = Specialization[db_model.specialization]
            specialty_value = spec_enum.value
        except (ValueError, KeyError):
            try:
                # Пробуем найти по значению enum (например 'Слесарь-сборщик')
                spec_enum = Specialization(db_model.specialization)
                specialty_value = spec_enum.value
            except (ValueError, KeyError):
                # Если не нашли, используем строку как есть
                specialty_value = str(db_model.specialization or "")
    else:
        specialty_value = str(db_model.specialization or "")

    return Worker(
        worker_id=str(db_model.worker_id) if db_model.worker_id else "",
        name=db_model.name or "",
        qualification=qualification_value,
        specialty=specialty_value,
        salary=db_model.salary or 0,
    )


def worker_db_to_logist_domain(db_model: WorkerDB):
    """Преобразует SQLAlchemy модель Worker в доменную сущность Logist."""
    from domain import Logist, Qualification

    # В БД qualification - это enum Qualification, в домене - int
    # qualification может быть enum, int, или строкой (например 'I' из SQL)
    if hasattr(db_model.qualification, "value"):
        qualification_value = db_model.qualification.value
    elif isinstance(db_model.qualification, str):
        # Если это строка, пытаемся преобразовать через enum
        try:
            qual_enum = Qualification[db_model.qualification]
            qualification_value = qual_enum.value
        except (ValueError, KeyError):
            try:
                qual_enum = Qualification(int(db_model.qualification))
                qualification_value = qual_enum.value
            except (ValueError, TypeError):
                qualification_value = Qualification.I.value
    elif isinstance(db_model.qualification, int):
        qualification_value = db_model.qualification
    else:
        qualification_value = Qualification.I.value

    # В БД specialization - это enum Specialization, в домене specialty - строка (значение enum)
    # specialization может быть enum, строкой (имя enum 'ASSEMBLER') или строкой (значение enum 'Логист')
    from domain import Specialization
    
    if isinstance(db_model.specialization, Specialization):
        specialty_value = db_model.specialization.value
    elif isinstance(db_model.specialization, str):
        # Если это строка, пытаемся найти enum по имени или по значению
        try:
            # Пробуем найти по имени enum (например 'LOGIST')
            spec_enum = Specialization[db_model.specialization]
            specialty_value = spec_enum.value
        except (ValueError, KeyError):
            try:
                # Пробуем найти по значению enum (например 'Логист')
                spec_enum = Specialization(db_model.specialization)
                specialty_value = spec_enum.value
            except (ValueError, KeyError):
                # Если не нашли, используем строку как есть
                specialty_value = str(db_model.specialization or "")
    else:
        specialty_value = str(db_model.specialization or "")

    # В БД vehicle_type - это enum VehicleType, в домене - строка (значение enum)
    # vehicle_type может быть enum, строкой (имя enum 'VAN') или строкой (значение enum 'Грузовой фургон')
    from domain import VehicleType
    
    if isinstance(db_model.vehicle_type, VehicleType):
        vehicle_type_value = db_model.vehicle_type.value
    elif isinstance(db_model.vehicle_type, str) and db_model.vehicle_type:
        # Если это строка, пытаемся найти enum по имени или по значению
        try:
            # Пробуем найти по имени enum (например 'VAN')
            vehicle_enum = VehicleType[db_model.vehicle_type]
            vehicle_type_value = vehicle_enum.value
        except (ValueError, KeyError):
            try:
                # Пробуем найти по значению enum (например 'Грузовой фургон')
                vehicle_enum = VehicleType(db_model.vehicle_type)
                vehicle_type_value = vehicle_enum.value
            except (ValueError, KeyError):
                # Если не нашли, используем строку как есть
                vehicle_type_value = str(db_model.vehicle_type or "")
    else:
        vehicle_type_value = str(db_model.vehicle_type or "") if db_model.vehicle_type else ""

    return Logist(
        worker_id=str(db_model.worker_id) if db_model.worker_id else "",
        name=db_model.name or "",
        qualification=qualification_value,
        specialty=specialty_value,
        salary=db_model.salary or 0,
        speed=db_model.speed if db_model.speed is not None else 0,
        vehicle_type=vehicle_type_value,
    )


def worker_domain_to_db(
    domain_entity: Worker, db_model: Optional[WorkerDB] = None
) -> WorkerDB:
    """Преобразует доменную сущность Worker в SQLAlchemy модель."""
    from domain import Logist

    if db_model is None:
        db_model = WorkerDB()

    # Определяем тип СРАЗУ после создания объекта, чтобы переопределить default="worker"
    # Проверяем и по классу, и по имени класса, и по наличию атрибутов логиста
    # Логист определяется наличием атрибутов speed и vehicle_type (даже если speed=0 или vehicle_type=NONE)
    has_speed_attr = hasattr(domain_entity, "speed")
    has_vehicle_type_attr = hasattr(domain_entity, "vehicle_type")
    is_logist = (
        isinstance(domain_entity, Logist)
        or type(domain_entity).__name__ == "Logist"
        or (has_speed_attr and has_vehicle_type_attr)
    )

    # Устанавливаем тип СРАЗУ, до установки других полей
    if is_logist:
        db_model.type = "logist"
        logger.debug(
            f"Setting worker type to 'logist' for worker_id={domain_entity.worker_id}, "
            f"entity_type={type(domain_entity).__name__}, is_logist={is_logist}"
        )
    else:
        # Если это обновление и уже был логист, не меняем тип на worker
        existing_type = getattr(db_model, "type", None)
        if existing_type == "logist":
            logger.debug(
                f"Keeping existing type 'logist' for worker_id={domain_entity.worker_id}"
            )
            db_model.type = "logist"
        else:
            db_model.type = "worker"
            logger.debug(
                f"Setting worker type to 'worker' for worker_id={domain_entity.worker_id}, "
                f"entity_type={type(domain_entity).__name__}"
            )

    db_model.name = domain_entity.name

    # В домене qualification - int, в БД - enum Qualification
    if isinstance(domain_entity.qualification, int):
        from domain import Qualification

        try:
            db_model.qualification = Qualification(domain_entity.qualification)
        except (ValueError, KeyError):
            db_model.qualification = Qualification.I
    else:
        db_model.qualification = domain_entity.qualification

    # В домене specialty - строка, в БД specialization - enum Specialization
    if isinstance(domain_entity.specialty, str):
        try:
            db_model.specialization = Specialization(domain_entity.specialty)
        except ValueError:
            db_model.specialization = Specialization.NONE
    else:
        db_model.specialization = domain_entity.specialty

    db_model.salary = domain_entity.salary

    # Устанавливаем поля логиста, если это логист
    if is_logist or db_model.type == "logist":
        if hasattr(domain_entity, "speed"):
            db_model.speed = domain_entity.speed
        if hasattr(domain_entity, "vehicle_type"):
            from domain import VehicleType

            # В домене vehicle_type - строка, в БД - enum VehicleType
            if isinstance(domain_entity.vehicle_type, str):
                try:
                    db_model.vehicle_type = VehicleType(domain_entity.vehicle_type)
                except (ValueError, KeyError):
                    db_model.vehicle_type = VehicleType.NONE
            elif isinstance(domain_entity.vehicle_type, VehicleType):
                db_model.vehicle_type = domain_entity.vehicle_type
            else:
                db_model.vehicle_type = VehicleType.NONE
        else:
            from domain import VehicleType

            db_model.vehicle_type = VehicleType.NONE

    # worker_id теперь строка
    if domain_entity.worker_id:
        db_model.worker_id = domain_entity.worker_id

    logger.debug(
        f"Final db_model.type='{db_model.type}' for worker_id={db_model.worker_id}"
    )
    return db_model


def supplier_db_to_domain(db_model: SupplierDB) -> Supplier:
    """Преобразует SQLAlchemy модель Supplier в доменную сущность."""
    return Supplier(
        supplier_id=str(db_model.supplier_id) if db_model.supplier_id else "",
        name=db_model.name or "",
        product_name=db_model.product_name or "",
        material_type=db_model.material_type or "",
        delivery_period=db_model.delivery_period or 0,
        special_delivery_period=db_model.special_delivery_period or 0,
        reliability=db_model.reliability or 0.0,
        product_quality=db_model.product_quality or 0.0,
        cost=db_model.cost or 0,
        special_delivery_cost=db_model.special_delivery_cost or 0,
    )


def supplier_domain_to_db(
    domain_entity: Supplier, db_model: Optional[SupplierDB] = None
) -> SupplierDB:
    """Преобразует доменную сущность Supplier в SQLAlchemy модель."""
    if db_model is None:
        db_model = SupplierDB()

    db_model.name = domain_entity.name
    db_model.product_name = domain_entity.product_name
    db_model.material_type = domain_entity.material_type
    db_model.delivery_period = domain_entity.delivery_period
    db_model.special_delivery_period = domain_entity.special_delivery_period
    db_model.reliability = domain_entity.reliability
    db_model.product_quality = domain_entity.product_quality
    db_model.cost = domain_entity.cost
    db_model.special_delivery_cost = domain_entity.special_delivery_cost

    if domain_entity.supplier_id:
        db_model.supplier_id = domain_entity.supplier_id

    return db_model


def equipment_db_to_domain(db_model: EquipmentDB) -> Equipment:
    """Преобразует SQLAlchemy модель Equipment в доменную сущность."""
    return Equipment(
        equipment_id=str(db_model.equipment_id) if db_model.equipment_id else "",
        name=db_model.name or "",
        equipment_type=db_model.equipment_type or "",
        reliability=db_model.reliability or 0.0,
        maintenance_cost=db_model.maintenance_cost or 0,
        cost=db_model.cost or 0,
        repair_cost=db_model.repair_cost or 0,
        repair_time=db_model.repair_time or 0,
        maintenance_period=db_model.maintenance_period or 0,  # обязательное поле
    )


def equipment_domain_to_db(
    domain_entity: Equipment, db_model: Optional[EquipmentDB] = None
) -> EquipmentDB:
    """Преобразует доменную сущность Equipment в SQLAlchemy модель."""
    if db_model is None:
        db_model = EquipmentDB()

    db_model.name = domain_entity.name
    db_model.equipment_type = domain_entity.equipment_type
    db_model.reliability = domain_entity.reliability
    db_model.maintenance_cost = domain_entity.maintenance_cost
    db_model.cost = domain_entity.cost
    db_model.repair_cost = domain_entity.repair_cost
    db_model.repair_time = domain_entity.repair_time

    # maintenance_period может быть None в домене, но в DB он обязателен
    # Используем значение из домена или 0 по умолчанию
    db_model.maintenance_period = (
        domain_entity.maintenance_period
        if domain_entity.maintenance_period is not None
        else 0
    )

    if domain_entity.equipment_id:
        db_model.equipment_id = domain_entity.equipment_id

    return db_model


def consumer_db_to_domain(db_model: ConsumerDB) -> Consumer:
    """Преобразует SQLAlchemy модель Consumer в доменную сущность."""
    # В БД type - это enum ConsumerType, в домене - строка
    type_value = (
        db_model.type.value
        if hasattr(db_model.type, "value")
        else str(db_model.type or "")
    )

    return Consumer(
        consumer_id=str(db_model.consumer_id) if db_model.consumer_id else "",
        name=db_model.name or "",
        type=type_value,
    )


def consumer_domain_to_db(
    domain_entity: Consumer, db_model: Optional[ConsumerDB] = None
) -> ConsumerDB:
    """Преобразует доменную сущность Consumer в SQLAlchemy модель."""
    if db_model is None:
        db_model = ConsumerDB()

    db_model.name = domain_entity.name

    # В домене type - строка, в БД - enum ConsumerType
    if isinstance(domain_entity.type, str):
        try:
            db_model.type = ConsumerType(domain_entity.type)
        except (ValueError, KeyError):
            db_model.type = ConsumerType.NOT_GOVERMANT
    else:
        db_model.type = domain_entity.type

    if domain_entity.consumer_id:
        db_model.consumer_id = domain_entity.consumer_id

    return db_model


async def workplace_db_to_domain(
    db_model: WorkplaceDB,
    session: AsyncSession,
) -> Workplace:
    """Преобразует SQLAlchemy модель Workplace в доменную сущность (асинхронная версия)."""
    # В БД required_qualification - это enum Qualification, в домене - int
    qualification_value = (
        db_model.required_qualification.value
        if hasattr(db_model.required_qualification, "value")
        else db_model.required_qualification
    )

    workplace = Workplace(
        workplace_id=str(db_model.workplace_id) if db_model.workplace_id else "",
        workplace_name=db_model.name or "",
        required_speciality=(
            db_model.required_speciality.value
            if hasattr(db_model.required_speciality, "value")
            else str(db_model.required_speciality or "")
        ),
        required_qualification=qualification_value,
        required_equipment=db_model.required_equipment or "",
        required_stages=db_model.required_stages or [],
    )

    # worker и equipment устанавливаются только во время симуляции, не хранятся в БД
    workplace.worker = None
    workplace.equipment = None

    return workplace


def workplace_domain_to_db(
    domain_entity: Workplace, db_model: Optional[WorkplaceDB] = None
) -> WorkplaceDB:
    """Преобразует доменную сущность Workplace в SQLAlchemy модель."""
    if db_model is None:
        db_model = WorkplaceDB()

    db_model.name = domain_entity.workplace_name

    # Преобразуем specialization из строки в enum
    if isinstance(domain_entity.required_speciality, str):
        try:
            db_model.required_speciality = Specialization(
                domain_entity.required_speciality
            )
        except ValueError:
            db_model.required_speciality = Specialization.NONE
    else:
        db_model.required_speciality = domain_entity.required_speciality

    # required_qualification теперь int - преобразуем в enum для БД
    if isinstance(domain_entity.required_qualification, int):
        from domain import Qualification

        try:
            db_model.required_qualification = Qualification(
                domain_entity.required_qualification
            )
        except (ValueError, KeyError):
            db_model.required_qualification = Qualification.I
    else:
        db_model.required_qualification = domain_entity.required_qualification

    # worker и equipment не хранятся в БД, устанавливаются только во время симуляции
    db_model.required_equipment = domain_entity.required_equipment
    db_model.required_stages = domain_entity.required_stages or []

    # Устанавливаем значения по умолчанию для полей, которых нет в доменной модели
    db_model.is_start_node = False
    db_model.is_end_node = False
    db_model.next_workplace_ids = []

    if domain_entity.workplace_id:
        db_model.workplace_id = domain_entity.workplace_id

    return db_model


async def tender_db_to_domain(db_model: TenderDB, session: AsyncSession) -> Tender:
    """Преобразует SQLAlchemy модель Tender в доменную сущность (асинхронная версия)."""
    from .models import Consumer as ConsumerDB

    # Загружаем Consumer
    consumer_db = None
    if db_model.consumer_id:
        result = await session.execute(
            select(ConsumerDB).where(ConsumerDB.consumer_id == db_model.consumer_id)
        )
        consumer_db = result.scalar_one_or_none()

    if consumer_db:
        consumer = consumer_db_to_domain(consumer_db)
    else:
        # Создаем Consumer с минимальной информацией
        consumer = Consumer(
            consumer_id=str(db_model.consumer_id) if db_model.consumer_id else "",
            name="",
            type="",  # строка, не enum
        )

    # В БД payment_form - это enum PaymentForm, в домене - строка
    payment_form_value = (
        db_model.payment_form.value
        if hasattr(db_model.payment_form, "value")
        else str(db_model.payment_form or "")
    )

    tender = Tender(
        tender_id=str(db_model.tender_id) if db_model.tender_id else "",
        consumer=consumer,
        cost=db_model.cost or 0,
        quantity_of_products=db_model.quantity_of_products or 0,
        penalty_per_day=db_model.penalty_per_day or 0,
        warranty_years=db_model.warranty_years or 0,
        payment_form=payment_form_value,
    )

    return tender


def tender_domain_to_db(
    domain_entity: Tender, db_model: Optional[TenderDB] = None
) -> TenderDB:
    """Преобразует доменную сущность Tender в SQLAlchemy модель."""
    if db_model is None:
        db_model = TenderDB()

    # Извлекаем consumer_id из связанного объекта
    if domain_entity.consumer and domain_entity.consumer.consumer_id:
        db_model.consumer_id = domain_entity.consumer.consumer_id

    db_model.cost = domain_entity.cost
    db_model.quantity_of_products = domain_entity.quantity_of_products
    db_model.penalty_per_day = domain_entity.penalty_per_day
    db_model.warranty_years = domain_entity.warranty_years

    # В домене payment_form - строка, в БД - enum PaymentForm
    if isinstance(domain_entity.payment_form, str):
        from domain import PaymentForm

        try:
            db_model.payment_form = PaymentForm(domain_entity.payment_form)
        except (ValueError, KeyError):
            db_model.payment_form = PaymentForm.CASH
    else:
        db_model.payment_form = domain_entity.payment_form

    if domain_entity.tender_id:
        db_model.tender_id = domain_entity.tender_id

    return db_model


# Repository implementations


class WorkerRepository(AbstractRepository[Worker]):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, model: Worker) -> Union[Worker, None]:
        try:
            from domain import Logist
            from sqlalchemy import text

            db_model = None
            existing_row = None
            if model.worker_id:
                # Проверяем существование записи - используем прямой SQL для обхода полиморфной загрузки
                sql_query = text(
                    """
                    SELECT worker_id, name, qualification, specialization, salary, 
                           type, speed, vehicle_type, created_at, updated_at
                    FROM workers 
                    WHERE worker_id = :worker_id
                    """
                )
                result = await self.session.execute(
                    sql_query, {"worker_id": model.worker_id}
                )
                existing_row = result.fetchone()

                if existing_row:
                    # Создаем новый WorkerDB объект из данных, полученных через SQL
                    # Это нужно, так как worker_domain_to_db ожидает WorkerDB объект
                    db_model = WorkerDB()
                    db_model.worker_id = existing_row.worker_id
                    db_model.name = existing_row.name
                    # Преобразуем qualification
                    from domain import Qualification, Specialization

                    # qualification может быть enum, int (числовое значение), или строка (имя enum 'I', 'II', etc.)
                    if isinstance(existing_row.qualification, Qualification):
                        db_model.qualification = existing_row.qualification
                    elif isinstance(existing_row.qualification, int):
                        try:
                            db_model.qualification = Qualification(existing_row.qualification)
                        except (ValueError, KeyError):
                            db_model.qualification = Qualification.I
                    elif isinstance(existing_row.qualification, str):
                        # Если это строка, пытаемся найти enum по имени (например 'I', 'II')
                        try:
                            db_model.qualification = Qualification[existing_row.qualification]
                        except (ValueError, KeyError):
                            # Если не нашли по имени, пытаемся как число
                            try:
                                db_model.qualification = Qualification(
                                    int(existing_row.qualification)
                                )
                            except (ValueError, TypeError):
                                db_model.qualification = Qualification.I
                    else:
                        db_model.qualification = Qualification.I
                    # Преобразуем specialization
                    if isinstance(existing_row.specialization, Specialization):
                        db_model.specialization = existing_row.specialization
                    elif isinstance(existing_row.specialization, str):
                        try:
                            db_model.specialization = Specialization(existing_row.specialization)
                        except ValueError:
                            db_model.specialization = Specialization.NONE
                    else:
                        db_model.specialization = Specialization.NONE
                    db_model.salary = existing_row.salary
                    db_model.type = existing_row.type
                    db_model.speed = existing_row.speed if existing_row.speed is not None else 0
                    # Преобразуем vehicle_type
                    from domain import VehicleType

                    if isinstance(existing_row.vehicle_type, VehicleType):
                        db_model.vehicle_type = existing_row.vehicle_type
                    elif existing_row.vehicle_type is not None:
                        try:
                            db_model.vehicle_type = VehicleType(existing_row.vehicle_type)
                        except (ValueError, KeyError):
                            db_model.vehicle_type = VehicleType.NONE
                    else:
                        db_model.vehicle_type = VehicleType.NONE
                    db_model.created_at = existing_row.created_at
                    db_model.updated_at = existing_row.updated_at

            db_model = worker_domain_to_db(model, db_model)
            logger.debug(
                f"Saving worker with type='{db_model.type}', worker_id={db_model.worker_id}"
            )

            if model.worker_id and existing_row:
                # Обновление: используем прямой SQL UPDATE чтобы избежать полиморфной загрузки
                from domain import Qualification, Specialization, VehicleType

                update_query = text(
                    """
                    UPDATE workers 
                    SET name = :name,
                        qualification = CAST(:qualification AS qualification_enum),
                        specialization = CAST(:specialization AS specialization_enum),
                        salary = :salary,
                        type = :type,
                        speed = :speed,
                        vehicle_type = CAST(:vehicle_type AS vehicle_type_enum),
                        updated_at = :updated_at
                    WHERE worker_id = :worker_id
                    RETURNING worker_id, name, qualification, specialization, salary, 
                              type, speed, vehicle_type, created_at, updated_at
                """
                )

                # Преобразуем enum в строковые значения для SQL CAST
                # PostgreSQL enum требует строковое представление
                if isinstance(db_model.qualification, Qualification):
                    # Qualification - это int Enum, но в PostgreSQL хранится как строка имени enum
                    # Используем имя enum (например, "I" вместо 1)
                    qual_value = db_model.qualification.name
                else:
                    # Если это уже строка или число, пробуем преобразовать
                    if isinstance(db_model.qualification, int):
                        try:
                            qual_enum = Qualification(db_model.qualification)
                            qual_value = qual_enum.name
                        except (ValueError, KeyError):
                            qual_value = "I"  # Значение по умолчанию
                    else:
                        qual_value = str(db_model.qualification)

                # Для PostgreSQL enum нужно использовать имя enum, а не значение
                # Проверяем, как хранится в БД - вероятно по имени
                if isinstance(db_model.specialization, Specialization):
                    # Используем имя enum (NONE, ASSEMBLER и т.д.) вместо значения
                    spec_value = db_model.specialization.name
                else:
                    # Если это строка, пытаемся найти соответствующий enum
                    if isinstance(db_model.specialization, str):
                        try:
                            # Пробуем найти по значению
                            spec_enum = Specialization(db_model.specialization)
                            spec_value = spec_enum.name
                        except (ValueError, KeyError):
                            try:
                                # Пробуем найти по имени
                                spec_enum = Specialization[
                                    db_model.specialization.upper()
                                ]
                                spec_value = spec_enum.name
                            except (ValueError, KeyError):
                                spec_value = "NONE"  # Значение по умолчанию
                    else:
                        spec_value = "NONE"

                if isinstance(db_model.vehicle_type, VehicleType):
                    # Используем имя enum (NONE, VAN, TRUCK и т.д.)
                    vehicle_value = db_model.vehicle_type.name
                elif db_model.vehicle_type is not None:
                    # Если это строка, пытаемся найти соответствующий enum
                    if isinstance(db_model.vehicle_type, str):
                        try:
                            # Пробуем найти по значению
                            vehicle_enum = VehicleType(db_model.vehicle_type)
                            vehicle_value = vehicle_enum.name
                        except (ValueError, KeyError):
                            try:
                                # Пробуем найти по имени
                                vehicle_enum = VehicleType[
                                    db_model.vehicle_type.upper()
                                ]
                                vehicle_value = vehicle_enum.name
                            except (ValueError, KeyError):
                                vehicle_value = "NONE"
                    else:
                        vehicle_value = "NONE"
                else:
                    vehicle_value = "NONE"  # Значение по умолчанию

                result = await self.session.execute(
                    update_query,
                    {
                        "worker_id": db_model.worker_id,
                        "name": db_model.name,
                        "qualification": qual_value,
                        "specialization": spec_value,
                        "salary": db_model.salary,
                        "type": db_model.type,
                        "speed": db_model.speed if db_model.speed is not None else 0,
                        "vehicle_type": vehicle_value,
                        "updated_at": datetime.now(timezone.utc).replace(tzinfo=None),
                    },
                )
                updated_row = result.fetchone()
                await self.session.commit()

                # Преобразуем обновленную строку обратно в объект для возврата
                if updated_row:

                    class WorkerRow:
                        def __init__(self, row):
                            self.worker_id = row.worker_id
                            self.name = row.name
                            self.qualification = row.qualification
                            self.specialization = row.specialization
                            self.salary = row.salary
                            self.type = row.type
                            self.speed = row.speed
                            self.vehicle_type = row.vehicle_type

                    db_model = WorkerRow(updated_row)
            else:
                # Создание новой записи - используем обычный ORM add
                # Это происходит когда worker_id не указан ИЛИ когда worker_id указан, но записи нет в БД
                self.session.add(db_model)
                await self.session.flush()
                await self.session.commit()
                
                # После INSERT используем прямой SQL запрос для получения данных, как после UPDATE
                # Это гарантирует консистентность и правильное чтение type поля
                sql_query = text(
                    """
                    SELECT worker_id, name, qualification, specialization, salary, 
                           type, speed, vehicle_type, created_at, updated_at
                    FROM workers 
                    WHERE worker_id = :worker_id
                    """
                )
                result = await self.session.execute(
                    sql_query, {"worker_id": db_model.worker_id}
                )
                inserted_row = result.fetchone()
                
                if inserted_row:
                    class WorkerRow:
                        def __init__(self, row):
                            self.worker_id = row.worker_id
                            self.name = row.name
                            self.qualification = row.qualification
                            self.specialization = row.specialization
                            self.salary = row.salary
                            self.type = row.type
                            self.speed = row.speed
                            self.vehicle_type = row.vehicle_type
                    
                    db_model = WorkerRow(inserted_row)
                else:
                    # Если не удалось получить через SQL, используем refresh
                    await self.session.refresh(db_model)

            # Проверяем, что тип действительно сохранился
            logger.debug(
                f"Saved worker type after commit: '{db_model.type}', worker_id={db_model.worker_id}"
            )

            # Возвращаем правильный тип в зависимости от type в БД
            if db_model.type == "logist":
                return worker_db_to_logist_domain(db_model)
            else:
                return worker_db_to_domain(db_model)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error saving Worker: {e}", exc_info=True)
            return None

    async def get(self, id: Union[UUID, str]) -> Union[Worker, None]:
        try:
            from sqlalchemy import text

            # worker_id теперь строка
            worker_id = str(id) if id else ""
            # Используем прямой SQL запрос для обхода полиморфной загрузки
            # SQLAlchemy пытается использовать полиморфную загрузку, которая не работает
            # с type="logist", так как нет соответствующего polymorphic_identity
            sql_query = text(
                """
                SELECT worker_id, name, qualification, specialization, salary, 
                       type, speed, vehicle_type, created_at, updated_at
                FROM workers 
                WHERE worker_id = :worker_id
                """
            )
            result = await self.session.execute(sql_query, {"worker_id": worker_id})
            row = result.fetchone()

            if row is None:
                return None

            # Преобразуем строку в простой объект для чтения данных
            # Используем тот же подход, что и в get_all
            from domain import Qualification, Specialization, VehicleType

            class WorkerRow:
                """Простой класс для хранения данных из БД без полиморфной загрузки"""

                def __init__(self, row):
                    self.worker_id = row.worker_id
                    self.name = row.name

                    # Преобразуем qualification в Enum
                    # qualification из SQL может быть строкой (имя enum 'I', 'II', etc.) или enum
                    if isinstance(row.qualification, Qualification):
                        self.qualification = row.qualification
                    elif isinstance(row.qualification, int):
                        try:
                            self.qualification = Qualification(row.qualification)
                        except (ValueError, KeyError):
                            self.qualification = Qualification.I
                    elif isinstance(row.qualification, str):
                        # Если это строка вроде 'I', 'II', 'IV', пробуем найти по имени
                        try:
                            self.qualification = Qualification[row.qualification]
                        except (ValueError, KeyError):
                            # Если не нашли по имени, пробуем как число
                            try:
                                self.qualification = Qualification(int(row.qualification))
                            except (ValueError, KeyError, TypeError):
                                self.qualification = Qualification.I
                    else:
                        self.qualification = Qualification.I

                    # Преобразуем specialization
                    # specialization из SQL может быть строкой (имя enum 'ASSEMBLER') или enum
                    if isinstance(row.specialization, Specialization):
                        self.specialization = row.specialization
                    elif isinstance(row.specialization, str):
                        try:
                            # Пробуем найти по имени enum (например 'ASSEMBLER')
                            self.specialization = Specialization[row.specialization]
                        except (ValueError, KeyError):
                            try:
                                # Пробуем найти по значению enum (например 'Слесарь-сборщик')
                                self.specialization = Specialization(row.specialization)
                            except (ValueError, KeyError):
                                self.specialization = Specialization.NONE
                    else:
                        self.specialization = Specialization.NONE

                    self.salary = row.salary
                    self.type = row.type
                    self.speed = row.speed if row.speed is not None else 0
                    
                    # Преобразуем vehicle_type в Enum
                    # vehicle_type из SQL может быть строкой (имя enum 'VAN') или enum
                    if isinstance(row.vehicle_type, VehicleType):
                        self.vehicle_type = row.vehicle_type
                    elif isinstance(row.vehicle_type, str):
                        try:
                            # Пробуем найти по имени enum (например 'VAN')
                            self.vehicle_type = VehicleType[row.vehicle_type]
                        except (ValueError, KeyError):
                            try:
                                # Пробуем найти по значению enum (например 'Грузовой фургон')
                                self.vehicle_type = VehicleType(row.vehicle_type)
                            except (ValueError, KeyError):
                                self.vehicle_type = VehicleType.NONE
                    elif row.vehicle_type is None:
                        self.vehicle_type = VehicleType.NONE
                    else:
                        self.vehicle_type = VehicleType.NONE

            db_model = WorkerRow(row)
            # Возвращаем правильный тип в зависимости от type в БД
            if db_model.type == "logist":
                return worker_db_to_logist_domain(db_model)
            else:
                return worker_db_to_domain(db_model)
        except Exception as e:
            logger.error(f"Error getting Worker: {e}", exc_info=True)
            return None

    async def delete(self, id: Union[UUID, str]) -> Union[Worker, None]:
        try:
            from sqlalchemy import text

            # worker_id теперь строка
            worker_id = str(id) if id else ""

            # Сначала получаем данные через прямой SQL запрос
            sql_query = text(
                """
                SELECT worker_id, name, qualification, specialization, salary, 
                       type, speed, vehicle_type, created_at, updated_at
                FROM workers 
                WHERE worker_id = :worker_id
                """
            )
            result = await self.session.execute(sql_query, {"worker_id": worker_id})
            row = result.fetchone()

            if row is None:
                return None

            # Преобразуем строку в простой объект
            from domain import Qualification, Specialization, VehicleType

            class WorkerRow:
                """Простой класс для хранения данных из БД без полиморфной загрузки"""

                def __init__(self, row):
                    self.worker_id = row.worker_id
                    self.name = row.name

                    # Преобразуем qualification в Enum
                    # qualification из SQL может быть строкой (имя enum 'I', 'II', etc.) или enum
                    if isinstance(row.qualification, Qualification):
                        self.qualification = row.qualification
                    elif isinstance(row.qualification, int):
                        try:
                            self.qualification = Qualification(row.qualification)
                        except (ValueError, KeyError):
                            self.qualification = Qualification.I
                    elif isinstance(row.qualification, str):
                        # Если это строка вроде 'I', 'II', 'IV', пробуем найти по имени
                        try:
                            self.qualification = Qualification[row.qualification]
                        except (ValueError, KeyError):
                            # Если не нашли по имени, пробуем как число
                            try:
                                self.qualification = Qualification(int(row.qualification))
                            except (ValueError, KeyError, TypeError):
                                self.qualification = Qualification.I
                    else:
                        self.qualification = Qualification.I

                    # Преобразуем specialization
                    # specialization из SQL может быть строкой (имя enum 'ASSEMBLER') или enum
                    if isinstance(row.specialization, Specialization):
                        self.specialization = row.specialization
                    elif isinstance(row.specialization, str):
                        try:
                            # Пробуем найти по имени enum (например 'ASSEMBLER')
                            self.specialization = Specialization[row.specialization]
                        except (ValueError, KeyError):
                            try:
                                # Пробуем найти по значению enum (например 'Слесарь-сборщик')
                                self.specialization = Specialization(row.specialization)
                            except (ValueError, KeyError):
                                self.specialization = Specialization.NONE
                    else:
                        self.specialization = Specialization.NONE

                    self.salary = row.salary
                    self.type = row.type
                    self.speed = row.speed if row.speed is not None else 0
                    
                    # Преобразуем vehicle_type в Enum
                    # vehicle_type из SQL может быть строкой (имя enum 'VAN') или enum
                    if isinstance(row.vehicle_type, VehicleType):
                        self.vehicle_type = row.vehicle_type
                    elif isinstance(row.vehicle_type, str):
                        try:
                            # Пробуем найти по имени enum (например 'VAN')
                            self.vehicle_type = VehicleType[row.vehicle_type]
                        except (ValueError, KeyError):
                            try:
                                # Пробуем найти по значению enum (например 'Грузовой фургон')
                                self.vehicle_type = VehicleType(row.vehicle_type)
                            except (ValueError, KeyError):
                                self.vehicle_type = VehicleType.NONE
                    elif row.vehicle_type is None:
                        self.vehicle_type = VehicleType.NONE
                    else:
                        self.vehicle_type = VehicleType.NONE

            db_model = WorkerRow(row)

            # Возвращаем правильный тип в зависимости от type в БД
            if db_model.type == "logist":
                domain_entity = worker_db_to_logist_domain(db_model)
            else:
                domain_entity = worker_db_to_domain(db_model)

            # Удаляем через прямой SQL запрос
            delete_query = text("DELETE FROM workers WHERE worker_id = :worker_id")
            await self.session.execute(delete_query, {"worker_id": worker_id})
            await self.session.commit()

            return domain_entity
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting Worker: {e}", exc_info=True)
            return None

    async def get_all(self, worker_type: Optional[str] = None) -> List[Worker]:
        """Получает всех работников, опционально фильтруя по типу."""
        try:
            from domain import Logist
            from sqlalchemy import text

            # Используем прямой SQL запрос для обхода полиморфной загрузки
            # SQLAlchemy пытается использовать полиморфную загрузку, которая не работает
            # с type="logist", так как нет соответствующего polymorphic_identity
            if worker_type:
                sql_query = text(
                    """
                    SELECT worker_id, name, qualification, specialization, salary, 
                           type, speed, vehicle_type, created_at, updated_at
                    FROM workers 
                    WHERE type = :worker_type
                    """
                )
                params = {"worker_type": worker_type}
                logger.debug(f"Filtering workers by type='{worker_type}'")
            else:
                sql_query = text(
                    """
                    SELECT worker_id, name, qualification, specialization, salary, 
                           type, speed, vehicle_type, created_at, updated_at
                    FROM workers
                    """
                )
                params = {}

            result = await self.session.execute(sql_query, params)
            rows = result.fetchall()

            # Преобразуем строки в простые объекты для чтения данных
            # Используем type для создания простого класса, имитирующего WorkerDB
            from domain import Qualification, Specialization, VehicleType

            class WorkerRow:
                """Простой класс для хранения данных из БД без полиморфной загрузки"""

                def __init__(self, row):
                    self.worker_id = row.worker_id
                    self.name = row.name

                    # Преобразуем qualification в Enum
                    if isinstance(row.qualification, Qualification):
                        self.qualification = row.qualification
                    elif isinstance(row.qualification, int):
                        try:
                            self.qualification = Qualification(row.qualification)
                        except (ValueError, KeyError):
                            self.qualification = Qualification.I
                    elif isinstance(row.qualification, str):
                        # Если это строка вроде 'I', пробуем найти по имени
                        try:
                            self.qualification = Qualification[row.qualification]
                        except (ValueError, KeyError):
                            # Если не удалось, пробуем как число
                            try:
                                self.qualification = Qualification(
                                    int(row.qualification)
                                )
                            except (ValueError, KeyError):
                                self.qualification = Qualification.I
                    else:
                        self.qualification = Qualification.I

                    # Преобразуем specialization в Enum
                    # specialization из SQL может быть строкой (имя enum 'ASSEMBLER') или enum
                    if isinstance(row.specialization, Specialization):
                        self.specialization = row.specialization
                    elif isinstance(row.specialization, str):
                        try:
                            # Пробуем найти по имени enum (например 'ASSEMBLER')
                            self.specialization = Specialization[row.specialization]
                        except (ValueError, KeyError):
                            try:
                                # Пробуем найти по значению enum (например 'Слесарь-сборщик')
                                self.specialization = Specialization(row.specialization)
                            except (ValueError, KeyError):
                                self.specialization = Specialization.NONE
                    else:
                        self.specialization = Specialization.NONE

                    self.salary = row.salary
                    self.type = row.type
                    self.speed = row.speed

                    # Преобразуем vehicle_type в Enum
                    # vehicle_type из SQL может быть строкой (имя enum 'VAN') или enum
                    if isinstance(row.vehicle_type, VehicleType):
                        self.vehicle_type = row.vehicle_type
                    elif isinstance(row.vehicle_type, str):
                        try:
                            # Пробуем найти по имени enum (например 'VAN')
                            self.vehicle_type = VehicleType[row.vehicle_type]
                        except (ValueError, KeyError):
                            try:
                                # Пробуем найти по значению enum (например 'Грузовой фургон')
                                self.vehicle_type = VehicleType(row.vehicle_type)
                            except (ValueError, KeyError):
                                self.vehicle_type = VehicleType.NONE
                    elif row.vehicle_type is None:
                        self.vehicle_type = VehicleType.NONE
                    else:
                        self.vehicle_type = VehicleType.NONE

                    self.created_at = row.created_at
                    self.updated_at = row.updated_at

            db_models = [WorkerRow(row) for row in rows]

            logger.debug(f"Found {len(db_models)} workers in database")

            domain_entities = []
            for db_model in db_models:
                if db_model.type == "logist":
                    domain_entities.append(worker_db_to_logist_domain(db_model))
                else:
                    domain_entities.append(worker_db_to_domain(db_model))

            logger.debug(f"Converted {len(domain_entities)} workers to domain entities")
            return domain_entities
        except Exception as e:
            logger.error(
                f"Error getting Workers by type {worker_type}: {e}", exc_info=True
            )
            return []

    async def get_all_by_type(self, worker_type: str) -> List[Worker]:
        """Получает всех работников по типу (worker или logist)."""
        try:
            result = await self.session.execute(
                select(WorkerDB).where(WorkerDB.type == worker_type)
            )
            db_models = result.scalars().all()
            return [worker_db_to_domain(db_model) for db_model in db_models]
        except Exception as e:
            logger.error(
                f"Error getting Workers by type {worker_type}: {e}", exc_info=True
            )
            return []


class SupplierRepository(AbstractRepository[Supplier]):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, model: Supplier) -> Union[Supplier, None]:
        try:
            db_model = None
            if model.supplier_id:
                result = await self.session.execute(
                    select(SupplierDB).where(
                        SupplierDB.supplier_id == model.supplier_id
                    )
                )
                db_model = result.scalar_one_or_none()

            db_model = supplier_domain_to_db(model, db_model)
            self.session.add(db_model)
            await self.session.commit()
            await self.session.refresh(db_model)

            return supplier_db_to_domain(db_model)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error saving Supplier: {e}", exc_info=True)
            return None

    async def get(self, id: Union[UUID, str]) -> Union[Supplier, None]:
        try:
            # supplier_id теперь строка
            supplier_id = str(id) if id else ""
            result = await self.session.execute(
                select(SupplierDB).where(SupplierDB.supplier_id == supplier_id)
            )
            db_model = result.scalar_one_or_none()
            if db_model is None:
                return None
            return supplier_db_to_domain(db_model)
        except Exception as e:
            logger.error(f"Error getting Supplier: {e}", exc_info=True)
            return None

    async def delete(self, id: Union[UUID, str]) -> Union[Supplier, None]:
        try:
            # supplier_id теперь строка
            supplier_id = str(id) if id else ""
            result = await self.session.execute(
                select(SupplierDB).where(SupplierDB.supplier_id == supplier_id)
            )
            db_model = result.scalar_one_or_none()
            if db_model:
                domain_entity = supplier_db_to_domain(db_model)
                await self.session.delete(db_model)
                await self.session.commit()
                return domain_entity
            return None
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting Supplier: {e}", exc_info=True)
            return None

    async def get_all(self) -> List[Supplier]:
        """Получает всех поставщиков."""
        try:
            result = await self.session.execute(select(SupplierDB))
            db_models = result.scalars().all()
            return [supplier_db_to_domain(db_model) for db_model in db_models]
        except Exception as e:
            logger.error(f"Error getting all Suppliers: {e}", exc_info=True)
            return []

    async def get_distinct_product_names(self) -> List[str]:
        """Получает уникальные названия продуктов."""
        try:
            from sqlalchemy import distinct

            result = await self.session.execute(
                select(distinct(SupplierDB.product_name))
            )
            product_names = result.scalars().all()
            return [name for name in product_names if name]
        except Exception as e:
            logger.error(f"Error getting distinct product names: {e}", exc_info=True)
            return []


class EquipmentRepository(AbstractRepository[Equipment]):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, model: Equipment) -> Union[Equipment, None]:
        try:
            db_model = None
            if model.equipment_id:
                result = await self.session.execute(
                    select(EquipmentDB).where(
                        EquipmentDB.equipment_id == model.equipment_id
                    )
                )
                db_model = result.scalar_one_or_none()

            db_model = equipment_domain_to_db(model, db_model)
            self.session.add(db_model)
            await self.session.commit()
            await self.session.refresh(db_model)

            return equipment_db_to_domain(db_model)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error saving Equipment: {e}", exc_info=True)
            return None

    async def get(self, id: Union[UUID, str]) -> Union[Equipment, None]:
        try:
            # equipment_id теперь строка
            equipment_id = str(id) if id else ""
            result = await self.session.execute(
                select(EquipmentDB).where(EquipmentDB.equipment_id == equipment_id)
            )
            db_model = result.scalar_one_or_none()
            if db_model is None:
                return None
            return equipment_db_to_domain(db_model)
        except Exception as e:
            logger.error(f"Error getting Equipment: {e}", exc_info=True)
            return None

    async def delete(self, id: Union[UUID, str]) -> Union[Equipment, None]:
        try:
            # equipment_id теперь строка
            equipment_id = str(id) if id else ""
            result = await self.session.execute(
                select(EquipmentDB).where(EquipmentDB.equipment_id == equipment_id)
            )
            db_model = result.scalar_one_or_none()
            if db_model:
                domain_entity = equipment_db_to_domain(db_model)
                await self.session.delete(db_model)
                await self.session.commit()
                return domain_entity
            return None
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting Equipment: {e}", exc_info=True)
            return None

    async def get_all(self) -> List[Equipment]:
        """Получает все оборудование."""
        try:
            result = await self.session.execute(select(EquipmentDB))
            db_models = result.scalars().all()
            return [equipment_db_to_domain(db_model) for db_model in db_models]
        except Exception as e:
            logger.error(f"Error getting all Equipment: {e}", exc_info=True)
            return []

    async def get_distinct_equipment_types(self) -> List[str]:
        """Получает уникальные типы оборудования."""
        try:
            from sqlalchemy import distinct

            result = await self.session.execute(
                select(distinct(EquipmentDB.equipment_type))
            )
            equipment_types = result.scalars().all()
            return [eq_type for eq_type in equipment_types if eq_type]
        except Exception as e:
            logger.error(f"Error getting distinct equipment types: {e}", exc_info=True)
            return []


class WorkplaceRepository(AbstractRepository[Workplace]):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, model: Workplace) -> Union[Workplace, None]:
        try:
            db_model = None
            if model.workplace_id:
                result = await self.session.execute(
                    select(WorkplaceDB).where(
                        WorkplaceDB.workplace_id == model.workplace_id
                    )
                )
                db_model = result.scalar_one_or_none()

            db_model = workplace_domain_to_db(model, db_model)
            self.session.add(db_model)
            await self.session.commit()
            await self.session.refresh(db_model)

            return await workplace_db_to_domain(db_model, self.session)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error saving Workplace: {e}", exc_info=True)
            return None

    async def get(self, id: Union[UUID, str]) -> Union[Workplace, None]:
        try:
            # workplace_id теперь строка
            workplace_id = str(id) if id else ""
            result = await self.session.execute(
                select(WorkplaceDB).where(WorkplaceDB.workplace_id == workplace_id)
            )
            db_model = result.scalar_one_or_none()
            if db_model is None:
                return None
            return await workplace_db_to_domain(db_model, self.session)
        except Exception as e:
            logger.error(f"Error getting Workplace: {e}", exc_info=True)
            return None

    async def delete(self, id: Union[UUID, str]) -> Union[Workplace, None]:
        try:
            # workplace_id теперь строка
            workplace_id = str(id) if id else ""
            result = await self.session.execute(
                select(WorkplaceDB).where(WorkplaceDB.workplace_id == workplace_id)
            )
            db_model = result.scalar_one_or_none()
            if db_model:
                domain_entity = await workplace_db_to_domain(db_model, self.session)
                await self.session.delete(db_model)
                await self.session.commit()
                return domain_entity
            return None
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting Workplace: {e}", exc_info=True)
            return None

    async def get_all(self) -> List[Workplace]:
        """Получает все рабочие места."""
        try:
            result = await self.session.execute(select(WorkplaceDB))
            db_models = result.scalars().all()
            workplaces = []
            for db_model in db_models:
                workplace = await workplace_db_to_domain(db_model, self.session)
                workplaces.append(workplace)
            return workplaces
        except Exception as e:
            logger.error(f"Error getting all Workplaces: {e}", exc_info=True)
            return []


class ConsumerRepository(AbstractRepository[Consumer]):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, model: Consumer) -> Union[Consumer, None]:
        try:
            db_model = None
            if model.consumer_id:
                result = await self.session.execute(
                    select(ConsumerDB).where(
                        ConsumerDB.consumer_id == model.consumer_id
                    )
                )
                db_model = result.scalar_one_or_none()

            db_model = consumer_domain_to_db(model, db_model)
            self.session.add(db_model)
            await self.session.commit()
            await self.session.refresh(db_model)

            return consumer_db_to_domain(db_model)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error saving Consumer: {e}", exc_info=True)
            return None

    async def get(self, id: Union[UUID, str]) -> Union[Consumer, None]:
        try:
            # consumer_id теперь строка
            consumer_id = str(id) if id else ""
            result = await self.session.execute(
                select(ConsumerDB).where(ConsumerDB.consumer_id == consumer_id)
            )
            db_model = result.scalar_one_or_none()
            if db_model is None:
                return None
            return consumer_db_to_domain(db_model)
        except Exception as e:
            logger.error(f"Error getting Consumer: {e}", exc_info=True)
            return None

    async def delete(self, id: Union[UUID, str]) -> Union[Consumer, None]:
        try:
            # consumer_id теперь строка
            consumer_id = str(id) if id else ""
            result = await self.session.execute(
                select(ConsumerDB).where(ConsumerDB.consumer_id == consumer_id)
            )
            db_model = result.scalar_one_or_none()
            if db_model:
                domain_entity = consumer_db_to_domain(db_model)
                await self.session.delete(db_model)
                await self.session.commit()
                return domain_entity
            return None
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting Consumer: {e}", exc_info=True)
            return None

    async def get_all(self) -> List[Consumer]:
        """Получает всех заказчиков."""
        try:
            result = await self.session.execute(select(ConsumerDB))
            db_models = result.scalars().all()
            return [consumer_db_to_domain(db_model) for db_model in db_models]
        except Exception as e:
            logger.error(f"Error getting all Consumers: {e}", exc_info=True)
            return []


class TenderRepository(AbstractRepository[Tender]):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, model: Tender) -> Union[Tender, None]:
        try:
            db_model = None
            if model.tender_id:
                result = await self.session.execute(
                    select(TenderDB).where(TenderDB.tender_id == model.tender_id)
                )
                db_model = result.scalar_one_or_none()

            # Сначала сохраняем Consumer, если он новый
            if model.consumer and not model.consumer.consumer_id:
                consumer_repo = ConsumerRepository(self.session)
                saved_consumer = await consumer_repo.save(model.consumer)
                if saved_consumer:
                    model.consumer = saved_consumer

            db_model = tender_domain_to_db(model, db_model)
            self.session.add(db_model)
            await self.session.commit()
            await self.session.refresh(db_model)

            return await tender_db_to_domain(db_model, self.session)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error saving Tender: {e}", exc_info=True)
            return None

    async def get(self, id: Union[UUID, str]) -> Union[Tender, None]:
        try:
            # tender_id теперь строка
            tender_id = str(id) if id else ""
            result = await self.session.execute(
                select(TenderDB).where(TenderDB.tender_id == tender_id)
            )
            db_model = result.scalar_one_or_none()
            if db_model is None:
                return None
            return await tender_db_to_domain(db_model, self.session)
        except Exception as e:
            logger.error(f"Error getting Tender: {e}", exc_info=True)
            return None

    async def delete(self, id: Union[UUID, str]) -> Union[Tender, None]:
        try:
            # tender_id теперь строка
            tender_id = str(id) if id else ""
            result = await self.session.execute(
                select(TenderDB).where(TenderDB.tender_id == tender_id)
            )
            db_model = result.scalar_one_or_none()
            if db_model:
                domain_entity = await tender_db_to_domain(db_model, self.session)
                await self.session.delete(db_model)
                await self.session.commit()
                return domain_entity
            return None
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting Tender: {e}", exc_info=True)
            return None

    async def get_all(self) -> List[Tender]:
        """Получает все тендеры."""
        try:
            result = await self.session.execute(select(TenderDB))
            db_models = result.scalars().all()
            tenders = []
            for db_model in db_models:
                tender = await tender_db_to_domain(db_model, self.session)
                tenders.append(tender)
            return tenders
        except Exception as e:
            logger.error(f"Error getting all Tenders: {e}", exc_info=True)
            return []


# Mapper functions for LeanImprovement
def lean_improvement_db_to_domain(
    db_model: LeanImprovementDB,
) -> LeanImprovement:
    """Преобразует SQLAlchemy модель LeanImprovement в доменную сущность."""
    return LeanImprovement(
        improvement_id=str(db_model.improvement_id) if db_model.improvement_id else "",
        name=db_model.name or "",
        is_implemented=db_model.is_implemented or False,
        implementation_cost=db_model.implementation_cost or 0,
        efficiency_gain=db_model.efficiency_gain or 0.0,
    )


def lean_improvement_domain_to_db(
    domain_entity: LeanImprovement,
    db_model: Optional[LeanImprovementDB] = None,
) -> LeanImprovementDB:
    """Преобразует доменную сущность LeanImprovement в SQLAlchemy модель."""
    if db_model is None:
        db_model = LeanImprovementDB()

    db_model.name = domain_entity.name
    db_model.is_implemented = domain_entity.is_implemented
    db_model.implementation_cost = domain_entity.implementation_cost
    db_model.efficiency_gain = domain_entity.efficiency_gain

    if domain_entity.improvement_id:
        db_model.improvement_id = domain_entity.improvement_id

    return db_model


class LeanImprovementRepository(AbstractRepository[LeanImprovement]):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, model: LeanImprovement) -> Union[LeanImprovement, None]:
        try:
            db_model = None
            if model.improvement_id:
                result = await self.session.execute(
                    select(LeanImprovementDB).where(
                        LeanImprovementDB.improvement_id == model.improvement_id
                    )
                )
                db_model = result.scalar_one_or_none()

            db_model = lean_improvement_domain_to_db(model, db_model)
            self.session.add(db_model)
            await self.session.commit()
            await self.session.refresh(db_model)

            return lean_improvement_db_to_domain(db_model)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error saving LeanImprovement: {e}", exc_info=True)
            return None

    async def get(self, id: Union[UUID, str]) -> Union[LeanImprovement, None]:
        try:
            # improvement_id теперь строка
            improvement_id = str(id) if id else ""
            result = await self.session.execute(
                select(LeanImprovementDB).where(
                    LeanImprovementDB.improvement_id == improvement_id
                )
            )
            db_model = result.scalar_one_or_none()
            if db_model is None:
                return None
            return lean_improvement_db_to_domain(db_model)
        except Exception as e:
            logger.error(f"Error getting LeanImprovement: {e}", exc_info=True)
            return None

    async def delete(self, id: Union[UUID, str]) -> Union[LeanImprovement, None]:
        try:
            # improvement_id теперь строка
            improvement_id = str(id) if id else ""
            result = await self.session.execute(
                select(LeanImprovementDB).where(
                    LeanImprovementDB.improvement_id == improvement_id
                )
            )
            db_model = result.scalar_one_or_none()
            if db_model:
                domain_entity = lean_improvement_db_to_domain(db_model)
                await self.session.delete(db_model)
                await self.session.commit()
                return domain_entity
            return None
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting LeanImprovement: {e}", exc_info=True)
            return None

    async def get_all(self) -> List[LeanImprovement]:
        """Получает все LEAN улучшения."""
        try:
            result = await self.session.execute(select(LeanImprovementDB))
            db_models = result.scalars().all()
            return [lean_improvement_db_to_domain(db_model) for db_model in db_models]
        except Exception as e:
            logger.error(f"Error getting all LeanImprovements: {e}", exc_info=True)
            return []


# Simulation mappers and repository


def _deserialize_from_dict(data_class: type, data: dict):
    """Вспомогательная функция для десериализации dataclass из словаря."""
    from dataclasses import fields
    from typing import get_args, get_origin
    from domain import (
        Tender,
        Supplier,
        Warehouse,
        ProcessGraph,
        Logist,
        DealingWithDefects,
        SaleStrategest,
        LeanImprovement,
        ProductionSchedule,
        ProductionPlanRow,
        Workplace,
        Route,
        Certification,
        Worker,
    )
    from domain.metrics import (
        FactoryMetrics,
        ProductionMetrics,
        QualityMetrics,
        EngineeringMetrics,
        CommercialMetrics,
        ProcurementMetrics,
        WarehouseMetrics,
    )

    if not data:
        return data_class()

    kwargs = {}
    for field_obj in fields(data_class):
        field_name = field_obj.name
        if field_name not in data:
            continue

        value = data[field_name]

        # Обработка Enum типов
        if field_name == "dealing_with_defects":
            try:
                value = DealingWithDefects(value)
            except (ValueError, AttributeError):
                value = DealingWithDefects.NONE
        elif field_name == "sales_strategy":
            try:
                value = SaleStrategest(value)
            except (ValueError, AttributeError):
                value = SaleStrategest.NONE
        elif get_origin(field_obj.type) is dict or (
            hasattr(field_obj.type, "__origin__") and field_obj.type.__origin__ is dict
        ):
            # Обработка Dict типов (например, Dict[str, WarehouseMetrics])
            if isinstance(value, dict):
                try:
                    args = get_args(field_obj.type)
                    if args and len(args) >= 2:
                        # args[1] - тип значения словаря
                        value_type = args[1]
                        # Если тип значения - класс (не примитивный тип)
                        if hasattr(value_type, "__name__") and value_type.__name__ in [
                            "WarehouseMetrics",
                            "FactoryMetrics",
                            "ProductionMetrics",
                            "QualityMetrics",
                            "EngineeringMetrics",
                            "CommercialMetrics",
                            "ProcurementMetrics",
                        ]:
                            # Десериализуем значения словаря
                            deserialized_dict = {}
                            for key, val in value.items():
                                if isinstance(val, dict):
                                    try:
                                        deserialized_dict[key] = _deserialize_from_dict(
                                            value_type, val
                                        )
                                    except Exception:
                                        deserialized_dict[key] = val
                                else:
                                    deserialized_dict[key] = val
                            value = deserialized_dict
                except Exception as e:
                    logger.warning(f"Error deserializing Dict field {field_name}: {e}")
                    # Если не удалось десериализовать, оставляем как есть
                    pass
        elif get_origin(field_obj.type) == list:
            # Универсальная обработка списков объектов
            if isinstance(value, list):
                try:
                    # Определяем тип элементов списка из аннотации типа
                    args = get_args(field_obj.type)
                    if args and len(args) > 0:
                        item_type = args[0]

                        # Получаем имя типа для сравнения
                        type_name = None
                        if hasattr(item_type, "__name__"):
                            type_name = item_type.__name__
                        elif isinstance(item_type, str):
                            type_name = item_type
                        elif hasattr(item_type, "_name"):
                            type_name = item_type._name

                        # Маппинг имен типов на классы
                        from domain.metrics import (
                            ProductionMetrics,
                            QualityMetrics,
                            EngineeringMetrics,
                            CommercialMetrics,
                            ProcurementMetrics,
                        )

                        type_mapping = {
                            "Tender": Tender,
                            "Supplier": Supplier,
                            "Workplace": Workplace,
                            "Route": Route,
                            "LeanImprovement": LeanImprovement,
                            "Certification": Certification,
                            "ProductionPlanRow": ProductionPlanRow,
                            "MonthlyProductivity": ProductionMetrics.MonthlyProductivity,
                            "DefectCause": QualityMetrics.DefectCause,
                            "OperationTiming": EngineeringMetrics.OperationTiming,
                            "DowntimeRecord": EngineeringMetrics.DowntimeRecord,
                            "DefectAnalysis": EngineeringMetrics.DefectAnalysis,
                            "YearlyRevenue": CommercialMetrics.YearlyRevenue,
                            "TenderGraphPoint": CommercialMetrics.TenderGraphPoint,
                            "ProjectProfitability": CommercialMetrics.ProjectProfitability,
                            "SupplierPerformance": ProcurementMetrics.SupplierPerformance,
                        }

                        # Прямое сравнение классов, если это класс
                        deserialize_class = None

                        # Проверяем вложенные классы метрик по имени (qualname)
                        if hasattr(item_type, "__qualname__"):
                            qualname = item_type.__qualname__
                            if "MonthlyProductivity" in qualname:
                                deserialize_class = (
                                    ProductionMetrics.MonthlyProductivity
                                )
                            elif "DefectCause" in qualname:
                                deserialize_class = QualityMetrics.DefectCause
                            elif "OperationTiming" in qualname:
                                deserialize_class = EngineeringMetrics.OperationTiming
                            elif "DowntimeRecord" in qualname:
                                deserialize_class = EngineeringMetrics.DowntimeRecord
                            elif "DefectAnalysis" in qualname:
                                deserialize_class = EngineeringMetrics.DefectAnalysis
                            elif "YearlyRevenue" in qualname:
                                deserialize_class = CommercialMetrics.YearlyRevenue
                            elif "TenderGraphPoint" in qualname:
                                deserialize_class = CommercialMetrics.TenderGraphPoint
                            elif "ProjectProfitability" in qualname:
                                deserialize_class = (
                                    CommercialMetrics.ProjectProfitability
                                )
                            elif "SupplierPerformance" in qualname:
                                deserialize_class = (
                                    ProcurementMetrics.SupplierPerformance
                                )

                        # Если не нашли через qualname, проверяем прямой тип
                        if not deserialize_class:
                            if item_type in [
                                Tender,
                                Supplier,
                                Workplace,
                                Route,
                                LeanImprovement,
                                Certification,
                                ProductionPlanRow,
                            ]:
                                deserialize_class = item_type
                            elif type_name and type_name in type_mapping:
                                deserialize_class = type_mapping[type_name]

                        # Если все еще не нашли, пробуем определить из данных
                        if not deserialize_class:
                            # Пробуем определить тип из первого элемента списка по _type
                            if (
                                value
                                and isinstance(value[0], dict)
                                and "_type" in value[0]
                            ):
                                type_name_from_data = value[0].get("_type")
                                if type_name_from_data in type_mapping:
                                    deserialize_class = type_mapping[
                                        type_name_from_data
                                    ]
                                elif type_name_from_data in type_mapping_from_data:
                                    deserialize_class = type_mapping_from_data[
                                        type_name_from_data
                                    ]

                        if deserialize_class:
                            try:
                                # Для LeanImprovement используем from_dict, если доступно
                                if deserialize_class == LeanImprovement and hasattr(
                                    LeanImprovement, "from_dict"
                                ):
                                    value = [
                                        (
                                            LeanImprovement.from_dict(v)
                                            if isinstance(v, dict)
                                            else v
                                        )
                                        for v in value
                                    ]
                                elif deserialize_class == Tender:
                                    # Для Tender нужно специально десериализовать consumer
                                    def deserialize_tender(tender_dict):
                                        if not isinstance(tender_dict, dict):
                                            return tender_dict
                                        # Десериализуем consumer, если он есть
                                        if "consumer" in tender_dict and isinstance(
                                            tender_dict["consumer"], dict
                                        ):
                                            tender_dict["consumer"] = (
                                                _deserialize_from_dict(
                                                    Consumer, tender_dict["consumer"]
                                                )
                                            )
                                        return _deserialize_from_dict(
                                            Tender, tender_dict
                                        )

                                    value = [
                                        (
                                            deserialize_tender(v)
                                            if isinstance(v, dict)
                                            else v
                                        )
                                        for v in value
                                    ]
                                else:
                                    # Используем универсальную десериализацию
                                    value = [
                                        (
                                            _deserialize_from_dict(deserialize_class, v)
                                            if isinstance(v, dict)
                                            else v
                                        )
                                        for v in value
                                    ]
                            except Exception as e:
                                logger.warning(
                                    f"Error deserializing list of {deserialize_class.__name__}: {e}"
                                )
                                value = []
                        else:
                            # Если тип не распознан, оставляем как есть (может быть примитивный тип)
                            value = value
                    else:
                        # Не можем определить тип из аннотации, пробуем по данным
                        if value and isinstance(value[0], dict) and "_type" in value[0]:
                            type_name_from_data = value[0].get("_type")
                            type_mapping_from_data = {
                                "Tender": Tender,
                                "Supplier": Supplier,
                                "Workplace": Workplace,
                                "Route": Route,
                                "LeanImprovement": LeanImprovement,
                                "Certification": Certification,
                                "ProductionPlanRow": ProductionPlanRow,
                                "MonthlyProductivity": ProductionMetrics.MonthlyProductivity,
                                "DefectCause": QualityMetrics.DefectCause,
                                "OperationTiming": EngineeringMetrics.OperationTiming,
                                "DowntimeRecord": EngineeringMetrics.DowntimeRecord,
                                "DefectAnalysis": EngineeringMetrics.DefectAnalysis,
                                "YearlyRevenue": CommercialMetrics.YearlyRevenue,
                                "TenderGraphPoint": CommercialMetrics.TenderGraphPoint,
                                "ProjectProfitability": CommercialMetrics.ProjectProfitability,
                                "SupplierPerformance": ProcurementMetrics.SupplierPerformance,
                            }
                            if type_name_from_data in type_mapping:
                                deserialize_class = type_mapping[type_name_from_data]
                                try:
                                    if (
                                        deserialize_class == LeanImprovement
                                        and hasattr(LeanImprovement, "from_dict")
                                    ):
                                        value = [
                                            (
                                                LeanImprovement.from_dict(v)
                                                if isinstance(v, dict)
                                                else v
                                            )
                                            for v in value
                                        ]
                                    else:
                                        # Для Tender нужно специально десериализовать consumer
                                        if deserialize_class == Tender:

                                            def deserialize_tender(tender_dict):
                                                if not isinstance(tender_dict, dict):
                                                    return tender_dict
                                                # Десериализуем consumer, если он есть
                                                if (
                                                    "consumer" in tender_dict
                                                    and isinstance(
                                                        tender_dict["consumer"], dict
                                                    )
                                                ):
                                                    tender_dict["consumer"] = (
                                                        _deserialize_from_dict(
                                                            Consumer,
                                                            tender_dict["consumer"],
                                                        )
                                                    )
                                                return _deserialize_from_dict(
                                                    Tender, tender_dict
                                                )

                                            value = [
                                                (
                                                    deserialize_tender(v)
                                                    if isinstance(v, dict)
                                                    else v
                                                )
                                                for v in value
                                            ]
                                        else:
                                            value = [
                                                (
                                                    _deserialize_from_dict(
                                                        deserialize_class, v
                                                    )
                                                    if isinstance(v, dict)
                                                    else v
                                                )
                                                for v in value
                                            ]
                                except Exception:
                                    value = []
                        else:
                            value = value
                except Exception as e:
                    logger.warning(f"Error processing list field {field_name}: {e}")
                    # Если что-то пошло не так, оставляем значение как есть
                    value = value
            else:
                value = value
        elif field_name in ("process_graph", "processes") and isinstance(value, dict):
            # Десериализуем ProcessGraph из словаря
            try:
                value = _deserialize_from_dict(ProcessGraph, value)
            except Exception:
                # Если не удалось десериализовать, создаем пустой ProcessGraph
                value = ProcessGraph()
        elif field_name in (
            "materials_warehouse",
            "product_warehouse",
        ) and isinstance(value, dict):
            # Десериализуем Warehouse из словаря
            try:
                value = _deserialize_from_dict(Warehouse, value)
            except Exception:
                # Если не удалось десериализовать, создаем пустой Warehouse
                value = Warehouse()
        elif field_name == "logist" and isinstance(value, dict):
            # Десериализуем Logist из словаря
            try:
                value = _deserialize_from_dict(Logist, value)
            except Exception:
                # Если не удалось десериализовать, оставляем None
                value = None
        elif field_name == "inventory_worker" and isinstance(value, dict):
            # Десериализуем Worker из словаря (может быть Worker или Logist)
            try:
                # Проверяем тип по полю _type или по структуре
                if value.get("_type") == "Logist":
                    value = _deserialize_from_dict(Logist, value)
                else:
                    value = _deserialize_from_dict(Worker, value)
            except Exception:
                # Если не удалось десериализовать, оставляем None
                value = None
        elif field_name == "production_schedule" and isinstance(value, dict):
            # Десериализуем ProductionSchedule из словаря
            try:
                value = _deserialize_from_dict(ProductionSchedule, value)
            except Exception:
                # Если не удалось десериализовать, создаем пустой ProductionSchedule
                value = ProductionSchedule()
        elif field_name == "consumer" and isinstance(value, dict):
            # Десериализуем Consumer из словаря (для Tender)
            try:
                value = _deserialize_from_dict(Consumer, value)
            except Exception:
                # Если не удалось десериализовать, создаем пустой Consumer
                value = Consumer(name="", type="")
        elif field_name in (
            "factory_metrics",
            "production_metrics",
            "quality_metrics",
            "engineering_metrics",
            "commercial_metrics",
            "procurement_metrics",
        ) and isinstance(value, dict):
            # Десериализуем метрики из словаря (для SimulationResults)
            metrics_class_map = {
                "factory_metrics": FactoryMetrics,
                "production_metrics": ProductionMetrics,
                "quality_metrics": QualityMetrics,
                "engineering_metrics": EngineeringMetrics,
                "commercial_metrics": CommercialMetrics,
                "procurement_metrics": ProcurementMetrics,
            }
            metrics_class = metrics_class_map.get(field_name)
            if metrics_class:
                try:
                    # Перед десериализацией обрабатываем вложенные списки объектов
                    if (
                        field_name == "production_metrics"
                        and "monthly_productivity" in value
                    ):
                        # Десериализуем MonthlyProductivity объекты
                        monthly_list = value.get("monthly_productivity", [])
                        if isinstance(monthly_list, list):
                            deserialized_monthly = []
                            for item in monthly_list:
                                if isinstance(item, dict):
                                    try:
                                        from domain.metrics import ProductionMetrics

                                        deserialized_monthly.append(
                                            _deserialize_from_dict(
                                                ProductionMetrics.MonthlyProductivity,
                                                item,
                                            )
                                        )
                                    except Exception:
                                        # Если не удалось, создаем из словаря
                                        deserialized_monthly.append(
                                            ProductionMetrics.MonthlyProductivity(
                                                month=item.get("month", ""),
                                                units_produced=item.get(
                                                    "units_produced", 0
                                                ),
                                            )
                                        )
                                else:
                                    deserialized_monthly.append(item)
                            value["monthly_productivity"] = deserialized_monthly

                    elif field_name == "quality_metrics" and "defect_causes" in value:
                        # Десериализуем DefectCause объекты
                        causes_list = value.get("defect_causes", [])
                        if isinstance(causes_list, list):
                            deserialized_causes = []
                            for item in causes_list:
                                if isinstance(item, dict):
                                    try:
                                        from domain.metrics import QualityMetrics

                                        deserialized_causes.append(
                                            _deserialize_from_dict(
                                                QualityMetrics.DefectCause, item
                                            )
                                        )
                                    except Exception:
                                        deserialized_causes.append(
                                            QualityMetrics.DefectCause(
                                                cause=item.get("cause", ""),
                                                count=item.get("count", 0),
                                                percentage=item.get("percentage", 0.0),
                                            )
                                        )
                                else:
                                    deserialized_causes.append(item)
                            value["defect_causes"] = deserialized_causes

                    elif field_name == "engineering_metrics":
                        # Десериализуем вложенные объекты EngineeringMetrics
                        from domain.metrics import EngineeringMetrics

                        if "operation_timings" in value:
                            timings_list = value.get("operation_timings", [])
                            if isinstance(timings_list, list):
                                deserialized_timings = []
                                for item in timings_list:
                                    if isinstance(item, dict):
                                        try:
                                            deserialized_timings.append(
                                                _deserialize_from_dict(
                                                    EngineeringMetrics.OperationTiming,
                                                    item,
                                                )
                                            )
                                        except Exception:
                                            deserialized_timings.append(
                                                EngineeringMetrics.OperationTiming(
                                                    operation_name=item.get(
                                                        "operation_name", ""
                                                    ),
                                                    cycle_time=item.get(
                                                        "cycle_time", 0
                                                    ),
                                                    takt_time=item.get("takt_time", 0),
                                                    timing_cost=item.get(
                                                        "timing_cost", 0
                                                    ),
                                                )
                                            )
                                    else:
                                        deserialized_timings.append(item)
                                value["operation_timings"] = deserialized_timings

                        if "downtime_records" in value:
                            records_list = value.get("downtime_records", [])
                            if isinstance(records_list, list):
                                deserialized_records = []
                                for item in records_list:
                                    if isinstance(item, dict):
                                        try:
                                            deserialized_records.append(
                                                _deserialize_from_dict(
                                                    EngineeringMetrics.DowntimeRecord,
                                                    item,
                                                )
                                            )
                                        except Exception:
                                            deserialized_records.append(
                                                EngineeringMetrics.DowntimeRecord(
                                                    cause=item.get("cause", ""),
                                                    total_minutes=item.get(
                                                        "total_minutes", 0
                                                    ),
                                                    average_per_shift=item.get(
                                                        "average_per_shift", 0.0
                                                    ),
                                                )
                                            )
                                    else:
                                        deserialized_records.append(item)
                                value["downtime_records"] = deserialized_records

                        if "defect_analysis" in value:
                            analysis_list = value.get("defect_analysis", [])
                            if isinstance(analysis_list, list):
                                deserialized_analysis = []
                                for item in analysis_list:
                                    if isinstance(item, dict):
                                        try:
                                            deserialized_analysis.append(
                                                _deserialize_from_dict(
                                                    EngineeringMetrics.DefectAnalysis,
                                                    item,
                                                )
                                            )
                                        except Exception:
                                            deserialized_analysis.append(
                                                EngineeringMetrics.DefectAnalysis(
                                                    defect_type=item.get(
                                                        "defect_type", ""
                                                    ),
                                                    count=item.get("count", 0),
                                                    percentage=item.get(
                                                        "percentage", 0.0
                                                    ),
                                                    cumulative_percentage=item.get(
                                                        "cumulative_percentage", 0.0
                                                    ),
                                                )
                                            )
                                    else:
                                        deserialized_analysis.append(item)
                                value["defect_analysis"] = deserialized_analysis

                    elif field_name == "commercial_metrics":
                        # Десериализуем вложенные объекты CommercialMetrics
                        from domain.metrics import CommercialMetrics

                        if "yearly_revenues" in value:
                            revenues_list = value.get("yearly_revenues", [])
                            if isinstance(revenues_list, list):
                                deserialized_revenues = []
                                for item in revenues_list:
                                    if isinstance(item, dict):
                                        try:
                                            deserialized_revenues.append(
                                                _deserialize_from_dict(
                                                    CommercialMetrics.YearlyRevenue,
                                                    item,
                                                )
                                            )
                                        except Exception:
                                            deserialized_revenues.append(
                                                CommercialMetrics.YearlyRevenue(
                                                    year=item.get("year", 0),
                                                    revenue=item.get("revenue", 0),
                                                )
                                            )
                                    else:
                                        deserialized_revenues.append(item)
                                value["yearly_revenues"] = deserialized_revenues

                        if "tender_graph" in value:
                            graph_list = value.get("tender_graph", [])
                            if isinstance(graph_list, list):
                                deserialized_graph = []
                                for item in graph_list:
                                    if isinstance(item, dict):
                                        try:
                                            deserialized_graph.append(
                                                _deserialize_from_dict(
                                                    CommercialMetrics.TenderGraphPoint,
                                                    item,
                                                )
                                            )
                                        except Exception:
                                            deserialized_graph.append(
                                                CommercialMetrics.TenderGraphPoint(
                                                    strategy=item.get("strategy", ""),
                                                    unit_size=item.get("unit_size", ""),
                                                    is_mastered=item.get(
                                                        "is_mastered", False
                                                    ),
                                                )
                                            )
                                    else:
                                        deserialized_graph.append(item)
                                value["tender_graph"] = deserialized_graph

                        if "project_profitabilities" in value:
                            profit_list = value.get("project_profitabilities", [])
                            if isinstance(profit_list, list):
                                deserialized_profit = []
                                for item in profit_list:
                                    if isinstance(item, dict):
                                        try:
                                            deserialized_profit.append(
                                                _deserialize_from_dict(
                                                    CommercialMetrics.ProjectProfitability,
                                                    item,
                                                )
                                            )
                                        except Exception:
                                            deserialized_profit.append(
                                                CommercialMetrics.ProjectProfitability(
                                                    project_name=item.get(
                                                        "project_name", ""
                                                    ),
                                                    profitability=item.get(
                                                        "profitability", 0.0
                                                    ),
                                                )
                                            )
                                    else:
                                        deserialized_profit.append(item)
                                value["project_profitabilities"] = deserialized_profit

                    elif (
                        field_name == "procurement_metrics"
                        and "supplier_performances" in value
                    ):
                        # Десериализуем SupplierPerformance объекты
                        performances_list = value.get("supplier_performances", [])
                        if isinstance(performances_list, list):
                            deserialized_performances = []
                            for item in performances_list:
                                if isinstance(item, dict):
                                    try:
                                        from domain.metrics import ProcurementMetrics

                                        deserialized_performances.append(
                                            _deserialize_from_dict(
                                                ProcurementMetrics.SupplierPerformance,
                                                item,
                                            )
                                        )
                                    except Exception:
                                        deserialized_performances.append(
                                            ProcurementMetrics.SupplierPerformance(
                                                supplier_id=item.get("supplier_id", ""),
                                                delivered_quantity=item.get(
                                                    "delivered_quantity", 0
                                                ),
                                                projected_defect_rate=item.get(
                                                    "projected_defect_rate", 0.0
                                                ),
                                                planned_reliability=item.get(
                                                    "planned_reliability", 0.0
                                                ),
                                                actual_reliability=item.get(
                                                    "actual_reliability", 0.0
                                                ),
                                                planned_cost=item.get(
                                                    "planned_cost", 0
                                                ),
                                                actual_cost=item.get("actual_cost", 0),
                                                actual_defect_count=item.get(
                                                    "actual_defect_count", 0
                                                ),
                                            )
                                        )
                                else:
                                    deserialized_performances.append(item)
                            value["supplier_performances"] = deserialized_performances

                    value = _deserialize_from_dict(metrics_class, value)
                except Exception as e:
                    logger.warning(
                        f"Error deserializing {field_name}: {e}", exc_info=True
                    )
                    # Если не удалось десериализовать, оставляем None
                    value = None
        elif isinstance(value, dict) and "_type" in value:
            # Универсальная десериализация для объектов с полем _type
            # Это резервный механизм, если объект не был распознан ранее
            type_name = value.get("_type")
            type_mapping = {
                "Warehouse": Warehouse,
                "ProcessGraph": ProcessGraph,
                "Logist": Logist,
                "Worker": Worker,
                "ProductionSchedule": ProductionSchedule,
                "Tender": Tender,
                "Supplier": Supplier,
                "Workplace": Workplace,
                "Route": Route,
                "Certification": Certification,
                "LeanImprovement": LeanImprovement,
                "ProductionPlanRow": ProductionPlanRow,
                "FactoryMetrics": FactoryMetrics,
                "ProductionMetrics": ProductionMetrics,
                "QualityMetrics": QualityMetrics,
                "EngineeringMetrics": EngineeringMetrics,
                "CommercialMetrics": CommercialMetrics,
                "ProcurementMetrics": ProcurementMetrics,
                "WarehouseMetrics": WarehouseMetrics,
                "SimulationResults": SimulationResults,
            }
            if type_name in type_mapping:
                try:
                    deserialize_class = type_mapping[type_name]
                    # Для LeanImprovement используем from_dict, если доступно
                    if type_name == "LeanImprovement" and hasattr(
                        LeanImprovement, "from_dict"
                    ):
                        value = LeanImprovement.from_dict(value)
                    elif type_name == "Tender":
                        # Для Tender нужно специально десериализовать consumer
                        if (
                            isinstance(value, dict)
                            and "consumer" in value
                            and isinstance(value["consumer"], dict)
                        ):
                            value["consumer"] = _deserialize_from_dict(
                                Consumer, value["consumer"]
                            )
                        value = _deserialize_from_dict(deserialize_class, value)
                    else:
                        value = _deserialize_from_dict(deserialize_class, value)
                except Exception as e:
                    logger.warning(f"Error deserializing {type_name} from _type: {e}")
                    # Если не удалось десериализовать, оставляем словарь
                    pass

        kwargs[field_name] = value

    try:
        return data_class(**kwargs)
    except Exception as e:
        logger.warning(
            f"Error deserializing {data_class.__name__}: {e}, using defaults"
        )
        return data_class()


def simulation_db_to_domain(db_model: SimulationDB) -> Simulation:
    """Преобразует SQLAlchemy модель Simulation в доменную сущность."""

    # parameters и results теперь списки
    # Поддерживаем старый формат (один объект) и новый (список)
    parameters_data = db_model.simulation_parameters or {}

    # Если это словарь (старый формат), конвертируем в список
    if isinstance(parameters_data, dict):
        simulation_parameters = [
            _deserialize_from_dict(SimulationParameters, parameters_data)
        ]
    elif isinstance(parameters_data, list):
        simulation_parameters = [
            _deserialize_from_dict(SimulationParameters, params_dict)
            for params_dict in parameters_data
        ]
    else:
        simulation_parameters = [SimulationParameters()]

    # results теперь список
    results_data = db_model.simulation_results or {}

    # Если это словарь (старый формат), конвертируем в список
    if isinstance(results_data, dict):
        # Проверяем наличие обязательных полей
        if "profit" not in results_data:
            results_data["profit"] = 0
        if "cost" not in results_data:
            results_data["cost"] = 0
        if "profitability" not in results_data:
            results_data["profitability"] = 0.0

        # Проверяем, что есть step, иначе это пустой результат (не добавляем)
        if "step" in results_data and results_data["step"] > 0:
            # Используем универсальную десериализацию для восстановления всех полей, включая метрики
            try:
                simulation_results = [
                    _deserialize_from_dict(SimulationResults, results_data)
                ]
            except Exception:
                # Fallback на простую десериализацию, если универсальная не сработала
                simulation_results = [
                    SimulationResults(
                        profit=results_data.get("profit", 0),
                        cost=results_data.get("cost", 0),
                        profitability=results_data.get("profitability", 0.0),
                        step=results_data.get("step", 0),
                    )
                ]
        else:
            simulation_results = []
    elif isinstance(results_data, list):
        simulation_results = []
        for result_dict in results_data:
            # Проверяем, что есть step и он > 0, иначе это пустой результат (не добавляем)
            if isinstance(result_dict, dict) and result_dict.get("step", 0) > 0:
                # Используем универсальную десериализацию для восстановления всех полей, включая метрики
                try:
                    simulation_results.append(
                        _deserialize_from_dict(SimulationResults, result_dict)
                    )
                except Exception:
                    # Fallback на простую десериализацию, если универсальная не сработала
                    simulation_results.append(
                        SimulationResults(
                            profit=result_dict.get("profit", 0),
                            cost=result_dict.get("cost", 0),
                            profitability=result_dict.get("profitability", 0.0),
                            step=result_dict.get("step", 0),
                        )
                    )
            # Если step отсутствует или = 0, не добавляем результат
    else:
        simulation_results = []

    return Simulation(
        simulation_id=str(db_model.simulation_id) if db_model.simulation_id else "",
        capital=db_model.capital or 0,
        parameters=simulation_parameters,
        results=simulation_results,
        room_id=getattr(db_model, "room_id", None) or "",
        is_completed=getattr(db_model, "is_completed", False),
    )


def simulation_domain_to_db(
    domain_entity: Simulation, db_model: Optional[SimulationDB] = None
) -> SimulationDB:
    """Преобразует доменную сущность Simulation в SQLAlchemy модель."""
    if db_model is None:
        db_model = SimulationDB()

    db_model.capital = domain_entity.capital

    # Сохраняем step из первого результата, если есть
    if domain_entity.results and len(domain_entity.results) > 0:
        db_model.step = (
            domain_entity.results[0].step
            if hasattr(domain_entity.results[0], "step")
            else 0
        )
    else:
        db_model.step = 0

    # Сериализуем parameters (список) в JSON
    if domain_entity.parameters:
        db_model.simulation_parameters = [
            params.to_redis_dict() if hasattr(params, "to_redis_dict") else {}
            for params in domain_entity.parameters
        ]
    else:
        db_model.simulation_parameters = []

    # Сериализуем results (список) в JSON
    # Фильтруем только результаты с валидным step
    valid_results = [
        result
        for result in domain_entity.results
        if hasattr(result, "step") and result.step > 0
    ]

    if valid_results:
        db_model.simulation_results = [
            (
                result.to_redis_dict()
                if hasattr(result, "to_redis_dict")
                else {
                    "profit": 0,
                    "cost": 0,
                    "profitability": 0.0,
                    "step": getattr(result, "step", 0),
                }
            )
            for result in valid_results
        ]
    else:
        # Если результатов нет или все пустые, сохраняем пустой список
        db_model.simulation_results = []

    if domain_entity.simulation_id:
        db_model.simulation_id = domain_entity.simulation_id

    return db_model


class SimulationRepository(AbstractRepository[Simulation]):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, model: Simulation) -> Union[Simulation, None]:
        """Сохраняет или обновляет Simulation."""
        try:
            db_model = None
            if model.simulation_id:
                result = await self.session.execute(
                    select(SimulationDB).where(
                        SimulationDB.simulation_id == model.simulation_id
                    )
                )
                db_model = result.scalar_one_or_none()

            db_model = simulation_domain_to_db(model, db_model)
            self.session.add(db_model)
            await self.session.commit()
            await self.session.refresh(db_model)

            return simulation_db_to_domain(db_model)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error saving Simulation: {e}", exc_info=True)
            return None

    async def get(self, id: Union[UUID, str]) -> Union[Simulation, None]:
        """Получает Simulation по ID."""
        try:
            # simulation_id теперь строка
            simulation_id = str(id) if id else ""
            result = await self.session.execute(
                select(SimulationDB).where(SimulationDB.simulation_id == simulation_id)
            )
            db_model = result.scalar_one_or_none()
            if db_model is None:
                return None
            return simulation_db_to_domain(db_model)
        except Exception as e:
            logger.error(f"Error getting Simulation: {e}", exc_info=True)
            return None

    async def delete(self, id: Union[UUID, str]) -> Union[Simulation, None]:
        """Удаляет Simulation по ID."""
        try:
            # simulation_id теперь строка
            simulation_id = str(id) if id else ""
            result = await self.session.execute(
                select(SimulationDB).where(SimulationDB.simulation_id == simulation_id)
            )
            db_model = result.scalar_one_or_none()
            if db_model:
                domain_entity = simulation_db_to_domain(db_model)
                await self.session.delete(db_model)
                await self.session.commit()
                return domain_entity
            return None
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting Simulation: {e}", exc_info=True)
            return None

    async def update_parameters(
        self, simulation_id: Union[UUID, str], parameters: SimulationParameters
    ) -> Union[Simulation, None]:
        """Обновляет только simulation_parameters для Simulation."""
        try:
            # simulation_id теперь строка
            sim_id = str(simulation_id) if simulation_id else ""
            result = await self.session.execute(
                select(SimulationDB).where(SimulationDB.simulation_id == sim_id)
            )
            db_model = result.scalar_one_or_none()

            if db_model is None:
                logger.warning(f"Simulation {sim_id} not found for parameters update")
                return None

            # Обновляем только параметры (теперь список)
            # Берем первый элемент или создаем новый список
            domain_entity = simulation_db_to_domain(db_model)
            if domain_entity.parameters:
                domain_entity.parameters[0] = parameters
            else:
                domain_entity.parameters = [parameters]

            db_model.simulation_parameters = [
                params.to_redis_dict() if hasattr(params, "to_redis_dict") else {}
                for params in domain_entity.parameters
            ]
            await self.session.commit()
            await self.session.refresh(db_model)

            return simulation_db_to_domain(db_model)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating Simulation parameters: {e}", exc_info=True)
            return None

    async def update_results(
        self, simulation_id: Union[UUID, str], results: SimulationResults
    ) -> Union[Simulation, None]:
        """Обновляет только simulation_results для Simulation."""
        try:
            # simulation_id теперь строка
            sim_id = str(simulation_id) if simulation_id else ""
            result = await self.session.execute(
                select(SimulationDB).where(SimulationDB.simulation_id == sim_id)
            )
            db_model = result.scalar_one_or_none()

            if db_model is None:
                logger.warning(f"Simulation {sim_id} not found for results update")
                return None

            # Обновляем только результаты (теперь список)
            # Берем первый элемент или создаем новый список
            domain_entity = simulation_db_to_domain(db_model)
            if domain_entity.results:
                domain_entity.results[0] = results
            else:
                domain_entity.results = [results]

            db_model.simulation_results = [
                (
                    result.to_redis_dict()
                    if hasattr(result, "to_redis_dict")
                    else {"profit": 0, "cost": 0, "profitability": 0.0}
                )
                for result in domain_entity.results
            ]
            await self.session.commit()
            await self.session.refresh(db_model)

            return simulation_db_to_domain(db_model)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating Simulation results: {e}", exc_info=True)
            return None

    async def get_all(self) -> List[Simulation]:
        """Получает все симуляции."""
        try:
            result = await self.session.execute(select(SimulationDB))
            db_models = result.scalars().all()
            return [simulation_db_to_domain(db_model) for db_model in db_models]
        except Exception as e:
            logger.error(f"Error getting all Simulations: {e}", exc_info=True)
            return []

    async def update_step(
        self, simulation_id: Union[UUID, str], step: int
    ) -> Union[Simulation, None]:
        """Обновляет шаг симуляции."""
        try:
            # simulation_id теперь строка
            sim_id = str(simulation_id) if simulation_id else ""
            result = await self.session.execute(
                select(SimulationDB).where(SimulationDB.simulation_id == sim_id)
            )
            db_model = result.scalar_one_or_none()

            if db_model is None:
                logger.warning(f"Simulation {sim_id} not found for step update")
                return None

            db_model.step = step
            await self.session.commit()
            await self.session.refresh(db_model)

            return simulation_db_to_domain(db_model)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating Simulation step: {e}", exc_info=True)
            return None

    async def update_capital(
        self, simulation_id: Union[UUID, str], capital: int
    ) -> Union[Simulation, None]:
        """Обновляет капитал симуляции."""
        try:
            # simulation_id теперь строка
            sim_id = str(simulation_id) if simulation_id else ""
            result = await self.session.execute(
                select(SimulationDB).where(SimulationDB.simulation_id == sim_id)
            )
            db_model = result.scalar_one_or_none()

            if db_model is None:
                logger.warning(f"Simulation {sim_id} not found for capital update")
                return None

            db_model.capital = capital
            await self.session.commit()
            await self.session.refresh(db_model)

            return simulation_db_to_domain(db_model)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating Simulation capital: {e}", exc_info=True)
            return None
