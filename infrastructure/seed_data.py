"""Модуль для создания тестовых данных в базе данных."""

from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.repositories import (
    WorkerRepository,
    SupplierRepository,
    EquipmentRepository,
    WorkplaceRepository,
    ConsumerRepository,
    TenderRepository,
    LeanImprovementRepository,
)
from domain import (
    Worker,
    Supplier,
    Equipment,
    Workplace,
    Consumer,
    Tender,
    LeanImprovement,
    Qualification,
    Specialization,
    ConsumerType,
    PaymentForm,
    VehicleType,
    Logist,
)


async def create_test_data(session: AsyncSession) -> None:
    """Создает тестовые данные для всех таблиц кроме simulations.

    Args:
        session: Асинхронная сессия SQLAlchemy для работы с БД
    """
    # 1. Создаем работников (Workers)
    worker_repo = WorkerRepository(session)

    workers = [
        Worker(
            worker_id=str(uuid4()),
            name="Иван Петров",
            qualification=Qualification.V.value,
            specialty=Specialization.ASSEMBLER.value,
            salary=50000,
        ),
        Worker(
            worker_id=str(uuid4()),
            name="Мария Сидорова",
            qualification=Qualification.IV.value,
            specialty=Specialization.ENGINEER_TECHNOLOGIST.value,
            salary=70000,
        ),
        Worker(
            worker_id=str(uuid4()),
            name="Алексей Козлов",
            qualification=Qualification.III.value,
            specialty=Specialization.QUALITY_CONTROLLER.value,
            salary=55000,
        ),
        Worker(
            worker_id=str(uuid4()),
            name="Елена Волкова",
            qualification=Qualification.II.value,
            specialty=Specialization.WAREHOUSE_KEEPER.value,
            salary=45000,
        ),
    ]

    # Создаем логиста
    logist = Logist(
        worker_id=str(uuid4()),
        name="Дмитрий Соколов",
        qualification=Qualification.VI.value,
        specialty=Specialization.LOGIST.value,
        salary=60000,
        speed=60,
        vehicle_type=VehicleType.TRUCK.value,
    )

    for worker in workers:
        try:
            await worker_repo.save(worker)
        except Exception as e:
            print(f"Ошибка при создании работника {worker.name}: {e}")

    # Сохраняем логиста как Worker (он наследуется от Worker)
    try:
        await worker_repo.save(logist)
    except Exception as e:
        print(f"Ошибка при создании логиста {logist.name}: {e}")

    # 2. Создаем поставщиков (Suppliers)
    supplier_repo = SupplierRepository(session)

    suppliers = [
        Supplier(
            supplier_id=str(uuid4()),
            name="ООО МеталлСнаб",
            product_name="Стальной лист",
            material_type="Металл",
            delivery_period=14,
            special_delivery_period=7,
            reliability=0.95,
            product_quality=0.92,
            cost=50000,
            special_delivery_cost=75000,
        ),
        Supplier(
            supplier_id=str(uuid4()),
            name="ПластМатериалы",
            product_name="Пластиковые детали",
            material_type="Пластик",
            delivery_period=10,
            special_delivery_period=5,
            reliability=0.88,
            product_quality=0.90,
            cost=30000,
            special_delivery_cost=45000,
        ),
        Supplier(
            supplier_id=str(uuid4()),
            name="ЭлектронКомплект",
            product_name="Электронные компоненты",
            material_type="Электроника",
            delivery_period=21,
            special_delivery_period=10,
            reliability=0.90,
            product_quality=0.95,
            cost=80000,
            special_delivery_cost=120000,
        ),
    ]

    for supplier in suppliers:
        try:
            await supplier_repo.save(supplier)
        except Exception as e:
            print(f"Ошибка при создании поставщика {supplier.name}: {e}")

    # 3. Создаем оборудование (Equipment)
    equipment_repo = EquipmentRepository(session)

    equipment_list = [
        Equipment(
            equipment_id=str(uuid4()),
            name="Токарный станок ЧПУ",
            equipment_type="Станок",
            reliability=0.85,
            maintenance_period=30,
            maintenance_cost=15000,
            cost=500000,
            repair_cost=50000,
            repair_time=48,
        ),
        Equipment(
            equipment_id=str(uuid4()),
            name="Сварочный аппарат",
            equipment_type="Сварочное оборудование",
            reliability=0.80,
            maintenance_period=20,
            maintenance_cost=8000,
            cost=150000,
            repair_cost=25000,
            repair_time=24,
        ),
        Equipment(
            equipment_id=str(uuid4()),
            name="Конвейерная лента",
            equipment_type="Транспортное оборудование",
            reliability=0.90,
            maintenance_period=60,
            maintenance_cost=10000,
            cost=200000,
            repair_cost=30000,
            repair_time=36,
        ),
        Equipment(
            equipment_id=str(uuid4()),
            name="Контрольный стенд",
            equipment_type="Измерительное оборудование",
            reliability=0.95,
            maintenance_period=90,
            maintenance_cost=5000,
            cost=300000,
            repair_cost=40000,
            repair_time=12,
        ),
    ]

    for equipment in equipment_list:
        try:
            await equipment_repo.save(equipment)
        except Exception as e:
            print(f"Ошибка при создании оборудования {equipment.name}: {e}")

    # 4. Создаем рабочие места (Workplaces)
    workplace_repo = WorkplaceRepository(session)

    workplace1 = Workplace(
        workplace_id=str(uuid4()),
        workplace_name="Сборочный участок",
        required_speciality=Specialization.ASSEMBLER.value,
        required_qualification=Qualification.IV.value,
        required_equipment="Токарный станок ЧПУ",
        required_stages=["Подготовка", "Сборка", "Проверка"],
        is_start_node=True,
        is_end_node=False,
        next_workplace_ids=[],
    )

    workplace2 = Workplace(
        workplace_id=str(uuid4()),
        workplace_name="Контроль качества",
        required_speciality=Specialization.QUALITY_CONTROLLER.value,
        required_qualification=Qualification.III.value,
        required_equipment="Контрольный стенд",
        required_stages=["Проверка", "Тестирование"],
        is_start_node=False,
        is_end_node=False,
        next_workplace_ids=[],
    )

    workplace3 = Workplace(
        workplace_id=str(uuid4()),
        workplace_name="Склад готовой продукции",
        required_speciality=Specialization.WAREHOUSE_KEEPER.value,
        required_qualification=Qualification.II.value,
        required_equipment="",
        required_stages=["Упаковка", "Маркировка"],
        is_start_node=False,
        is_end_node=True,
        next_workplace_ids=[],
    )

    # Устанавливаем связи между рабочими местами
    workplace1.next_workplace_ids = [workplace2.workplace_id]
    workplace2.next_workplace_ids = [workplace3.workplace_id]

    workplaces = [workplace1, workplace2, workplace3]

    for workplace in workplaces:
        try:
            await workplace_repo.save(workplace)
        except Exception as e:
            print(f"Ошибка при создании рабочего места {workplace.workplace_name}: {e}")

    # 5. Создаем потребителей (Consumers)
    consumer_repo = ConsumerRepository(session)

    consumers = [
        Consumer(
            consumer_id=str(uuid4()),
            name="Министерство обороны",
            type=ConsumerType.GOVERMANT.value,  # "Государсвенный"
        ),
        Consumer(
            consumer_id=str(uuid4()),
            name="ООО Промышленные системы",
            type=ConsumerType.NOT_GOVERMANT.value,  # "Частный"
        ),
        Consumer(
            consumer_id=str(uuid4()),
            name="АО Машиностроительный завод",
            type=ConsumerType.NOT_GOVERMANT.value,  # "Частный"
        ),
    ]

    for consumer in consumers:
        try:
            await consumer_repo.save(consumer)
        except Exception as e:
            print(f"Ошибка при создании потребителя {consumer.name}: {e}")

    # 6. Создаем тендеры (Tenders) - нужны consumers
    tender_repo = TenderRepository(session)

    # Получаем созданных consumers
    all_consumers = await consumer_repo.get_all()

    if all_consumers:
        tenders = [
            Tender(
                tender_id=str(uuid4()),
                consumer=all_consumers[0],
                cost=5000000,
                quantity_of_products=100,
                penalty_per_day=50000,
                warranty_years=2,
                payment_form=PaymentForm.FULL_ADVANCE.value,
            ),
            Tender(
                tender_id=str(uuid4()),
                consumer=(
                    all_consumers[1] if len(all_consumers) > 1 else all_consumers[0]
                ),
                cost=3000000,
                quantity_of_products=50,
                penalty_per_day=30000,
                warranty_years=1,
                payment_form=PaymentForm.PARTIAL_ADVANCE.value,
            ),
            Tender(
                tender_id=str(uuid4()),
                consumer=(
                    all_consumers[2] if len(all_consumers) > 2 else all_consumers[0]
                ),
                cost=8000000,
                quantity_of_products=200,
                penalty_per_day=80000,
                warranty_years=3,
                payment_form=PaymentForm.ON_DELIVERY.value,
            ),
        ]

        for tender in tenders:
            try:
                await tender_repo.save(tender)
            except Exception as e:
                print(f"Ошибка при создании тендера: {e}")

    # 7. Создаем LEAN улучшения (LeanImprovements)
    improvement_repo = LeanImprovementRepository(session)

    improvements = [
        LeanImprovement(
            improvement_id=str(uuid4()),
            name="Внедрение системы 5S",
            is_implemented=False,
            implementation_cost=200000,
            efficiency_gain=0.15,
        ),
        LeanImprovement(
            improvement_id=str(uuid4()),
            name="Канбан система",
            is_implemented=False,
            implementation_cost=300000,
            efficiency_gain=0.20,
        ),
        LeanImprovement(
            improvement_id=str(uuid4()),
            name="Автоматизация учета",
            is_implemented=False,
            implementation_cost=500000,
            efficiency_gain=0.25,
        ),
        LeanImprovement(
            improvement_id=str(uuid4()),
            name="Обучение персонала",
            is_implemented=False,
            implementation_cost=150000,
            efficiency_gain=0.10,
        ),
    ]

    for improvement in improvements:
        try:
            await improvement_repo.save(improvement)
        except Exception as e:
            print(f"Ошибка при создании улучшения {improvement.name}: {e}")

    # Коммитим все изменения
    try:
        await session.commit()
        print("Тестовые данные успешно созданы!")
    except Exception as e:
        await session.rollback()
        print(f"Ошибка при коммите транзакции: {e}")
        raise
