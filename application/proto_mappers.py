"""Мапперы для преобразования между доменными сущностями и proto сообщениями."""

import logging
from typing import Optional
from uuid import UUID

logger = logging.getLogger(__name__)

from grpc_generated.simulator_pb2 import (
    Worker as WorkerProto,
    Supplier as SupplierProto,
    Equipment as EquipmentProto,
    Workplace as WorkplaceProto,
    Consumer as ConsumerProto,
    Tender as TenderProto,
    Logist as LogistProto,
    LeanImprovement as LeanImprovementProto,
    Simulation as SimulationProto,
    SimulationParameters as SimulationParametersProto,
    SimulationResults as SimulationResultsProto,
    Route as RouteProto,
    ProcessGraph as ProcessGraphProto,
    Warehouse as WarehouseProto,
    ProductionPlanRow as ProductionPlanRowProto,
    ProductionSchedule as ProductionScheduleProto,
    Certification as CertificationProto,
    UnplannedRepair as UnplannedRepairProto,
    RequiredMaterial as RequiredMaterialProto,
    FactoryMetrics as FactoryMetricsProto,
    WarehouseMetrics as WarehouseMetricsProto,
    ProductionMetrics as ProductionMetricsProto,
    QualityMetrics as QualityMetricsProto,
    EngineeringMetrics as EngineeringMetricsProto,
    CommercialMetrics as CommercialMetricsProto,
    ProcurementMetrics as ProcurementMetricsProto,
    DistributionStrategy as DistributionStrategyProto,
)

from domain import (
    Worker,
    Supplier,
    Equipment,
    Workplace,
    Consumer,
    Tender,
    Logist,
    Qualification,
    ConsumerType,
    PaymentForm,
    Specialization,
    LeanImprovement,
    Simulation,
    SimulationParameters,
    SimulationResults,
    DealingWithDefects,
    SaleStrategest,
    ProductImpruvement,
    Route,
    ProcessGraph,
    Warehouse,
    ProductionPlanRow,
    ProductionSchedule,
    Certification,
    DistributionStrategy,
    UnplannedRepair,
    RequiredMaterial,
)
from domain.metrics import (
    FactoryMetrics,
    WarehouseMetrics,
    ProductionMetrics,
    QualityMetrics,
    EngineeringMetrics,
    CommercialMetrics,
    ProcurementMetrics,
)


def domain_worker_to_proto(domain: Worker) -> WorkerProto:
    """Преобразует доменную сущность Worker в proto сообщение."""
    from domain import Qualification

    proto = WorkerProto()
    proto.worker_id = domain.worker_id or ""
    proto.name = domain.name

    # qualification должен быть int в proto и домене
    # Защита от случаев, когда qualification может быть строкой или enum
    if isinstance(domain.qualification, int):
        proto.qualification = domain.qualification
    elif isinstance(domain.qualification, str):
        # Если это строка, пытаемся преобразовать через enum
        try:
            qual_enum = Qualification[domain.qualification]
            proto.qualification = qual_enum.value
        except (ValueError, KeyError):
            try:
                qual_enum = Qualification(int(domain.qualification))
                proto.qualification = qual_enum.value
            except (ValueError, TypeError):
                proto.qualification = Qualification.I.value
    elif hasattr(domain.qualification, "value"):
        proto.qualification = domain.qualification.value
    else:
        proto.qualification = Qualification.I.value

    proto.specialty = domain.specialty  # В домене это строка
    proto.salary = domain.salary
    return proto


def proto_worker_to_domain(proto: WorkerProto) -> Worker:
    """Преобразует proto сообщение Worker в доменную сущность."""
    return Worker(
        worker_id=proto.worker_id or "",
        name=proto.name,
        qualification=proto.qualification,  # int в proto и домене
        specialty=proto.specialty,  # string в proto и домене
        salary=proto.salary,
    )


def domain_logist_to_proto(domain: Logist) -> LogistProto:
    """Преобразует доменную сущность Logist в proto сообщение."""
    from domain import Qualification

    proto = LogistProto()
    proto.worker_id = domain.worker_id or ""
    proto.name = domain.name

    # qualification должен быть int в proto и домене
    # Защита от случаев, когда qualification может быть строкой или enum
    if isinstance(domain.qualification, int):
        proto.qualification = domain.qualification
    elif isinstance(domain.qualification, str):
        # Если это строка, пытаемся преобразовать через enum
        try:
            qual_enum = Qualification[domain.qualification]
            proto.qualification = qual_enum.value
        except (ValueError, KeyError):
            try:
                qual_enum = Qualification(int(domain.qualification))
                proto.qualification = qual_enum.value
            except (ValueError, TypeError):
                proto.qualification = Qualification.I.value
    elif hasattr(domain.qualification, "value"):
        proto.qualification = domain.qualification.value
    else:
        proto.qualification = Qualification.I.value

    proto.specialty = domain.specialty  # string в proto и домене
    proto.salary = domain.salary
    proto.speed = domain.speed
    proto.vehicle_type = domain.vehicle_type or ""  # string в proto и домене
    return proto


def domain_supplier_to_proto(domain: Supplier) -> SupplierProto:
    """Преобразует доменную сущность Supplier в proto сообщение."""
    proto = SupplierProto()
    proto.supplier_id = domain.supplier_id or ""
    proto.name = domain.name
    proto.product_name = domain.product_name
    proto.material_type = domain.material_type or ""
    proto.delivery_period = domain.delivery_period
    proto.special_delivery_period = domain.special_delivery_period
    proto.reliability = domain.reliability
    proto.product_quality = domain.product_quality
    proto.cost = domain.cost
    proto.special_delivery_cost = domain.special_delivery_cost
    proto.quality_inspection_enabled = domain.quality_inspection_enabled
    return proto


def proto_supplier_to_domain(proto: SupplierProto) -> Supplier:
    """Преобразует proto сообщение Supplier в доменную сущность."""
    return Supplier(
        supplier_id=proto.supplier_id or "",
        name=proto.name,
        product_name=proto.product_name,
        material_type=proto.material_type or "",
        delivery_period=proto.delivery_period,
        special_delivery_period=proto.special_delivery_period,
        reliability=proto.reliability,
        product_quality=proto.product_quality,
        cost=proto.cost,
        special_delivery_cost=proto.special_delivery_cost,
    )


def domain_equipment_to_proto(domain: Equipment) -> EquipmentProto:
    """Преобразует доменную сущность Equipment в proto сообщение."""
    proto = EquipmentProto()
    proto.equipment_id = domain.equipment_id or ""
    proto.name = domain.name
    proto.equipment_type = domain.equipment_type or ""
    proto.reliability = domain.reliability
    proto.maintenance_period = domain.maintenance_period  # обязательное поле в домене
    proto.maintenance_cost = domain.maintenance_cost
    proto.cost = domain.cost
    proto.repair_cost = domain.repair_cost
    proto.repair_time = domain.repair_time
    return proto


def proto_equipment_to_domain(proto: EquipmentProto) -> Equipment:
    """Преобразует proto сообщение Equipment в доменную сущность."""
    return Equipment(
        equipment_id=proto.equipment_id or "",
        name=proto.name,
        equipment_type=proto.equipment_type or "",
        reliability=proto.reliability,
        maintenance_period=proto.maintenance_period,  # обязательное поле
        maintenance_cost=proto.maintenance_cost,
        cost=proto.cost,
        repair_cost=proto.repair_cost,
        repair_time=proto.repair_time,
    )


def domain_consumer_to_proto(domain: Consumer) -> ConsumerProto:
    """Преобразует доменную сущность Consumer в proto сообщение."""
    proto = ConsumerProto()
    proto.consumer_id = domain.consumer_id or ""
    proto.name = domain.name
    proto.type = domain.type  # string в домене и proto
    return proto


def proto_consumer_to_domain(proto: ConsumerProto) -> Consumer:
    """Преобразует proto сообщение Consumer в доменную сущность."""
    consumer_id = ""
    if hasattr(proto, "consumer_id"):
        consumer_id = proto.consumer_id or ""

    return Consumer(
        consumer_id=consumer_id,
        name=proto.name,
        type=proto.type,  # string в proto и домене
    )


def domain_workplace_to_proto(domain: Workplace) -> WorkplaceProto:
    """Преобразует доменную сущность Workplace в proto сообщение."""
    proto = WorkplaceProto()
    proto.workplace_id = domain.workplace_id or ""
    proto.workplace_name = domain.workplace_name
    proto.required_speciality = domain.required_speciality
    proto.required_qualification = domain.required_qualification  # int в домене и proto
    proto.required_equipment = domain.required_equipment or ""

    # Преобразуем связанные объекты
    if domain.worker:
        proto.worker.CopyFrom(domain_worker_to_proto(domain.worker))

    if domain.equipment:
        proto.equipment.CopyFrom(domain_equipment_to_proto(domain.equipment))

    proto.required_stages.extend(domain.required_stages or [])

    # Преобразуем поля графа процесса
    proto.is_start_node = domain.is_start_node
    proto.is_end_node = domain.is_end_node
    proto.next_workplace_ids.extend(domain.next_workplace_ids or [])

    # Преобразуем координаты
    # Если None, используем 255 как sentinel значение "не установлено"
    # (координаты на сетке 7x7 это 0-6, поэтому 255 вне диапазона и безопасно использовать)
    domain_x = getattr(domain, "x", None)
    domain_y = getattr(domain, "y", None)
    if domain_x is not None and domain_y is not None:
        proto.x = domain_x
        proto.y = domain_y
    else:
        proto.x = 255
        proto.y = 255

    proto.x = domain_x if domain_x is not None else 255  # 255 = "не установлено"
    proto.y = domain_y if domain_y is not None else 255  # 255 = "не установлено"

    return proto


def proto_workplace_to_domain(proto: WorkplaceProto) -> Workplace:
    """Преобразует proto сообщение Workplace в доменную сущность."""
    # Преобразуем связанные объекты
    worker = None
    if proto.HasField("worker"):
        try:
            worker = proto_worker_to_domain(proto.worker)
        except Exception as e:
            logger.debug(f"Failed to convert worker proto to domain: {e}")
            worker = None

    equipment = None
    if proto.HasField("equipment"):
        try:
            equipment = proto_equipment_to_domain(proto.equipment)
        except Exception as e:
            logger.debug(f"Failed to convert equipment proto to domain: {e}")
            equipment = None

    return Workplace(
        workplace_id=proto.workplace_id or "",
        workplace_name=proto.workplace_name,
        required_speciality=proto.required_speciality,
        required_qualification=proto.required_qualification,  # int в proto и домене
        required_equipment=proto.required_equipment or "",
        worker=worker,
        equipment=equipment,
        required_stages=list(proto.required_stages),
        is_start_node=proto.is_start_node,
        is_end_node=proto.is_end_node,
        next_workplace_ids=list(proto.next_workplace_ids),
        x=(
            proto.x if proto.x != 255 else None
        ),  # 255 в proto означает None (не установлено)
        y=proto.y if proto.y != 255 else None,
    )


def domain_tender_to_proto(domain: Tender) -> TenderProto:
    """Преобразует доменную сущность Tender в proto сообщение."""
    proto = TenderProto()
    proto.tender_id = domain.tender_id or ""

    # Преобразуем consumer
    if domain.consumer:
        proto.consumer.CopyFrom(domain_consumer_to_proto(domain.consumer))

    proto.cost = domain.cost
    proto.quantity_of_products = domain.quantity_of_products
    proto.penalty_per_day = domain.penalty_per_day
    proto.warranty_years = domain.warranty_years
    proto.payment_form = domain.payment_form or ""  # string в домене и proto

    return proto


def proto_tender_to_domain(proto: TenderProto) -> Tender:
    """Преобразует proto сообщение Tender в доменную сущность."""
    # Преобразуем consumer
    consumer = None
    if proto.HasField("consumer"):
        consumer = proto_consumer_to_domain(proto.consumer)

    return Tender(
        tender_id=proto.tender_id or "",
        consumer=consumer or Consumer(name="", type=""),
        cost=proto.cost,
        quantity_of_products=proto.quantity_of_products,
        penalty_per_day=proto.penalty_per_day,
        warranty_years=proto.warranty_years,
        payment_form=proto.payment_form or "",  # string в proto и домене
    )


def domain_lean_improvement_to_proto(
    domain: LeanImprovement,
) -> LeanImprovementProto:
    """Преобразует доменную сущность LeanImprovement в proto сообщение."""
    proto = LeanImprovementProto()
    proto.improvement_id = domain.improvement_id or ""
    proto.name = domain.name
    proto.is_implemented = domain.is_implemented
    proto.implementation_cost = domain.implementation_cost
    proto.efficiency_gain = domain.efficiency_gain
    return proto


def proto_lean_improvement_to_domain(
    proto: LeanImprovementProto,
) -> LeanImprovement:
    """Преобразует proto сообщение LeanImprovement в доменную сущность."""
    return LeanImprovement(
        improvement_id=proto.improvement_id or "",
        name=proto.name,
        is_implemented=proto.is_implemented,
        implementation_cost=proto.implementation_cost,
        efficiency_gain=proto.efficiency_gain,
    )


def domain_route_to_proto(domain: Route) -> RouteProto:
    """Преобразует доменную сущность Route в proto сообщение."""
    proto = RouteProto()
    proto.length = domain.length
    proto.from_workplace = domain.from_workplace
    proto.to_workplace = domain.to_workplace
    return proto


def proto_route_to_domain(proto: RouteProto) -> Route:
    """Преобразует proto сообщение Route в доменную сущность."""
    return Route(
        length=proto.length,
        from_workplace=proto.from_workplace,
        to_workplace=proto.to_workplace,
    )


def domain_process_graph_to_proto(domain: ProcessGraph) -> ProcessGraphProto:
    """Преобразует доменную сущность ProcessGraph в proto сообщение."""
    proto = ProcessGraphProto()
    proto.process_graph_id = domain.process_graph_id or ""

    # Преобразуем workplaces
    for workplace in domain.workplaces:
        proto.workplaces.add().CopyFrom(domain_workplace_to_proto(workplace))

    # Преобразуем routes
    for route in domain.routes:
        proto.routes.add().CopyFrom(domain_route_to_proto(route))

    return proto


def proto_process_graph_to_domain(proto: ProcessGraphProto) -> ProcessGraph:
    """Преобразует proto сообщение ProcessGraph в доменную сущность."""
    # Преобразуем workplaces
    workplaces = [proto_workplace_to_domain(w) for w in proto.workplaces]

    # Преобразуем routes
    routes = [proto_route_to_domain(r) for r in proto.routes]

    return ProcessGraph(
        process_graph_id=proto.process_graph_id or "",
        workplaces=workplaces,
        routes=routes,
    )


def domain_warehouse_to_proto(domain: Warehouse) -> WarehouseProto:
    """Преобразует доменную сущность Warehouse в proto сообщение."""
    proto = WarehouseProto()
    proto.warehouse_id = domain.warehouse_id or ""
    proto.size = domain.size
    # loading является свойством (property), которое вычисляется из materials
    # domain.loading автоматически вычислит сумму всех материалов
    proto.loading = domain.loading

    # Преобразуем inventory_worker
    if domain.inventory_worker:
        proto.inventory_worker.CopyFrom(domain_worker_to_proto(domain.inventory_worker))

    # Преобразуем materials
    for key, value in (domain.materials or {}).items():
        proto.materials[key] = value

    return proto


def proto_warehouse_to_domain(proto: WarehouseProto) -> Warehouse:
    """Преобразует proto сообщение Warehouse в доменную сущность."""
    # Преобразуем inventory_worker
    inventory_worker = None
    if proto.HasField("inventory_worker"):
        inventory_worker = proto_worker_to_domain(proto.inventory_worker)

    # Преобразуем materials
    # loading является свойством (property), которое вычисляется из materials
    # поэтому не нужно его устанавливать при создании объекта
    materials = dict(proto.materials) if proto.materials else {}

    return Warehouse(
        warehouse_id=proto.warehouse_id or "",
        inventory_worker=inventory_worker,
        size=proto.size,
        materials=materials,
    )


def domain_simulation_results_to_proto(
    domain: SimulationResults,
) -> SimulationResultsProto:
    """Преобразует доменную сущность SimulationResults в proto сообщение."""
    from grpc_generated.simulator_pb2 import (
        FactoryMetrics as FactoryMetricsProto,
        ProductionMetrics as ProductionMetricsProto,
        QualityMetrics as QualityMetricsProto,
        EngineeringMetrics as EngineeringMetricsProto,
        CommercialMetrics as CommercialMetricsProto,
        ProcurementMetrics as ProcurementMetricsProto,
    )
    from domain.metrics import (
        FactoryMetrics,
        ProductionMetrics,
        QualityMetrics,
        EngineeringMetrics,
        CommercialMetrics,
        ProcurementMetrics,
    )

    proto = SimulationResultsProto()
    proto.profit = domain.profit
    proto.cost = domain.cost
    proto.profitability = domain.profitability
    proto.step = domain.step

    # Преобразуем метрики
    if domain.factory_metrics:
        proto.factory_metrics.CopyFrom(
            domain_factory_metrics_obj_to_proto(domain.factory_metrics)
        )
    if domain.production_metrics:
        proto.production_metrics.CopyFrom(
            domain_production_metrics_obj_to_proto(domain.production_metrics)
        )
    if domain.quality_metrics:
        proto.quality_metrics.CopyFrom(
            domain_quality_metrics_obj_to_proto(domain.quality_metrics)
        )
    if domain.engineering_metrics:
        proto.engineering_metrics.CopyFrom(
            domain_engineering_metrics_obj_to_proto(domain.engineering_metrics)
        )
    if domain.commercial_metrics:
        proto.commercial_metrics.CopyFrom(
            domain_commercial_metrics_obj_to_proto(domain.commercial_metrics)
        )
    if domain.procurement_metrics:
        proto.procurement_metrics.CopyFrom(
            domain_procurement_metrics_obj_to_proto(domain.procurement_metrics)
        )

    return proto


def proto_simulation_results_to_domain(
    proto: SimulationResultsProto,
) -> SimulationResults:
    """Преобразует proto сообщение SimulationResults в доменную сущность."""
    from domain.metrics import (
        FactoryMetrics,
        ProductionMetrics,
        QualityMetrics,
        EngineeringMetrics,
        CommercialMetrics,
        ProcurementMetrics,
    )

    factory_metrics = None
    if proto.HasField("factory_metrics"):
        factory_metrics = proto_factory_metrics_to_domain(proto.factory_metrics)

    production_metrics = None
    if proto.HasField("production_metrics"):
        production_metrics = proto_production_metrics_to_domain(
            proto.production_metrics
        )

    quality_metrics = None
    if proto.HasField("quality_metrics"):
        quality_metrics = proto_quality_metrics_to_domain(proto.quality_metrics)

    engineering_metrics = None
    if proto.HasField("engineering_metrics"):
        engineering_metrics = proto_engineering_metrics_to_domain(
            proto.engineering_metrics
        )

    commercial_metrics = None
    if proto.HasField("commercial_metrics"):
        commercial_metrics = proto_commercial_metrics_to_domain(
            proto.commercial_metrics
        )

    procurement_metrics = None
    if proto.HasField("procurement_metrics"):
        procurement_metrics = proto_procurement_metrics_to_domain(
            proto.procurement_metrics
        )

    return SimulationResults(
        profit=proto.profit,
        cost=proto.cost,
        profitability=proto.profitability,
        factory_metrics=factory_metrics,
        production_metrics=production_metrics,
        quality_metrics=quality_metrics,
        engineering_metrics=engineering_metrics,
        commercial_metrics=commercial_metrics,
        procurement_metrics=procurement_metrics,
        step=proto.step,
    )


def domain_simulation_parameters_to_proto(
    domain: SimulationParameters,
) -> SimulationParametersProto:
    """Преобразует доменную сущность SimulationParameters в proto сообщение."""
    proto = SimulationParametersProto()

    # Преобразуем logist
    if domain.logist:
        proto.logist.CopyFrom(domain_logist_to_proto(domain.logist))

    # Преобразуем suppliers
    for supplier in domain.suppliers:
        proto.suppliers.add().CopyFrom(domain_supplier_to_proto(supplier))

    # Преобразуем backup_suppliers
    for supplier in domain.backup_suppliers:
        proto.backup_suppliers.add().CopyFrom(domain_supplier_to_proto(supplier))

    # Преобразуем warehouses
    if domain.materials_warehouse:
        proto.materials_warehouse.CopyFrom(
            domain_warehouse_to_proto(domain.materials_warehouse)
        )
    if domain.product_warehouse:
        proto.product_warehouse.CopyFrom(
            domain_warehouse_to_proto(domain.product_warehouse)
        )

    # Преобразуем processes
    if domain.processes:
        proto.processes.CopyFrom(domain_process_graph_to_proto(domain.processes))

    # Преобразуем tenders
    for tender in domain.tenders:
        proto.tenders.add().CopyFrom(domain_tender_to_proto(tender))

    # Преобразуем dealing_with_defects
    if isinstance(domain.dealing_with_defects, DealingWithDefects):
        proto.dealing_with_defects = domain.dealing_with_defects.value
    else:
        proto.dealing_with_defects = str(domain.dealing_with_defects)

    # Преобразуем production_improvements (теперь список LeanImprovement)
    for improvement in domain.production_improvements:
        proto.production_improvements.add().CopyFrom(
            domain_lean_improvement_to_proto(improvement)
        )

    # Преобразуем sales_strategy
    if isinstance(domain.sales_strategy, SaleStrategest):
        proto.sales_strategy = domain.sales_strategy.value
    else:
        proto.sales_strategy = str(domain.sales_strategy)

    # Преобразуем production_schedule
    if domain.production_schedule:
        proto.production_schedule.CopyFrom(
            domain_production_schedule_to_proto(domain.production_schedule)
        )

    # Преобразуем certifications
    for cert in domain.certifications:
        proto.certifications.add().CopyFrom(domain_certification_to_proto(cert))

    # Преобразуем lean_improvements
    for improvement in domain.lean_improvements:
        proto.lean_improvements.add().CopyFrom(
            domain_lean_improvement_to_proto(improvement)
        )

    # Преобразуем distribution_strategy
    proto.distribution_strategy = (
        domain.distribution_strategy.value
        if hasattr(domain.distribution_strategy, "value")
        else domain.distribution_strategy
    )

    # Преобразуем дополнительные поля
    proto.step = domain.step
    proto.capital = domain.capital

    return proto


def proto_simulation_parameters_to_domain(
    proto: SimulationParametersProto,
) -> SimulationParameters:
    """Преобразует proto сообщение SimulationParameters в доменную сущность."""
    from domain import ProcessGraph, Warehouse

    # Преобразуем logist
    logist = None
    if proto.HasField("logist") and proto.logist.worker_id:
        logist = proto_logist_to_domain(proto.logist)

    # Преобразуем suppliers
    suppliers = [proto_supplier_to_domain(s) for s in proto.suppliers]
    backup_suppliers = [proto_supplier_to_domain(s) for s in proto.backup_suppliers]

    # Преобразуем tenders
    tenders = []
    for tender_proto in proto.tenders:
        if tender_proto.tender_id:
            tenders.append(proto_tender_to_domain(tender_proto))

    # Преобразуем dealing_with_defects
    try:
        dealing_with_defects = DealingWithDefects(proto.dealing_with_defects)
    except (ValueError, KeyError):
        dealing_with_defects = DealingWithDefects.NONE

    # Преобразуем sales_strategy
    try:
        sales_strategy = SaleStrategest(proto.sales_strategy)
    except (ValueError, KeyError):
        sales_strategy = SaleStrategest.NONE

    # Преобразуем production_improvements (теперь список LeanImprovement)
    production_improvements = []
    for improvement_proto in proto.production_improvements:
        production_improvements.append(
            proto_lean_improvement_to_domain(improvement_proto)
        )

    # Преобразуем warehouses
    materials_warehouse = Warehouse(size=1000, materials={})
    if proto.HasField("materials_warehouse"):
        materials_warehouse = proto_warehouse_to_domain(proto.materials_warehouse)

    product_warehouse = Warehouse(size=1000, materials={})
    if proto.HasField("product_warehouse"):
        product_warehouse = proto_warehouse_to_domain(proto.product_warehouse)

    # Преобразуем processes
    processes = ProcessGraph()
    if proto.HasField("processes"):
        processes = proto_process_graph_to_domain(proto.processes)

    # Преобразуем production_schedule
    from domain import ProductionSchedule

    production_schedule = ProductionSchedule()
    if proto.HasField("production_schedule"):
        production_schedule = proto_production_schedule_to_domain(
            proto.production_schedule
        )

    # Преобразуем certifications
    certifications = []
    for cert_proto in proto.certifications:
        certifications.append(proto_certification_to_domain(cert_proto))

    # Преобразуем lean_improvements
    lean_improvements = []
    for improvement_proto in proto.lean_improvements:
        lean_improvements.append(proto_lean_improvement_to_domain(improvement_proto))

    # Преобразуем distribution_strategy
    try:
        distribution_strategy = DistributionStrategy(proto.distribution_strategy)
    except (ValueError, KeyError):
        distribution_strategy = DistributionStrategy.DISTRIBUTION_STRATEGY_UNSPECIFIED

    return SimulationParameters(
        logist=logist,
        suppliers=suppliers,
        backup_suppliers=backup_suppliers,
        materials_warehouse=materials_warehouse,
        product_warehouse=product_warehouse,
        processes=processes,
        tenders=tenders,
        dealing_with_defects=dealing_with_defects,
        production_improvements=production_improvements,
        sales_strategy=sales_strategy,
        production_schedule=production_schedule,
        certifications=certifications,
        lean_improvements=lean_improvements,
        distribution_strategy=distribution_strategy,
        step=proto.step,
        capital=proto.capital if proto.capital else 10000000,
    )


def proto_logist_to_domain(proto: LogistProto) -> Logist:
    """Преобразует proto сообщение Logist в доменную сущность."""
    return Logist(
        worker_id=proto.worker_id or "",
        name=proto.name,
        qualification=proto.qualification,  # int в proto и домене
        specialty=proto.specialty,  # string в proto и домене
        salary=proto.salary,
        speed=proto.speed,
        vehicle_type=proto.vehicle_type or "",  # string в proto и домене
    )


def domain_simulation_to_proto(domain: Simulation) -> SimulationProto:
    """Преобразует доменную сущность Simulation в proto сообщение."""
    proto = SimulationProto()
    proto.capital = domain.capital
    proto.simulation_id = domain.simulation_id or ""
    proto.room_id = domain.room_id or ""
    proto.is_completed = domain.is_completed

    # Преобразуем parameters (список в proto)
    for params in domain.parameters:
        proto.parameters.add().CopyFrom(domain_simulation_parameters_to_proto(params))

    # Преобразуем results (список в proto)
    for results in domain.results:
        proto.results.add().CopyFrom(domain_simulation_results_to_proto(results))

    return proto


def proto_simulation_to_domain(proto: SimulationProto) -> Simulation:
    """Преобразует proto сообщение Simulation в доменную сущность."""
    # Преобразуем parameters (список в proto)
    parameters = [proto_simulation_parameters_to_domain(p) for p in proto.parameters]
    if not parameters:
        parameters = [SimulationParameters()]

    # Преобразуем results (список в proto)
    results = [proto_simulation_results_to_domain(r) for r in proto.results]
    if not results:
        results = [SimulationResults()]

    return Simulation(
        capital=proto.capital,
        simulation_id=proto.simulation_id or "",
        parameters=parameters,
        results=results,
        room_id=proto.room_id or "",
        is_completed=proto.is_completed,
    )


# Мапперы для метрик


def domain_factory_metrics_to_proto(metrics_data: dict) -> "FactoryMetrics":
    """Преобразует словарь метрик завода в proto объект."""
    from grpc_generated.simulator_pb2 import FactoryMetrics, WarehouseMetrics

    proto = FactoryMetrics()
    proto.profitability = metrics_data.get("profitability", 0.0)
    proto.on_time_delivery_rate = metrics_data.get("on_time_delivery_rate", 0.0)
    proto.oee = metrics_data.get("oee", 0.0)
    proto.total_procurement_cost = metrics_data.get("total_procurement_cost", 0)
    proto.defect_rate = metrics_data.get("defect_rate", 0.0)

    # Преобразуем метрики складов
    warehouse_metrics = metrics_data.get("warehouse_metrics", {})
    for warehouse_type, warehouse_data in warehouse_metrics.items():
        proto_warehouse = WarehouseMetrics()
        proto_warehouse.fill_level = warehouse_data.get("fill_level", 0.0)
        proto_warehouse.current_load = warehouse_data.get("current_load", 0)
        proto_warehouse.max_capacity = warehouse_data.get("max_capacity", 0)

        # Преобразуем уровни материалов
        material_levels = warehouse_data.get("material_levels", {})
        for material_name, level in material_levels.items():
            proto_warehouse.material_levels[material_name] = level

        proto.warehouse_metrics[warehouse_type].CopyFrom(proto_warehouse)

    return proto


def domain_production_metrics_to_proto(metrics_data: dict) -> "ProductionMetrics":
    """Преобразует словарь метрик производства в proto объект."""
    from grpc_generated.simulator_pb2 import ProductionMetrics, UnplannedRepair

    proto = ProductionMetrics()
    proto.average_equipment_utilization = metrics_data.get(
        "average_equipment_utilization", 0.0
    )
    proto.wip_count = metrics_data.get("wip_count", 0)
    proto.finished_goods_count = metrics_data.get("finished_goods_count", 0)

    # Преобразуем месячную продуктивность
    monthly_data = metrics_data.get("monthly_productivity", [])
    for item in monthly_data:
        monthly_proto = ProductionMetrics.MonthlyProductivity()
        monthly_proto.month = item.get("month", "")
        monthly_proto.units_produced = item.get("units_produced", 0)
        proto.monthly_productivity.append(monthly_proto)

    # Преобразуем запасы материалов
    material_reserves = metrics_data.get("material_reserves", {})
    for material_name, quantity in material_reserves.items():
        proto.material_reserves[material_name] = quantity

    # Преобразуем внеплановые ремонты
    unplanned_repairs_data = metrics_data.get("unplanned_repairs", {})
    if unplanned_repairs_data:
        unplanned_repairs_proto = UnplannedRepair()
        unplanned_repairs_proto.total_repair_cost = unplanned_repairs_data.get(
            "total_repair_cost", 0
        )

        repairs = unplanned_repairs_data.get("repairs", [])
        for repair in repairs:
            repair_proto = UnplannedRepair.RepairRecord()
            repair_proto.month = repair.get("month", "")
            repair_proto.repair_cost = repair.get("repair_cost", 0)
            repair_proto.equipment_id = repair.get("equipment_id", "")
            repair_proto.reason = repair.get("reason", "")
            unplanned_repairs_proto.repairs.append(repair_proto)

        proto.unplanned_repairs.CopyFrom(unplanned_repairs_proto)

    return proto


def domain_quality_metrics_to_proto(metrics_data: dict) -> "QualityMetrics":
    """Преобразует словарь метрик качества в proto объект."""
    from grpc_generated.simulator_pb2 import QualityMetrics

    proto = QualityMetrics()
    proto.defect_percentage = metrics_data.get("defect_percentage", 0.0)
    proto.good_output_percentage = metrics_data.get("good_output_percentage", 0.0)
    proto.average_material_quality = metrics_data.get("average_material_quality", 0.0)
    proto.average_supplier_failure_probability = metrics_data.get(
        "average_supplier_failure_probability", 0.0
    )
    proto.procurement_volume = metrics_data.get("procurement_volume", 0)

    # Преобразуем причины дефектов
    defect_causes = metrics_data.get("defect_causes", [])
    for cause in defect_causes:
        cause_proto = QualityMetrics.DefectCause()
        cause_proto.cause = cause.get("cause", "")
        cause_proto.count = cause.get("count", 0)
        cause_proto.percentage = cause.get("percentage", 0.0)
        proto.defect_causes.append(cause_proto)

    return proto


def domain_engineering_metrics_to_proto(metrics_data: dict) -> "EngineeringMetrics":
    """Преобразует словарь инженерных метрик в proto объект."""
    from grpc_generated.simulator_pb2 import (
        EngineeringMetrics,
        OperationTimingChart,
        DowntimeChart,
    )

    proto = EngineeringMetrics()
    proto.mttr = metrics_data.get("mttr", 0.0)
    proto.mtbf = metrics_data.get("mtbf", 0.0)

    # Преобразуем хронометраж операций
    operations = metrics_data.get("operation_timings", [])
    for op in operations:
        timing_proto = EngineeringMetrics.OperationTiming()
        timing_proto.operation_name = op.get("operation_name", "")
        timing_proto.cycle_time = op.get("cycle_time", 0)
        timing_proto.takt_time = op.get("takt_time", 0)
        timing_proto.timing_cost = op.get("timing_cost", 0)
        proto.operation_timings.append(timing_proto)

    # Преобразуем причины простоев
    downtimes = metrics_data.get("downtime_records", [])
    for downtime in downtimes:
        downtime_proto = EngineeringMetrics.DowntimeRecord()
        downtime_proto.cause = downtime.get("cause", "")
        downtime_proto.total_minutes = downtime.get("total_minutes", 0)
        downtime_proto.average_per_shift = downtime.get("average_per_shift", 0.0)
        proto.downtime_records.append(downtime_proto)

    # Преобразуем анализ дефектов
    defects = metrics_data.get("defect_analysis", [])
    for defect in defects:
        defect_proto = EngineeringMetrics.DefectAnalysis()
        defect_proto.defect_type = defect.get("defect_type", "")
        defect_proto.count = defect.get("count", 0)
        defect_proto.percentage = defect.get("percentage", 0.0)
        defect_proto.cumulative_percentage = defect.get("cumulative_percentage", 0.0)
        proto.defect_analysis.append(defect_proto)

    # Преобразуем диаграмму спагетти (используется ProcessGraph)
    spaghetti_diagram = metrics_data.get("spaghetti_diagram", [])
    for workplace in spaghetti_diagram:
        workplace_proto = EngineeringMetrics.SpaghettiDiagram()
        workplace_proto.workplace = workplace.get("workplace", "")
        workplace_proto.distance = workplace.get("distance", 0)
        proto.spaghetti_diagram.append(workplace_proto)

    # Преобразуем графики хронометража
    timing_chart_data = metrics_data.get("timing_chart_data", [])
    if timing_chart_data:
        timing_chart = OperationTimingChart()
        for item in timing_chart_data:
            timing_data_proto = OperationTimingChart.TimingData()
            timing_data_proto.process_name = item.get("process_name", "")
            timing_data_proto.cycle_time = item.get("cycle_time", 0)
            timing_data_proto.takt_time = item.get("takt_time", 0)
            timing_data_proto.timing_cost = item.get("timing_cost", 0)
            timing_chart.timing_data.append(timing_data_proto)

        timing_chart.chart_type = "bar_chart"
        proto.operation_timing_chart.CopyFrom(timing_chart)

    # Преобразуем графики простоев
    downtime_chart_data = metrics_data.get("downtime_chart_data", [])
    if downtime_chart_data:
        downtime_chart = DowntimeChart()
        for item in downtime_chart_data:
            downtime_data_proto = DowntimeChart.DowntimeData()
            downtime_data_proto.process_name = item.get("process_name", "")
            downtime_data_proto.cause = item.get("cause", "")
            downtime_data_proto.downtime_minutes = item.get("downtime_minutes", 0)
            downtime_chart.downtime_data.append(downtime_data_proto)

        downtime_chart.chart_type = "bar_chart"
        proto.downtime_chart.CopyFrom(downtime_chart)

    return proto


def domain_commercial_metrics_to_proto(metrics_data: dict) -> "CommercialMetrics":
    """Преобразует словарь коммерческих метрик в proto объект."""
    from grpc_generated.simulator_pb2 import (
        CommercialMetrics,
        ModelMasteryChart,
        ProjectProfitabilityChart,
    )

    proto = CommercialMetrics()
    proto.customer_satisfaction = metrics_data.get("customer_satisfaction", 0.0)
    proto.market_share = metrics_data.get("market_share", 0.0)
    proto.tender_revenue_plan = metrics_data.get("tender_revenue_plan", 0)
    proto.total_payments = metrics_data.get("total_payments", 0)
    proto.total_receipts = metrics_data.get("total_receipts", 0)
    proto.on_time_completed_orders = metrics_data.get("on_time_completed_orders", 0)

    # Преобразуем выручку по годам
    yearly_revenues = metrics_data.get("yearly_revenues", [])
    for item in yearly_revenues:
        revenue_proto = CommercialMetrics.YearlyRevenue()
        revenue_proto.year = item.get("year", 0)
        revenue_proto.revenue = item.get("revenue", 0)
        proto.yearly_revenues.append(revenue_proto)

    # Преобразуем прогноз продаж
    sales_forecast = metrics_data.get("sales_forecast", {})
    for strategy, value in sales_forecast.items():
        proto.sales_forecast[strategy] = value

    # Преобразуем стоимость стратегий
    strategy_costs = metrics_data.get("strategy_costs", {})
    for strategy, cost in strategy_costs.items():
        proto.strategy_costs[strategy] = cost

    # Преобразуем граф тендеров
    tender_graph = metrics_data.get("tender_graph", [])
    for item in tender_graph:
        graph_point = CommercialMetrics.TenderGraphPoint()
        graph_point.strategy = item.get("strategy", "")
        graph_point.unit_size = item.get("unit_size", "")
        graph_point.is_mastered = item.get("is_mastered", False)
        proto.tender_graph.append(graph_point)

    # Преобразуем прибыльность проектов
    project_profitabilities = metrics_data.get("project_profitabilities", [])
    for item in project_profitabilities:
        profitability_proto = CommercialMetrics.ProjectProfitability()
        profitability_proto.project_name = item.get("project_name", "")
        profitability_proto.profitability = item.get("profitability", 0.0)
        proto.project_profitabilities.append(profitability_proto)

    # Преобразуем освоенные модели
    model_mastery_points = metrics_data.get("model_mastery_points", [])
    if model_mastery_points:
        model_mastery_chart = ModelMasteryChart()
        for item in model_mastery_points:
            model_point = ModelMasteryChart.ModelPoint()
            model_point.strategy = item.get("strategy", "")
            model_point.unit_size = item.get("unit_size", "")
            model_point.is_mastered = item.get("is_mastered", False)
            model_point.model_name = item.get("model_name", "")
            model_mastery_chart.model_points.append(model_point)

        proto.model_mastery_chart.CopyFrom(model_mastery_chart)

    # Преобразуем рентабельность проектов
    project_chart_data = metrics_data.get("project_chart_data", [])
    if project_chart_data:
        project_chart = ProjectProfitabilityChart()
        for item in project_chart_data:
            project_data = ProjectProfitabilityChart.ProjectData()
            project_data.project_name = item.get("project_name", "")
            project_data.profitability = item.get("profitability", 0.0)
            project_chart.projects.append(project_data)

        project_chart.chart_type = "bar_chart"
        proto.project_profitability_chart.CopyFrom(project_chart)

    return proto


def domain_procurement_metrics_to_proto(metrics_data: dict) -> "ProcurementMetrics":
    """Преобразует словарь метрик закупок в proto объект."""
    from grpc_generated.simulator_pb2 import ProcurementMetrics

    proto = ProcurementMetrics()
    proto.total_procurement_value = metrics_data.get("total_procurement_value", 0)

    # Преобразуем производительность поставщиков
    supplier_performances = metrics_data.get("supplier_performances", [])
    for item in supplier_performances:
        performance_proto = ProcurementMetrics.SupplierPerformance()
        performance_proto.supplier_id = item.get("supplier_id", "")
        performance_proto.delivered_quantity = item.get("delivered_quantity", 0)
        performance_proto.projected_defect_rate = item.get("projected_defect_rate", 0.0)
        performance_proto.planned_reliability = item.get("planned_reliability", 0.0)
        performance_proto.actual_reliability = item.get("actual_reliability", 0.0)
        performance_proto.planned_cost = item.get("planned_cost", 0)
        performance_proto.actual_cost = item.get("actual_cost", 0)
        performance_proto.actual_defect_count = item.get("actual_defect_count", 0)
        proto.supplier_performances.append(performance_proto)

    return proto


def domain_production_plan_row_to_proto(
    domain: ProductionPlanRow,
) -> ProductionPlanRowProto:
    """Преобразует доменную сущность ProductionPlanRow в proto сообщение."""
    proto = ProductionPlanRowProto()
    proto.tender_id = domain.tender_id
    proto.product_name = domain.product_name
    # Основные поля из продуктового плана
    proto.priority = domain.priority
    proto.plan_date = domain.plan_date
    proto.dse = domain.dse
    proto.short_set = domain.short_set
    proto.dse_name = domain.dse_name
    proto.planned_quantity = domain.planned_quantity
    proto.actual_quantity = domain.actual_quantity
    proto.remaining_to_produce = domain.remaining_to_produce
    proto.provision_status = domain.provision_status
    proto.note = domain.note
    proto.planned_completion_date = domain.planned_completion_date
    proto.cost_breakdown = domain.cost_breakdown
    proto.order_number = domain.order_number
    return proto


def proto_production_plan_row_to_domain(
    proto: ProductionPlanRowProto,
) -> ProductionPlanRow:
    """Преобразует proto сообщение ProductionPlanRow в доменную сущность."""
    return ProductionPlanRow(
        tender_id=proto.tender_id,
        product_name=proto.product_name,
        # Основные поля из продуктового плана
        priority=proto.priority,
        plan_date=proto.plan_date,
        dse=proto.dse,
        short_set=proto.short_set,
        dse_name=proto.dse_name,
        planned_quantity=proto.planned_quantity,
        actual_quantity=proto.actual_quantity,
        remaining_to_produce=proto.remaining_to_produce,
        provision_status=proto.provision_status,
        note=proto.note,
        planned_completion_date=proto.planned_completion_date,
        cost_breakdown=proto.cost_breakdown,
        order_number=proto.order_number,
    )


def domain_production_schedule_to_proto(
    domain: ProductionSchedule,
) -> ProductionScheduleProto:
    """Преобразует доменную сущность ProductionSchedule в proto сообщение."""
    proto = ProductionScheduleProto()
    for row in domain.rows:
        proto.rows.append(domain_production_plan_row_to_proto(row))
    return proto


def proto_production_schedule_to_domain(
    proto: ProductionScheduleProto,
) -> ProductionSchedule:
    """Преобразует proto сообщение ProductionSchedule в доменную сущность."""
    from domain import ProductionSchedule

    schedule = ProductionSchedule()
    for row_proto in proto.rows:
        schedule.rows.append(proto_production_plan_row_to_domain(row_proto))
    return schedule


def domain_certification_to_proto(domain: Certification) -> CertificationProto:
    """Преобразует доменную сущность Certification в proto сообщение."""
    proto = CertificationProto()
    proto.certificate_type = domain.certificate_type
    proto.is_obtained = domain.is_obtained
    proto.implementation_cost = domain.implementation_cost
    proto.implementation_time_days = domain.implementation_time_days
    return proto


def proto_certification_to_domain(proto: CertificationProto) -> Certification:
    """Преобразует proto сообщение Certification в доменную сущность."""
    return Certification(
        certificate_type=proto.certificate_type or "",
        is_obtained=proto.is_obtained,
        implementation_cost=proto.implementation_cost,
        implementation_time_days=proto.implementation_time_days,
    )


# Мапперы для новых сущностей


def domain_unplanned_repair_to_proto(domain: UnplannedRepair) -> UnplannedRepairProto:
    """Преобразует доменную сущность UnplannedRepair в proto сообщение."""
    proto = UnplannedRepairProto()

    for repair in domain.repairs:
        repair_proto = proto.repairs.add()
        repair_proto.month = repair.month
        repair_proto.repair_cost = repair.repair_cost
        repair_proto.equipment_id = repair.equipment_id
        repair_proto.reason = repair.reason

    proto.total_repair_cost = domain.total_repair_cost
    return proto


def proto_unplanned_repair_to_domain(proto: UnplannedRepairProto) -> UnplannedRepair:
    """Преобразует proto сообщение UnplannedRepair в доменную сущность."""
    repairs = []
    for repair_proto in proto.repairs:
        repair = UnplannedRepair.RepairRecord(
            month=repair_proto.month or "",
            repair_cost=repair_proto.repair_cost,
            equipment_id=repair_proto.equipment_id or "",
            reason=repair_proto.reason or "",
        )
        repairs.append(repair)

    return UnplannedRepair(
        repairs=repairs,
        total_repair_cost=proto.total_repair_cost,
    )


def domain_required_material_to_proto(
    domain: RequiredMaterial,
) -> RequiredMaterialProto:
    """Преобразует доменную сущность RequiredMaterial в proto сообщение."""
    proto = RequiredMaterialProto()
    proto.material_id = domain.material_id
    proto.name = domain.name
    proto.has_contracted_supplier = domain.has_contracted_supplier
    proto.required_quantity = domain.required_quantity
    proto.current_stock = domain.current_stock
    return proto


def proto_required_material_to_domain(proto: RequiredMaterialProto) -> RequiredMaterial:
    """Преобразует proto сообщение RequiredMaterial в доменную сущность."""
    return RequiredMaterial(
        material_id=proto.material_id or "",
        name=proto.name or "",
        has_contracted_supplier=proto.has_contracted_supplier,
        required_quantity=proto.required_quantity,
        current_stock=proto.current_stock,
    )


# Мапперы для метрик (доменные объекты)


def domain_factory_metrics_obj_to_proto(domain: FactoryMetrics) -> FactoryMetricsProto:
    """Преобразует доменный объект FactoryMetrics в proto сообщение."""

    def _to_int(value, default=0):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def _to_float(value, default=0.0):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    proto = FactoryMetricsProto()
    proto.profitability = _to_float(domain.profitability)
    proto.on_time_delivery_rate = _to_float(domain.on_time_delivery_rate)
    proto.oee = _to_float(domain.oee)
    proto.total_procurement_cost = _to_int(domain.total_procurement_cost)
    proto.defect_rate = _to_float(domain.defect_rate)

    # Преобразуем метрики складов
    for warehouse_type, warehouse_metrics in domain.warehouse_metrics.items():
        proto.warehouse_metrics[warehouse_type].CopyFrom(
            domain_warehouse_metrics_to_proto(warehouse_metrics)
        )

    return proto


def proto_factory_metrics_to_domain(proto: FactoryMetricsProto) -> FactoryMetrics:
    """Преобразует proto сообщение FactoryMetrics в доменную сущность."""
    warehouse_metrics = {}
    for warehouse_type, warehouse_proto in proto.warehouse_metrics.items():
        warehouse_metrics[warehouse_type] = proto_warehouse_metrics_to_domain(
            warehouse_proto
        )

    return FactoryMetrics(
        profitability=proto.profitability,
        on_time_delivery_rate=proto.on_time_delivery_rate,
        oee=proto.oee,
        warehouse_metrics=warehouse_metrics,
        total_procurement_cost=proto.total_procurement_cost,
        defect_rate=proto.defect_rate,
    )


def domain_warehouse_metrics_to_proto(
    domain: WarehouseMetrics,
) -> WarehouseMetricsProto:
    """Преобразует доменный объект WarehouseMetrics в proto сообщение."""

    def _to_int(value, default=0):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def _to_float(value, default=0.0):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    proto = WarehouseMetricsProto()
    proto.fill_level = _to_float(domain.fill_level)
    proto.current_load = _to_int(domain.current_load)
    proto.max_capacity = _to_int(domain.max_capacity)
    for material_name, level in domain.material_levels.items():
        proto.material_levels[material_name] = _to_int(level)
    # Преобразуем load_over_time (массив чисел)
    proto.load_over_time[:] = [_to_int(v) for v in domain.load_over_time]
    # Преобразуем max_capacity_over_time (массив чисел)
    proto.max_capacity_over_time[:] = [
        _to_int(v) for v in domain.max_capacity_over_time
    ]
    return proto


def proto_warehouse_metrics_to_domain(proto: WarehouseMetricsProto) -> WarehouseMetrics:
    """Преобразует proto сообщение WarehouseMetrics в доменную сущность."""
    return WarehouseMetrics(
        fill_level=proto.fill_level,
        current_load=proto.current_load,
        max_capacity=proto.max_capacity,
        material_levels=dict(proto.material_levels),
        load_over_time=list(proto.load_over_time),
        max_capacity_over_time=list(proto.max_capacity_over_time),
    )


def domain_production_metrics_obj_to_proto(
    domain: ProductionMetrics,
) -> ProductionMetricsProto:
    """Преобразует доменный объект ProductionMetrics в proto сообщение."""

    def _to_int(value, default=0):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def _to_float(value, default=0.0):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    proto = ProductionMetricsProto()
    proto.average_equipment_utilization = _to_float(
        domain.average_equipment_utilization
    )
    proto.wip_count = _to_int(domain.wip_count)
    proto.finished_goods_count = _to_int(domain.finished_goods_count)

    for monthly in domain.monthly_productivity:
        monthly_proto = proto.monthly_productivity.add()
        monthly_proto.month = monthly.month
        monthly_proto.units_produced = _to_int(monthly.units_produced)

    for material_name, quantity in domain.material_reserves.items():
        proto.material_reserves[material_name] = _to_int(quantity)

    return proto


def proto_production_metrics_to_domain(
    proto: ProductionMetricsProto,
) -> ProductionMetrics:
    """Преобразует proto сообщение ProductionMetrics в доменную сущность."""
    monthly_productivity = []
    for monthly_proto in proto.monthly_productivity:
        monthly_productivity.append(
            ProductionMetrics.MonthlyProductivity(
                month=monthly_proto.month,
                units_produced=monthly_proto.units_produced,
            )
        )

    return ProductionMetrics(
        monthly_productivity=monthly_productivity,
        average_equipment_utilization=proto.average_equipment_utilization,
        wip_count=proto.wip_count,
        finished_goods_count=proto.finished_goods_count,
        material_reserves=dict(proto.material_reserves),
    )


def domain_quality_metrics_obj_to_proto(domain: QualityMetrics) -> QualityMetricsProto:
    """Преобразует доменный объект QualityMetrics в proto сообщение."""

    def _to_int(value, default=0):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def _to_float(value, default=0.0):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    proto = QualityMetricsProto()
    proto.defect_percentage = _to_float(domain.defect_percentage)
    proto.good_output_percentage = _to_float(domain.good_output_percentage)
    proto.average_material_quality = _to_float(domain.average_material_quality)
    proto.average_supplier_failure_probability = _to_float(
        domain.average_supplier_failure_probability
    )
    proto.procurement_volume = _to_int(domain.procurement_volume)

    for cause in domain.defect_causes:
        cause_proto = proto.defect_causes.add()
        cause_proto.cause = cause.cause
        cause_proto.count = _to_int(cause.count)
        cause_proto.percentage = _to_float(cause.percentage)

    return proto


def proto_quality_metrics_to_domain(proto: QualityMetricsProto) -> QualityMetrics:
    """Преобразует proto сообщение QualityMetrics в доменную сущность."""
    defect_causes = []
    for cause_proto in proto.defect_causes:
        defect_causes.append(
            QualityMetrics.DefectCause(
                cause=cause_proto.cause,
                count=cause_proto.count,
                percentage=cause_proto.percentage,
            )
        )

    return QualityMetrics(
        defect_percentage=proto.defect_percentage,
        good_output_percentage=proto.good_output_percentage,
        defect_causes=defect_causes,
        average_material_quality=proto.average_material_quality,
        average_supplier_failure_probability=proto.average_supplier_failure_probability,
        procurement_volume=proto.procurement_volume,
    )


def domain_engineering_metrics_obj_to_proto(
    domain: EngineeringMetrics,
) -> EngineeringMetricsProto:
    """Преобразует доменный объект EngineeringMetrics в proto сообщение."""

    def _to_int(value, default=0):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def _to_float(value, default=0.0):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    proto = EngineeringMetricsProto()

    for timing in domain.operation_timings:
        timing_proto = proto.operation_timings.add()
        timing_proto.operation_name = timing.operation_name
        timing_proto.cycle_time = _to_int(timing.cycle_time)
        timing_proto.takt_time = _to_int(timing.takt_time)
        timing_proto.timing_cost = _to_int(timing.timing_cost)

    for downtime in domain.downtime_records:
        downtime_proto = proto.downtime_records.add()
        downtime_proto.cause = downtime.cause
        downtime_proto.total_minutes = _to_int(downtime.total_minutes)
        downtime_proto.average_per_shift = _to_float(downtime.average_per_shift)

    for defect in domain.defect_analysis:
        defect_proto = proto.defect_analysis.add()
        defect_proto.defect_type = defect.defect_type
        defect_proto.count = _to_int(defect.count)
        defect_proto.percentage = _to_float(defect.percentage)
        defect_proto.cumulative_percentage = _to_float(defect.cumulative_percentage)

    return proto


def proto_engineering_metrics_to_domain(
    proto: EngineeringMetricsProto,
) -> EngineeringMetrics:
    """Преобразует proto сообщение EngineeringMetrics в доменную сущность."""
    operation_timings = []
    for timing_proto in proto.operation_timings:
        operation_timings.append(
            EngineeringMetrics.OperationTiming(
                operation_name=timing_proto.operation_name,
                cycle_time=timing_proto.cycle_time,
                takt_time=timing_proto.takt_time,
                timing_cost=timing_proto.timing_cost,
            )
        )

    downtime_records = []
    for downtime_proto in proto.downtime_records:
        downtime_records.append(
            EngineeringMetrics.DowntimeRecord(
                cause=downtime_proto.cause,
                total_minutes=downtime_proto.total_minutes,
                average_per_shift=downtime_proto.average_per_shift,
            )
        )

    defect_analysis = []
    for defect_proto in proto.defect_analysis:
        defect_analysis.append(
            EngineeringMetrics.DefectAnalysis(
                defect_type=defect_proto.defect_type,
                count=defect_proto.count,
                percentage=defect_proto.percentage,
                cumulative_percentage=defect_proto.cumulative_percentage,
            )
        )

    return EngineeringMetrics(
        operation_timings=operation_timings,
        downtime_records=downtime_records,
        defect_analysis=defect_analysis,
    )


def domain_commercial_metrics_obj_to_proto(
    domain: CommercialMetrics,
) -> CommercialMetricsProto:
    """Преобразует доменный объект CommercialMetrics в proto сообщение."""

    def _to_int(value, default=0):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def _to_float(value, default=0.0):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    proto = CommercialMetricsProto()
    proto.tender_revenue_plan = _to_int(domain.tender_revenue_plan)
    proto.total_payments = _to_int(domain.total_payments)
    proto.total_receipts = _to_int(domain.total_receipts)
    proto.on_time_completed_orders = _to_int(domain.on_time_completed_orders)

    for revenue in domain.yearly_revenues:
        revenue_proto = proto.yearly_revenues.add()
        revenue_proto.year = _to_int(revenue.year)
        revenue_proto.revenue = _to_int(revenue.revenue)

    for strategy, value in domain.sales_forecast.items():
        proto.sales_forecast[strategy] = _to_float(value)

    for strategy, cost in domain.strategy_costs.items():
        proto.strategy_costs[strategy] = _to_int(cost)

    for point in domain.tender_graph:
        point_proto = proto.tender_graph.add()
        point_proto.strategy = point.strategy
        point_proto.unit_size = point.unit_size
        point_proto.is_mastered = point.is_mastered

    for profitability in domain.project_profitabilities:
        profitability_proto = proto.project_profitabilities.add()
        profitability_proto.project_name = profitability.project_name
        profitability_proto.profitability = _to_float(profitability.profitability)

    return proto


def proto_commercial_metrics_to_domain(
    proto: CommercialMetricsProto,
) -> CommercialMetrics:
    """Преобразует proto сообщение CommercialMetrics в доменную сущность."""
    yearly_revenues = []
    for revenue_proto in proto.yearly_revenues:
        yearly_revenues.append(
            CommercialMetrics.YearlyRevenue(
                year=revenue_proto.year,
                revenue=revenue_proto.revenue,
            )
        )

    tender_graph = []
    for point_proto in proto.tender_graph:
        tender_graph.append(
            CommercialMetrics.TenderGraphPoint(
                strategy=point_proto.strategy,
                unit_size=point_proto.unit_size,
                is_mastered=point_proto.is_mastered,
            )
        )

    project_profitabilities = []
    for profitability_proto in proto.project_profitabilities:
        project_profitabilities.append(
            CommercialMetrics.ProjectProfitability(
                project_name=profitability_proto.project_name,
                profitability=profitability_proto.profitability,
            )
        )

    return CommercialMetrics(
        yearly_revenues=yearly_revenues,
        tender_revenue_plan=proto.tender_revenue_plan,
        total_payments=proto.total_payments,
        total_receipts=proto.total_receipts,
        sales_forecast=dict(proto.sales_forecast),
        strategy_costs=dict(proto.strategy_costs),
        tender_graph=tender_graph,
        project_profitabilities=project_profitabilities,
        on_time_completed_orders=proto.on_time_completed_orders,
    )


def domain_procurement_metrics_obj_to_proto(
    domain: ProcurementMetrics,
) -> ProcurementMetricsProto:
    """Преобразует доменный объект ProcurementMetrics в proto сообщение."""

    def _to_int(value, default=0):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def _to_float(value, default=0.0):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    proto = ProcurementMetricsProto()
    proto.total_procurement_value = _to_int(domain.total_procurement_value)

    for performance in domain.supplier_performances:
        performance_proto = proto.supplier_performances.add()
        performance_proto.supplier_id = performance.supplier_id
        performance_proto.delivered_quantity = _to_int(performance.delivered_quantity)
        performance_proto.projected_defect_rate = _to_float(
            performance.projected_defect_rate
        )
        performance_proto.planned_reliability = _to_float(
            performance.planned_reliability
        )
        performance_proto.actual_reliability = _to_float(performance.actual_reliability)
        performance_proto.planned_cost = _to_int(performance.planned_cost)
        performance_proto.actual_cost = _to_int(performance.actual_cost)
        performance_proto.actual_defect_count = _to_int(performance.actual_defect_count)

    return proto


def proto_procurement_metrics_to_domain(
    proto: ProcurementMetricsProto,
) -> ProcurementMetrics:
    """Преобразует proto сообщение ProcurementMetrics в доменную сущность."""
    supplier_performances = []
    for performance_proto in proto.supplier_performances:
        supplier_performances.append(
            ProcurementMetrics.SupplierPerformance(
                supplier_id=performance_proto.supplier_id,
                delivered_quantity=performance_proto.delivered_quantity,
                projected_defect_rate=performance_proto.projected_defect_rate,
                planned_reliability=performance_proto.planned_reliability,
                actual_reliability=performance_proto.actual_reliability,
                planned_cost=performance_proto.planned_cost,
                actual_cost=performance_proto.actual_cost,
                actual_defect_count=performance_proto.actual_defect_count,
            )
        )

    return ProcurementMetrics(
        supplier_performances=supplier_performances,
        total_procurement_value=proto.total_procurement_value,
    )
