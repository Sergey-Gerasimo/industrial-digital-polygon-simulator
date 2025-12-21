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
            name="Сергей Морозов",
            qualification=Qualification.VII.value,
            specialty=Specialization.ASSEMBLER.value,
            salary=65000,
        ),
        Worker(
            name="Анна Белова",
            qualification=Qualification.VIII.value,
            specialty=Specialization.QUALITY_CONTROLLER.value,
            salary=72000,
        ),
        Worker(
            name="Павел Смирнов",
            qualification=Qualification.VII.value,
            specialty=Specialization.ASSEMBLER.value,
            salary=61000,
        ),
        Worker(
            name="Олег Кузнецов",
            qualification=Qualification.VI.value,
            specialty=Specialization.ASSEMBLER.value,
            salary=58000,
        ),
        Worker(
            name="Наталья Иванова",
            qualification=Qualification.IV.value,
            specialty=Specialization.ASSEMBLER.value,
            salary=52000,
        ),
        Worker(
            name="Дмитрий Королев",
            qualification=Qualification.V.value,
            specialty=Specialization.ASSEMBLER.value,
            salary=54000,
        ),
        Worker(
            name="Ирина Зайцева",
            qualification=Qualification.VIII.value,
            specialty=Specialization.QUALITY_CONTROLLER.value,
            salary=74000,
        ),
        Worker(
            name="Роман Лебедев",
            qualification=Qualification.IX.value,
            specialty=Specialization.ENGINEER_TECHNOLOGIST.value,
            salary=80000,
        ),
    ]

    # Создаем логиста
    logist = Logist(
        name="Георгий Логинов",
        qualification=Qualification.V.value,
        specialty=Specialization.LOGIST.value,
        salary=60000,
        speed=70,
        vehicle_type=VehicleType.VAN.value,
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
            name="Energetics",
            product_name="Контроллеры",
            material_type="Электроника",
            delivery_period=5,
            special_delivery_period=3,
            reliability=0.96,
            product_quality=0.98,
            cost=20000,
            special_delivery_cost=26000,
        ),
        Supplier(
            name="Блупер",
            product_name="Контроллеры",
            material_type="Электроника",
            delivery_period=10,
            special_delivery_period=8,
            reliability=0.96,
            product_quality=0.95,
            cost=20000,
            special_delivery_cost=26000,
        ),
        Supplier(
            name="Нейтрон",
            product_name="Контроллеры",
            material_type="Электроника",
            delivery_period=15,
            special_delivery_period=12,
            reliability=0.94,
            product_quality=0.96,
            cost=30000,
            special_delivery_cost=39000,
        ),
        Supplier(
            name="Джетикс",
            product_name="Маховик",
            material_type="Механика",
            delivery_period=7,
            special_delivery_period=5,
            reliability=0.92,
            product_quality=0.90,
            cost=32000,
            special_delivery_cost=41600,
        ),
        Supplier(
            name="Алмаз",
            product_name="Маховик",
            material_type="Механика",
            delivery_period=4,
            special_delivery_period=3,
            reliability=0.94,
            product_quality=0.98,
            cost=25000,
            special_delivery_cost=32500,
        ),
        Supplier(
            name="Неон",
            product_name="Маховик",
            material_type="Механика",
            delivery_period=5,
            special_delivery_period=3,
            reliability=0.97,
            product_quality=0.96,
            cost=17000,
            special_delivery_cost=22100,
        ),
        Supplier(
            name="Брик",
            product_name="Несущая конструкция",
            material_type="Конструкция",
            delivery_period=5,
            special_delivery_period=3,
            reliability=0.94,
            product_quality=0.94,
            cost=20000,
            special_delivery_cost=26000,
        ),
        Supplier(
            name="Колосс",
            product_name="Несущая конструкция",
            material_type="Конструкция",
            delivery_period=10,
            special_delivery_period=8,
            reliability=0.96,
            product_quality=0.98,
            cost=17000,
            special_delivery_cost=22100,
        ),
        Supplier(
            name="Шиммер",
            product_name="Несущая конструкция",
            material_type="Конструкция",
            delivery_period=6,
            special_delivery_period=4,
            reliability=0.93,
            product_quality=0.95,
            cost=25000,
            special_delivery_cost=32500,
        ),
        Supplier(
            name="Arua",
            product_name="Солнечные панели",
            material_type="Электроника",
            delivery_period=7,
            special_delivery_period=5,
            reliability=0.94,
            product_quality=0.92,
            cost=28000,
            special_delivery_cost=36400,
        ),
        Supplier(
            name="Energylife",
            product_name="Солнечные панели",
            material_type="Электроника",
            delivery_period=7,
            special_delivery_period=5,
            reliability=0.95,
            product_quality=0.98,
            cost=16000,
            special_delivery_cost=20800,
        ),
        Supplier(
            name="Xtra",
            product_name="Солнечные панели",
            material_type="Электроника",
            delivery_period=6,
            special_delivery_period=4,
            reliability=0.95,
            product_quality=0.97,
            cost=14000,
            special_delivery_cost=18200,
        ),
        Supplier(
            name="Tempo",
            product_name="Датчики температуры",
            material_type="Электроника",
            delivery_period=4,
            special_delivery_period=3,
            reliability=0.95,
            product_quality=0.96,
            cost=20000,
            special_delivery_cost=26000,
        ),
        Supplier(
            name="Poison",
            product_name="Датчики температуры",
            material_type="Электроника",
            delivery_period=5,
            special_delivery_period=3,
            reliability=0.95,
            product_quality=0.93,
            cost=3500,
            special_delivery_cost=4550,
        ),
        Supplier(
            name="Umbrella",
            product_name="Датчики температуры",
            material_type="Электроника",
            delivery_period=10,
            special_delivery_period=8,
            reliability=0.93,
            product_quality=0.94,
            cost=4200,
            special_delivery_cost=5460,
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
            name="Сборочный стенд",
            equipment_type="Сборочное оборудование",
            reliability=0.90,
            maintenance_period=25,
            maintenance_cost=12000,
            cost=450000,
            repair_cost=50000,
            repair_time=36,
        ),
        Equipment(
            name="Контрольный стенд",
            equipment_type="Измерительное оборудование",
            reliability=0.95,
            maintenance_period=60,
            maintenance_cost=6000,
            cost=320000,
            repair_cost=42000,
            repair_time=18,
        ),
        Equipment(
            name="Паяльная станция",
            equipment_type="Сварочное оборудование",
            reliability=0.88,
            maintenance_period=20,
            maintenance_cost=9000,
            cost=120000,
            repair_cost=25000,
            repair_time=16,
        ),
        Equipment(
            name="Монтажный стол",
            equipment_type="Станок",
            reliability=0.90,
            maintenance_period=30,
            maintenance_cost=7000,
            cost=100000,
            repair_cost=20000,
            repair_time=12,
        ),
        Equipment(
            name="Рабочий стол",
            equipment_type="Станок",
            reliability=0.92,
            maintenance_period=30,
            maintenance_cost=6000,
            cost=80000,
            repair_cost=18000,
            repair_time=10,
        ),
        Equipment(
            name="Кран-балка",
            equipment_type="Транспортное оборудование",
            reliability=0.90,
            maintenance_period=45,
            maintenance_cost=11000,
            cost=250000,
            repair_cost=35000,
            repair_time=24,
        ),
        Equipment(
            name="Вибростенд",
            equipment_type="Испытательное оборудование",
            reliability=0.93,
            maintenance_period=60,
            maintenance_cost=15000,
            cost=400000,
            repair_cost=55000,
            repair_time=48,
        ),
        Equipment(
            name="Погрузчик",
            equipment_type="Транспорт",
            reliability=0.85,
            maintenance_period=40,
            maintenance_cost=10000,
            cost=300000,
            repair_cost=45000,
            repair_time=24,
        ),
    ]

    for equipment in equipment_list:
        try:
            await equipment_repo.save(equipment)
        except Exception as e:
            print(f"Ошибка при создании оборудования {equipment.name}: {e}")

    # 4. Создаем рабочие места (Workplaces)
    workplace_repo = WorkplaceRepository(session)

    workplace_defs = [
        {
            "name": "Сборка бортового комплекса управления",
            "speciality": Specialization.ASSEMBLER.value,
            "qualification": Qualification.VII.value,
            "equipment": "Сборочный стенд",
            "stages": ["Сборка бортового комплекса управления"],
        },
        {
            "name": "Контроль правильности сборки",
            "speciality": Specialization.QUALITY_CONTROLLER.value,
            "qualification": Qualification.VIII.value,
            "equipment": "Контрольный стенд",
            "stages": ["Контроль правильности сборки"],
        },
        {
            "name": "Пайка проводки плат",
            "speciality": Specialization.ASSEMBLER.value,
            "qualification": Qualification.VII.value,
            "equipment": "Паяльная станция",
            "stages": ["Пайка проводки плат"],
        },
        {
            "name": "Коммутация проводов",
            "speciality": Specialization.ASSEMBLER.value,
            "qualification": Qualification.VI.value,
            "equipment": "Монтажный стол",
            "stages": ["Коммутация проводов"],
        },
        {
            "name": "Установка электроники в каркас",
            "speciality": Specialization.ASSEMBLER.value,
            "qualification": Qualification.IV.value,
            "equipment": "Рабочий стол",
            "stages": ["Установка электроники в каркас"],
        },
        {
            "name": "Установка солнечных панелей и антенн",
            "speciality": Specialization.ASSEMBLER.value,
            "qualification": Qualification.V.value,
            "equipment": "Кран-балка",
            "stages": ["Установка солнечных панелей и антенн"],
        },
        {
            "name": "Контроль правильности установки",
            "speciality": Specialization.QUALITY_CONTROLLER.value,
            "qualification": Qualification.VIII.value,
            "equipment": "Контрольный стенд",
            "stages": ["Контроль правильности установки"],
        },
        {
            "name": "Испытания на работоспособность и прочность",
            "speciality": Specialization.ENGINEER_TECHNOLOGIST.value,
            "qualification": Qualification.IX.value,
            "equipment": "Вибростенд",
            "stages": ["Испытания на работоспособность и прочность"],
        },
        {
            "name": "Транспортировка",
            "speciality": Specialization.LOGIST.value,
            "qualification": Qualification.IX.value,
            "equipment": "Погрузчик",
            "stages": ["Транспортировка"],
        },
    ]

    workplaces = []
    for index, definition in enumerate(workplace_defs):
        workplace = Workplace(
            workplace_id=str(uuid4()),
            workplace_name=definition["name"],
            required_speciality=definition["speciality"],
            required_qualification=definition["qualification"],
            required_equipment=definition["equipment"],
            required_stages=definition["stages"],
            is_start_node=index == 0,
            is_end_node=index == len(workplace_defs) - 1,
            next_workplace_ids=[],
        )
        workplaces.append(workplace)

    # Связываем этапы последовательно в производственный поток
    for idx in range(len(workplaces) - 1):
        workplaces[idx].next_workplace_ids = [workplaces[idx + 1].workplace_id]

    for workplace in workplaces:
        try:
            await workplace_repo.save(workplace)
        except Exception as e:
            print(f"Ошибка при создании рабочего места {workplace.workplace_name}: {e}")

    # 5. Создаем потребителей (Consumers)
    consumer_repo = ConsumerRepository(session)

    consumers = [
        Consumer(
            name="Роскосмос",
            type=ConsumerType.GOVERMANT.value,
        ),
        Consumer(
            name="Росгидромет",
            type=ConsumerType.GOVERMANT.value,
        ),
        Consumer(
            name="Сфера",
            type=ConsumerType.NOT_GOVERMANT.value,
        ),
        Consumer(
            name="НФТ",
            type=ConsumerType.NOT_GOVERMANT.value,
        ),
        Consumer(
            name="Ростех",
            type=ConsumerType.GOVERMANT.value,
        ),
        Consumer(
            name="Минтранс России",
            type=ConsumerType.GOVERMANT.value,
        ),
        Consumer(
            name="Три Солнца",
            type=ConsumerType.NOT_GOVERMANT.value,
        ),
        Consumer(
            consumer_id=str(uuid4()),
            name="МИР",
            type=ConsumerType.NOT_GOVERMANT.value,
        ),
        Consumer(
            consumer_id=str(uuid4()),
            name="ГЛОНАСС",
            type=ConsumerType.GOVERMANT.value,
        ),
        Consumer(
            consumer_id=str(uuid4()),
            name="Фонд перспективных исследований",
            type=ConsumerType.GOVERMANT.value,
        ),
        Consumer(
            consumer_id=str(uuid4()),
            name="РОСКОМ",
            type=ConsumerType.NOT_GOVERMANT.value,
        ),
        Consumer(
            consumer_id=str(uuid4()),
            name="Роснано",
            type=ConsumerType.NOT_GOVERMANT.value,
        ),
        Consumer(
            consumer_id=str(uuid4()),
            name="ВНИИЭМ",
            type=ConsumerType.GOVERMANT.value,
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
    consumer_by_name = {consumer.name: consumer for consumer in all_consumers}

    if all_consumers:
        tenders = [
            Tender(
                tender_id=str(uuid4()),
                consumer=consumer_by_name.get("Роскосмос", all_consumers[0]),
                cost=727_200_000,
                quantity_of_products=3000,
                penalty_per_day=450_000,
                warranty_years=3,
                payment_form=PaymentForm.FULL_ADVANCE.value,
            ),
            Tender(
                tender_id=str(uuid4()),
                consumer=consumer_by_name.get("Росгидромет", all_consumers[0]),
                cost=484_800_000,
                quantity_of_products=2000,
                penalty_per_day=360_000,
                warranty_years=2,
                payment_form=PaymentForm.FULL_ADVANCE.value,
            ),
            Tender(
                tender_id=str(uuid4()),
                consumer=consumer_by_name.get("Сфера", all_consumers[0]),
                cost=163_800_000,
                quantity_of_products=1000,
                penalty_per_day=117_000,
                warranty_years=1,
                payment_form=PaymentForm.PARTIAL_ADVANCE.value,
            ),
            Tender(
                tender_id=str(uuid4()),
                consumer=consumer_by_name.get("НФТ", all_consumers[0]),
                cost=257_600_000,
                quantity_of_products=1000,
                penalty_per_day=184_000,
                warranty_years=1,
                payment_form=PaymentForm.PARTIAL_ADVANCE.value,
            ),
            Tender(
                tender_id=str(uuid4()),
                consumer=consumer_by_name.get("Ростех", all_consumers[0]),
                cost=484_800_000,
                quantity_of_products=2000,
                penalty_per_day=405_000,
                warranty_years=2,
                payment_form=PaymentForm.FULL_ADVANCE.value,
            ),
            Tender(
                tender_id=str(uuid4()),
                consumer=consumer_by_name.get("Роскосмос", all_consumers[0]),
                cost=662_400_000,
                quantity_of_products=5000,
                penalty_per_day=810_000,
                warranty_years=3,
                payment_form=PaymentForm.FULL_ADVANCE.value,
            ),
            Tender(
                tender_id=str(uuid4()),
                consumer=consumer_by_name.get("Минтранс России", all_consumers[0]),
                cost=969_600_000,
                quantity_of_products=4000,
                penalty_per_day=720_000,
                warranty_years=3,
                payment_form=PaymentForm.FULL_ADVANCE.value,
            ),
            Tender(
                tender_id=str(uuid4()),
                consumer=consumer_by_name.get("Три Солнца", all_consumers[0]),
                cost=562_800_000,
                quantity_of_products=3000,
                penalty_per_day=402_000,
                warranty_years=2,
                payment_form=PaymentForm.PARTIAL_ADVANCE.value,
            ),
            Tender(
                tender_id=str(uuid4()),
                consumer=consumer_by_name.get("МИР", all_consumers[0]),
                cost=565_600_000,
                quantity_of_products=2000,
                penalty_per_day=404_000,
                warranty_years=2,
                payment_form=PaymentForm.PARTIAL_ADVANCE.value,
            ),
            Tender(
                tender_id=str(uuid4()),
                consumer=consumer_by_name.get("ГЛОНАСС", all_consumers[0]),
                cost=683_200_000,
                quantity_of_products=4000,
                penalty_per_day=765_000,
                warranty_years=3,
                payment_form=PaymentForm.FULL_ADVANCE.value,
            ),
            Tender(
                tender_id=str(uuid4()),
                consumer=consumer_by_name.get("Роскосмос", all_consumers[0]),
                cost=380_800_000,
                quantity_of_products=2000,
                penalty_per_day=225_000,
                warranty_years=2,
                payment_form=PaymentForm.FULL_ADVANCE.value,
            ),
            Tender(
                tender_id=str(uuid4()),
                consumer=consumer_by_name.get(
                    "Фонд перспективных исследований", all_consumers[0]
                ),
                cost=462_400_000,
                quantity_of_products=3000,
                penalty_per_day=400_000,
                warranty_years=2,
                payment_form=PaymentForm.FULL_ADVANCE.value,
            ),
            Tender(
                tender_id=str(uuid4()),
                consumer=consumer_by_name.get("РОСКОМ", all_consumers[0]),
                cost=882_000_000,
                quantity_of_products=1000,
                penalty_per_day=202_000,
                warranty_years=3,
                payment_form=PaymentForm.PARTIAL_ADVANCE.value,
            ),
            Tender(
                tender_id=str(uuid4()),
                consumer=consumer_by_name.get("Роснано", all_consumers[0]),
                cost=882_800_000,
                quantity_of_products=1000,
                penalty_per_day=202_000,
                warranty_years=3,
                payment_form=PaymentForm.PARTIAL_ADVANCE.value,
            ),
            Tender(
                tender_id=str(uuid4()),
                consumer=consumer_by_name.get("ВНИИЭМ", all_consumers[0]),
                cost=684_800_000,
                quantity_of_products=2000,
                penalty_per_day=216_000,
                warranty_years=3,
                payment_form=PaymentForm.FULL_ADVANCE.value,
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
            name="Внедрение системы 5S",
            is_implemented=False,
            implementation_cost=200000,
            efficiency_gain=0.15,
        ),
        LeanImprovement(
            name="Канбан система",
            is_implemented=False,
            implementation_cost=300000,
            efficiency_gain=0.20,
        ),
        LeanImprovement(
            name="Автоматизация учета",
            is_implemented=False,
            implementation_cost=500000,
            efficiency_gain=0.25,
        ),
        LeanImprovement(
            name="Обучение персонала",
            is_implemented=False,
            implementation_cost=150000,
            efficiency_gain=0.10,
        ),
        LeanImprovement(
            name="Poka-Yoke на ключевых операциях",
            is_implemented=False,
            implementation_cost=120000,
            efficiency_gain=0.08,
        ),
        LeanImprovement(
            name="SMED для переналадки линий",
            is_implemented=False,
            implementation_cost=180000,
            efficiency_gain=0.12,
        ),
        LeanImprovement(
            name="Андон и визуализация статуса",
            is_implemented=False,
            implementation_cost=90000,
            efficiency_gain=0.06,
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
