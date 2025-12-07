from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class WarehouseType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    WAREHOUSE_TYPE_UNSPECIFIED: _ClassVar[WarehouseType]
    WAREHOUSE_TYPE_MATERIALS: _ClassVar[WarehouseType]
    WAREHOUSE_TYPE_PRODUCTS: _ClassVar[WarehouseType]
WAREHOUSE_TYPE_UNSPECIFIED: WarehouseType
WAREHOUSE_TYPE_MATERIALS: WarehouseType
WAREHOUSE_TYPE_PRODUCTS: WarehouseType

class Supplier(_message.Message):
    __slots__ = ("supplier_id", "name", "product_name", "delivery_period", "special_delivery_period", "reliability", "product_quality", "cost", "special_delivery_cost")
    SUPPLIER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_NAME_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_PERIOD_FIELD_NUMBER: _ClassVar[int]
    SPECIAL_DELIVERY_PERIOD_FIELD_NUMBER: _ClassVar[int]
    RELIABILITY_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_QUALITY_FIELD_NUMBER: _ClassVar[int]
    COST_FIELD_NUMBER: _ClassVar[int]
    SPECIAL_DELIVERY_COST_FIELD_NUMBER: _ClassVar[int]
    supplier_id: str
    name: str
    product_name: str
    delivery_period: int
    special_delivery_period: int
    reliability: float
    product_quality: float
    cost: int
    special_delivery_cost: int
    def __init__(self, supplier_id: _Optional[str] = ..., name: _Optional[str] = ..., product_name: _Optional[str] = ..., delivery_period: _Optional[int] = ..., special_delivery_period: _Optional[int] = ..., reliability: _Optional[float] = ..., product_quality: _Optional[float] = ..., cost: _Optional[int] = ..., special_delivery_cost: _Optional[int] = ...) -> None: ...

class Warehouse(_message.Message):
    __slots__ = ("warehouse_id", "inventory_worker", "size", "loading", "materials")
    class MaterialsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    WAREHOUSE_ID_FIELD_NUMBER: _ClassVar[int]
    INVENTORY_WORKER_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    LOADING_FIELD_NUMBER: _ClassVar[int]
    MATERIALS_FIELD_NUMBER: _ClassVar[int]
    warehouse_id: str
    inventory_worker: Worker
    size: int
    loading: int
    materials: _containers.ScalarMap[str, int]
    def __init__(self, warehouse_id: _Optional[str] = ..., inventory_worker: _Optional[_Union[Worker, _Mapping]] = ..., size: _Optional[int] = ..., loading: _Optional[int] = ..., materials: _Optional[_Mapping[str, int]] = ...) -> None: ...

class Worker(_message.Message):
    __slots__ = ("worker_id", "name", "qualification", "specialty", "salary")
    WORKER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    QUALIFICATION_FIELD_NUMBER: _ClassVar[int]
    SPECIALTY_FIELD_NUMBER: _ClassVar[int]
    SALARY_FIELD_NUMBER: _ClassVar[int]
    worker_id: str
    name: str
    qualification: int
    specialty: str
    salary: int
    def __init__(self, worker_id: _Optional[str] = ..., name: _Optional[str] = ..., qualification: _Optional[int] = ..., specialty: _Optional[str] = ..., salary: _Optional[int] = ...) -> None: ...

class Logist(_message.Message):
    __slots__ = ("worker_id", "name", "qualification", "specialty", "salary", "speed", "vehicle_type")
    WORKER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    QUALIFICATION_FIELD_NUMBER: _ClassVar[int]
    SPECIALTY_FIELD_NUMBER: _ClassVar[int]
    SALARY_FIELD_NUMBER: _ClassVar[int]
    SPEED_FIELD_NUMBER: _ClassVar[int]
    VEHICLE_TYPE_FIELD_NUMBER: _ClassVar[int]
    worker_id: str
    name: str
    qualification: int
    specialty: str
    salary: int
    speed: int
    vehicle_type: str
    def __init__(self, worker_id: _Optional[str] = ..., name: _Optional[str] = ..., qualification: _Optional[int] = ..., specialty: _Optional[str] = ..., salary: _Optional[int] = ..., speed: _Optional[int] = ..., vehicle_type: _Optional[str] = ...) -> None: ...

class Equipment(_message.Message):
    __slots__ = ("equipment_id", "name", "reliability", "maintenance_period", "maintenance_cost", "cost", "repair_cost", "repair_time")
    EQUIPMENT_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    RELIABILITY_FIELD_NUMBER: _ClassVar[int]
    MAINTENANCE_PERIOD_FIELD_NUMBER: _ClassVar[int]
    MAINTENANCE_COST_FIELD_NUMBER: _ClassVar[int]
    COST_FIELD_NUMBER: _ClassVar[int]
    REPAIR_COST_FIELD_NUMBER: _ClassVar[int]
    REPAIR_TIME_FIELD_NUMBER: _ClassVar[int]
    equipment_id: str
    name: str
    reliability: float
    maintenance_period: int
    maintenance_cost: int
    cost: int
    repair_cost: int
    repair_time: int
    def __init__(self, equipment_id: _Optional[str] = ..., name: _Optional[str] = ..., reliability: _Optional[float] = ..., maintenance_period: _Optional[int] = ..., maintenance_cost: _Optional[int] = ..., cost: _Optional[int] = ..., repair_cost: _Optional[int] = ..., repair_time: _Optional[int] = ...) -> None: ...

class Workplace(_message.Message):
    __slots__ = ("workplace_id", "workplace_name", "required_speciality", "required_qualification", "worker", "equipment", "required_stages")
    WORKPLACE_ID_FIELD_NUMBER: _ClassVar[int]
    WORKPLACE_NAME_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_SPECIALITY_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_QUALIFICATION_FIELD_NUMBER: _ClassVar[int]
    WORKER_FIELD_NUMBER: _ClassVar[int]
    EQUIPMENT_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_STAGES_FIELD_NUMBER: _ClassVar[int]
    workplace_id: str
    workplace_name: str
    required_speciality: str
    required_qualification: int
    worker: Worker
    equipment: Equipment
    required_stages: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, workplace_id: _Optional[str] = ..., workplace_name: _Optional[str] = ..., required_speciality: _Optional[str] = ..., required_qualification: _Optional[int] = ..., worker: _Optional[_Union[Worker, _Mapping]] = ..., equipment: _Optional[_Union[Equipment, _Mapping]] = ..., required_stages: _Optional[_Iterable[str]] = ...) -> None: ...

class Route(_message.Message):
    __slots__ = ("length", "from_workplace", "to_workplace")
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    FROM_WORKPLACE_FIELD_NUMBER: _ClassVar[int]
    TO_WORKPLACE_FIELD_NUMBER: _ClassVar[int]
    length: int
    from_workplace: str
    to_workplace: str
    def __init__(self, length: _Optional[int] = ..., from_workplace: _Optional[str] = ..., to_workplace: _Optional[str] = ...) -> None: ...

class ProcessGraph(_message.Message):
    __slots__ = ("process_graph_id", "workplaces", "routes")
    PROCESS_GRAPH_ID_FIELD_NUMBER: _ClassVar[int]
    WORKPLACES_FIELD_NUMBER: _ClassVar[int]
    ROUTES_FIELD_NUMBER: _ClassVar[int]
    process_graph_id: str
    workplaces: _containers.RepeatedCompositeFieldContainer[Workplace]
    routes: _containers.RepeatedCompositeFieldContainer[Route]
    def __init__(self, process_graph_id: _Optional[str] = ..., workplaces: _Optional[_Iterable[_Union[Workplace, _Mapping]]] = ..., routes: _Optional[_Iterable[_Union[Route, _Mapping]]] = ...) -> None: ...

class Consumer(_message.Message):
    __slots__ = ("consumer_id", "name", "type")
    CONSUMER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    consumer_id: str
    name: str
    type: str
    def __init__(self, consumer_id: _Optional[str] = ..., name: _Optional[str] = ..., type: _Optional[str] = ...) -> None: ...

class Tender(_message.Message):
    __slots__ = ("tender_id", "consumer", "cost", "quantity_of_products")
    TENDER_ID_FIELD_NUMBER: _ClassVar[int]
    CONSUMER_FIELD_NUMBER: _ClassVar[int]
    COST_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_OF_PRODUCTS_FIELD_NUMBER: _ClassVar[int]
    tender_id: str
    consumer: Consumer
    cost: int
    quantity_of_products: int
    def __init__(self, tender_id: _Optional[str] = ..., consumer: _Optional[_Union[Consumer, _Mapping]] = ..., cost: _Optional[int] = ..., quantity_of_products: _Optional[int] = ...) -> None: ...

class SimulationParameters(_message.Message):
    __slots__ = ("logist", "suppliers", "backup_suppliers", "materials_warehouse", "product_warehouse", "processes", "tenders", "dealing_with_defects", "has_certification", "production_improvements", "sales_strategy")
    LOGIST_FIELD_NUMBER: _ClassVar[int]
    SUPPLIERS_FIELD_NUMBER: _ClassVar[int]
    BACKUP_SUPPLIERS_FIELD_NUMBER: _ClassVar[int]
    MATERIALS_WAREHOUSE_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_WAREHOUSE_FIELD_NUMBER: _ClassVar[int]
    PROCESSES_FIELD_NUMBER: _ClassVar[int]
    TENDERS_FIELD_NUMBER: _ClassVar[int]
    DEALING_WITH_DEFECTS_FIELD_NUMBER: _ClassVar[int]
    HAS_CERTIFICATION_FIELD_NUMBER: _ClassVar[int]
    PRODUCTION_IMPROVEMENTS_FIELD_NUMBER: _ClassVar[int]
    SALES_STRATEGY_FIELD_NUMBER: _ClassVar[int]
    logist: Logist
    suppliers: _containers.RepeatedCompositeFieldContainer[Supplier]
    backup_suppliers: _containers.RepeatedCompositeFieldContainer[Supplier]
    materials_warehouse: Warehouse
    product_warehouse: Warehouse
    processes: ProcessGraph
    tenders: _containers.RepeatedCompositeFieldContainer[Tender]
    dealing_with_defects: str
    has_certification: bool
    production_improvements: _containers.RepeatedScalarFieldContainer[str]
    sales_strategy: str
    def __init__(self, logist: _Optional[_Union[Logist, _Mapping]] = ..., suppliers: _Optional[_Iterable[_Union[Supplier, _Mapping]]] = ..., backup_suppliers: _Optional[_Iterable[_Union[Supplier, _Mapping]]] = ..., materials_warehouse: _Optional[_Union[Warehouse, _Mapping]] = ..., product_warehouse: _Optional[_Union[Warehouse, _Mapping]] = ..., processes: _Optional[_Union[ProcessGraph, _Mapping]] = ..., tenders: _Optional[_Iterable[_Union[Tender, _Mapping]]] = ..., dealing_with_defects: _Optional[str] = ..., has_certification: bool = ..., production_improvements: _Optional[_Iterable[str]] = ..., sales_strategy: _Optional[str] = ...) -> None: ...

class SimulationResults(_message.Message):
    __slots__ = ("profit", "cost", "profitability")
    PROFIT_FIELD_NUMBER: _ClassVar[int]
    COST_FIELD_NUMBER: _ClassVar[int]
    PROFITABILITY_FIELD_NUMBER: _ClassVar[int]
    profit: int
    cost: int
    profitability: float
    def __init__(self, profit: _Optional[int] = ..., cost: _Optional[int] = ..., profitability: _Optional[float] = ...) -> None: ...

class Simulation(_message.Message):
    __slots__ = ("capital", "step", "simulation_id", "parameters", "results")
    CAPITAL_FIELD_NUMBER: _ClassVar[int]
    STEP_FIELD_NUMBER: _ClassVar[int]
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    capital: int
    step: int
    simulation_id: str
    parameters: SimulationParameters
    results: SimulationResults
    def __init__(self, capital: _Optional[int] = ..., step: _Optional[int] = ..., simulation_id: _Optional[str] = ..., parameters: _Optional[_Union[SimulationParameters, _Mapping]] = ..., results: _Optional[_Union[SimulationResults, _Mapping]] = ...) -> None: ...

class SimulationResponse(_message.Message):
    __slots__ = ("simulation", "timestamp")
    SIMULATION_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    simulation: Simulation
    timestamp: str
    def __init__(self, simulation: _Optional[_Union[Simulation, _Mapping]] = ..., timestamp: _Optional[str] = ...) -> None: ...

class GetSimulationRequest(_message.Message):
    __slots__ = ("simulation_id",)
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    def __init__(self, simulation_id: _Optional[str] = ...) -> None: ...

class SetLogistRequest(_message.Message):
    __slots__ = ("simulation_id", "worker_id")
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    WORKER_ID_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    worker_id: str
    def __init__(self, simulation_id: _Optional[str] = ..., worker_id: _Optional[str] = ...) -> None: ...

class AddSupplierRequest(_message.Message):
    __slots__ = ("simulation_id", "supplier_id", "is_backup")
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    SUPPLIER_ID_FIELD_NUMBER: _ClassVar[int]
    IS_BACKUP_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    supplier_id: str
    is_backup: bool
    def __init__(self, simulation_id: _Optional[str] = ..., supplier_id: _Optional[str] = ..., is_backup: bool = ...) -> None: ...

class SetWarehouseInventoryWorkerRequest(_message.Message):
    __slots__ = ("simulation_id", "worker_id", "warehouse_type")
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    WORKER_ID_FIELD_NUMBER: _ClassVar[int]
    WAREHOUSE_TYPE_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    worker_id: str
    warehouse_type: WarehouseType
    def __init__(self, simulation_id: _Optional[str] = ..., worker_id: _Optional[str] = ..., warehouse_type: _Optional[_Union[WarehouseType, str]] = ...) -> None: ...

class IncreaseWarehouseSizeRequest(_message.Message):
    __slots__ = ("simulation_id", "warehouse_type", "size")
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    WAREHOUSE_TYPE_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    warehouse_type: WarehouseType
    size: int
    def __init__(self, simulation_id: _Optional[str] = ..., warehouse_type: _Optional[_Union[WarehouseType, str]] = ..., size: _Optional[int] = ...) -> None: ...

class AddTenderRequest(_message.Message):
    __slots__ = ("simulation_id", "tender_id")
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    TENDER_ID_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    tender_id: str
    def __init__(self, simulation_id: _Optional[str] = ..., tender_id: _Optional[str] = ...) -> None: ...

class RemoveTenderRequest(_message.Message):
    __slots__ = ("simulation_id", "tender_id")
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    TENDER_ID_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    tender_id: str
    def __init__(self, simulation_id: _Optional[str] = ..., tender_id: _Optional[str] = ...) -> None: ...

class SetDealingWithDefectsRequest(_message.Message):
    __slots__ = ("simulation_id", "dealing_with_defects")
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    DEALING_WITH_DEFECTS_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    dealing_with_defects: str
    def __init__(self, simulation_id: _Optional[str] = ..., dealing_with_defects: _Optional[str] = ...) -> None: ...

class SetHasCertificationRequest(_message.Message):
    __slots__ = ("simulation_id", "has_certification")
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    HAS_CERTIFICATION_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    has_certification: bool
    def __init__(self, simulation_id: _Optional[str] = ..., has_certification: bool = ...) -> None: ...

class DeleteSupplierRequest(_message.Message):
    __slots__ = ("simulation_id", "supplier_id")
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    SUPPLIER_ID_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    supplier_id: str
    def __init__(self, simulation_id: _Optional[str] = ..., supplier_id: _Optional[str] = ...) -> None: ...

class AddProductionImprovementRequest(_message.Message):
    __slots__ = ("simulation_id", "production_improvement")
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCTION_IMPROVEMENT_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    production_improvement: str
    def __init__(self, simulation_id: _Optional[str] = ..., production_improvement: _Optional[str] = ...) -> None: ...

class DeleteProductionImprovementRequest(_message.Message):
    __slots__ = ("simulation_id", "production_improvement")
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCTION_IMPROVEMENT_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    production_improvement: str
    def __init__(self, simulation_id: _Optional[str] = ..., production_improvement: _Optional[str] = ...) -> None: ...

class SetSalesStrategyRequest(_message.Message):
    __slots__ = ("simulation_id", "sales_strategy")
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    SALES_STRATEGY_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    sales_strategy: str
    def __init__(self, simulation_id: _Optional[str] = ..., sales_strategy: _Optional[str] = ...) -> None: ...

class RunSimulationRequest(_message.Message):
    __slots__ = ("simulation_id",)
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    def __init__(self, simulation_id: _Optional[str] = ...) -> None: ...

class AddProcessRouteRequest(_message.Message):
    __slots__ = ("simulation_id", "length", "from_workplace", "to_workplace")
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    FROM_WORKPLACE_FIELD_NUMBER: _ClassVar[int]
    TO_WORKPLACE_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    length: int
    from_workplace: str
    to_workplace: str
    def __init__(self, simulation_id: _Optional[str] = ..., length: _Optional[int] = ..., from_workplace: _Optional[str] = ..., to_workplace: _Optional[str] = ...) -> None: ...

class DeleteProcesRouteRequest(_message.Message):
    __slots__ = ("simulation_id", "from_workplace", "to_workplace")
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    FROM_WORKPLACE_FIELD_NUMBER: _ClassVar[int]
    TO_WORKPLACE_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    from_workplace: str
    to_workplace: str
    def __init__(self, simulation_id: _Optional[str] = ..., from_workplace: _Optional[str] = ..., to_workplace: _Optional[str] = ...) -> None: ...

class SetWorkerOnWorkerplaceRequest(_message.Message):
    __slots__ = ("simulation_id", "worker_id", "workplace_id")
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    WORKER_ID_FIELD_NUMBER: _ClassVar[int]
    WORKPLACE_ID_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    worker_id: str
    workplace_id: str
    def __init__(self, simulation_id: _Optional[str] = ..., worker_id: _Optional[str] = ..., workplace_id: _Optional[str] = ...) -> None: ...

class UnSetWorkerOnWorkerplaceRequest(_message.Message):
    __slots__ = ("simulation_id", "worker_id")
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    WORKER_ID_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    worker_id: str
    def __init__(self, simulation_id: _Optional[str] = ..., worker_id: _Optional[str] = ...) -> None: ...

class CreateSimulationRquest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SetEquipmentOnWorkplaceRequst(_message.Message):
    __slots__ = ("simulation_id", "workplace_id", "equipment_id")
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    WORKPLACE_ID_FIELD_NUMBER: _ClassVar[int]
    EQUIPMENT_ID_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    workplace_id: str
    equipment_id: str
    def __init__(self, simulation_id: _Optional[str] = ..., workplace_id: _Optional[str] = ..., equipment_id: _Optional[str] = ...) -> None: ...

class UnSetEquipmentOnWorkplaceRequst(_message.Message):
    __slots__ = ("simulation_id", "workplace_id")
    SIMULATION_ID_FIELD_NUMBER: _ClassVar[int]
    WORKPLACE_ID_FIELD_NUMBER: _ClassVar[int]
    simulation_id: str
    workplace_id: str
    def __init__(self, simulation_id: _Optional[str] = ..., workplace_id: _Optional[str] = ...) -> None: ...

class SuccessResponse(_message.Message):
    __slots__ = ("success", "message", "timestamp")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    timestamp: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ..., timestamp: _Optional[str] = ...) -> None: ...

class CreateSupplierRequest(_message.Message):
    __slots__ = ("name", "product_name", "delivery_period", "special_delivery_period", "reliability", "product_quality", "cost", "special_delivery_cost")
    NAME_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_NAME_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_PERIOD_FIELD_NUMBER: _ClassVar[int]
    SPECIAL_DELIVERY_PERIOD_FIELD_NUMBER: _ClassVar[int]
    RELIABILITY_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_QUALITY_FIELD_NUMBER: _ClassVar[int]
    COST_FIELD_NUMBER: _ClassVar[int]
    SPECIAL_DELIVERY_COST_FIELD_NUMBER: _ClassVar[int]
    name: str
    product_name: str
    delivery_period: int
    special_delivery_period: int
    reliability: float
    product_quality: float
    cost: int
    special_delivery_cost: int
    def __init__(self, name: _Optional[str] = ..., product_name: _Optional[str] = ..., delivery_period: _Optional[int] = ..., special_delivery_period: _Optional[int] = ..., reliability: _Optional[float] = ..., product_quality: _Optional[float] = ..., cost: _Optional[int] = ..., special_delivery_cost: _Optional[int] = ...) -> None: ...

class UpdateSupplierRequest(_message.Message):
    __slots__ = ("supplier_id", "name", "product_name", "delivery_period", "special_delivery_period", "reliability", "product_quality", "cost", "special_delivery_cost")
    SUPPLIER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_NAME_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_PERIOD_FIELD_NUMBER: _ClassVar[int]
    SPECIAL_DELIVERY_PERIOD_FIELD_NUMBER: _ClassVar[int]
    RELIABILITY_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_QUALITY_FIELD_NUMBER: _ClassVar[int]
    COST_FIELD_NUMBER: _ClassVar[int]
    SPECIAL_DELIVERY_COST_FIELD_NUMBER: _ClassVar[int]
    supplier_id: str
    name: str
    product_name: str
    delivery_period: int
    special_delivery_period: int
    reliability: float
    product_quality: float
    cost: int
    special_delivery_cost: int
    def __init__(self, supplier_id: _Optional[str] = ..., name: _Optional[str] = ..., product_name: _Optional[str] = ..., delivery_period: _Optional[int] = ..., special_delivery_period: _Optional[int] = ..., reliability: _Optional[float] = ..., product_quality: _Optional[float] = ..., cost: _Optional[int] = ..., special_delivery_cost: _Optional[int] = ...) -> None: ...

class GetAllSuppliersResponse(_message.Message):
    __slots__ = ("suppliers", "total_count")
    SUPPLIERS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    suppliers: _containers.RepeatedCompositeFieldContainer[Supplier]
    total_count: int
    def __init__(self, suppliers: _Optional[_Iterable[_Union[Supplier, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class GetWarehouseRequest(_message.Message):
    __slots__ = ("warehouse_id",)
    WAREHOUSE_ID_FIELD_NUMBER: _ClassVar[int]
    warehouse_id: str
    def __init__(self, warehouse_id: _Optional[str] = ...) -> None: ...

class CreateWorkerRequest(_message.Message):
    __slots__ = ("name", "qualification", "specialty", "salary")
    NAME_FIELD_NUMBER: _ClassVar[int]
    QUALIFICATION_FIELD_NUMBER: _ClassVar[int]
    SPECIALTY_FIELD_NUMBER: _ClassVar[int]
    SALARY_FIELD_NUMBER: _ClassVar[int]
    name: str
    qualification: int
    specialty: str
    salary: int
    def __init__(self, name: _Optional[str] = ..., qualification: _Optional[int] = ..., specialty: _Optional[str] = ..., salary: _Optional[int] = ...) -> None: ...

class UpdateWorkerRequest(_message.Message):
    __slots__ = ("worker_id", "name", "qualification", "specialty", "salary")
    WORKER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    QUALIFICATION_FIELD_NUMBER: _ClassVar[int]
    SPECIALTY_FIELD_NUMBER: _ClassVar[int]
    SALARY_FIELD_NUMBER: _ClassVar[int]
    worker_id: str
    name: str
    qualification: int
    specialty: str
    salary: int
    def __init__(self, worker_id: _Optional[str] = ..., name: _Optional[str] = ..., qualification: _Optional[int] = ..., specialty: _Optional[str] = ..., salary: _Optional[int] = ...) -> None: ...

class DeleteWorkerRequest(_message.Message):
    __slots__ = ("worker_id",)
    WORKER_ID_FIELD_NUMBER: _ClassVar[int]
    worker_id: str
    def __init__(self, worker_id: _Optional[str] = ...) -> None: ...

class GetAllWorkersResponse(_message.Message):
    __slots__ = ("workers", "total_count")
    WORKERS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    workers: _containers.RepeatedCompositeFieldContainer[Worker]
    total_count: int
    def __init__(self, workers: _Optional[_Iterable[_Union[Worker, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class CreateLogistRequest(_message.Message):
    __slots__ = ("name", "qualification", "specialty", "salary", "speed", "vehicle_type")
    NAME_FIELD_NUMBER: _ClassVar[int]
    QUALIFICATION_FIELD_NUMBER: _ClassVar[int]
    SPECIALTY_FIELD_NUMBER: _ClassVar[int]
    SALARY_FIELD_NUMBER: _ClassVar[int]
    SPEED_FIELD_NUMBER: _ClassVar[int]
    VEHICLE_TYPE_FIELD_NUMBER: _ClassVar[int]
    name: str
    qualification: int
    specialty: str
    salary: int
    speed: int
    vehicle_type: str
    def __init__(self, name: _Optional[str] = ..., qualification: _Optional[int] = ..., specialty: _Optional[str] = ..., salary: _Optional[int] = ..., speed: _Optional[int] = ..., vehicle_type: _Optional[str] = ...) -> None: ...

class UpdateLogistRequest(_message.Message):
    __slots__ = ("worker_id", "name", "qualification", "specialty", "salary", "speed", "vehicle_type")
    WORKER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    QUALIFICATION_FIELD_NUMBER: _ClassVar[int]
    SPECIALTY_FIELD_NUMBER: _ClassVar[int]
    SALARY_FIELD_NUMBER: _ClassVar[int]
    SPEED_FIELD_NUMBER: _ClassVar[int]
    VEHICLE_TYPE_FIELD_NUMBER: _ClassVar[int]
    worker_id: str
    name: str
    qualification: int
    specialty: str
    salary: int
    speed: int
    vehicle_type: str
    def __init__(self, worker_id: _Optional[str] = ..., name: _Optional[str] = ..., qualification: _Optional[int] = ..., specialty: _Optional[str] = ..., salary: _Optional[int] = ..., speed: _Optional[int] = ..., vehicle_type: _Optional[str] = ...) -> None: ...

class DeleteLogistRequest(_message.Message):
    __slots__ = ("worker_id",)
    WORKER_ID_FIELD_NUMBER: _ClassVar[int]
    worker_id: str
    def __init__(self, worker_id: _Optional[str] = ...) -> None: ...

class GetAllLogistsResponse(_message.Message):
    __slots__ = ("logists", "total_count")
    LOGISTS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    logists: _containers.RepeatedCompositeFieldContainer[Logist]
    total_count: int
    def __init__(self, logists: _Optional[_Iterable[_Union[Logist, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class CreateWorkplaceRequest(_message.Message):
    __slots__ = ("workplace_name", "required_speciality", "required_qualification", "worker_id", "required_stages")
    WORKPLACE_NAME_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_SPECIALITY_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_QUALIFICATION_FIELD_NUMBER: _ClassVar[int]
    WORKER_ID_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_STAGES_FIELD_NUMBER: _ClassVar[int]
    workplace_name: str
    required_speciality: str
    required_qualification: str
    worker_id: str
    required_stages: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, workplace_name: _Optional[str] = ..., required_speciality: _Optional[str] = ..., required_qualification: _Optional[str] = ..., worker_id: _Optional[str] = ..., required_stages: _Optional[_Iterable[str]] = ...) -> None: ...

class UpdateWorkplaceRequest(_message.Message):
    __slots__ = ("workplace_id", "workplace_name", "required_speciality", "required_qualification", "worker_id", "required_stages")
    WORKPLACE_ID_FIELD_NUMBER: _ClassVar[int]
    WORKPLACE_NAME_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_SPECIALITY_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_QUALIFICATION_FIELD_NUMBER: _ClassVar[int]
    WORKER_ID_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_STAGES_FIELD_NUMBER: _ClassVar[int]
    workplace_id: str
    workplace_name: str
    required_speciality: str
    required_qualification: str
    worker_id: str
    required_stages: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, workplace_id: _Optional[str] = ..., workplace_name: _Optional[str] = ..., required_speciality: _Optional[str] = ..., required_qualification: _Optional[str] = ..., worker_id: _Optional[str] = ..., required_stages: _Optional[_Iterable[str]] = ...) -> None: ...

class DeleteWorkplaceRequest(_message.Message):
    __slots__ = ("workplace_id",)
    WORKPLACE_ID_FIELD_NUMBER: _ClassVar[int]
    workplace_id: str
    def __init__(self, workplace_id: _Optional[str] = ...) -> None: ...

class GetAllWorkplacesResponse(_message.Message):
    __slots__ = ("workplaces", "total_count")
    WORKPLACES_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    workplaces: _containers.RepeatedCompositeFieldContainer[Workplace]
    total_count: int
    def __init__(self, workplaces: _Optional[_Iterable[_Union[Workplace, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class GetProcessGraphRequest(_message.Message):
    __slots__ = ("process_graph_id",)
    PROCESS_GRAPH_ID_FIELD_NUMBER: _ClassVar[int]
    process_graph_id: str
    def __init__(self, process_graph_id: _Optional[str] = ...) -> None: ...

class CreateConsumerRequest(_message.Message):
    __slots__ = ("name", "type")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: str
    def __init__(self, name: _Optional[str] = ..., type: _Optional[str] = ...) -> None: ...

class UpdateConsumerRequest(_message.Message):
    __slots__ = ("consumer_id", "name", "type")
    CONSUMER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    consumer_id: str
    name: str
    type: str
    def __init__(self, consumer_id: _Optional[str] = ..., name: _Optional[str] = ..., type: _Optional[str] = ...) -> None: ...

class DeleteConsumerRequest(_message.Message):
    __slots__ = ("consumer_id",)
    CONSUMER_ID_FIELD_NUMBER: _ClassVar[int]
    consumer_id: str
    def __init__(self, consumer_id: _Optional[str] = ...) -> None: ...

class GetAllConsumersResponse(_message.Message):
    __slots__ = ("consumers", "total_count")
    CONSUMERS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    consumers: _containers.RepeatedCompositeFieldContainer[Consumer]
    total_count: int
    def __init__(self, consumers: _Optional[_Iterable[_Union[Consumer, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class CreateTenderRequest(_message.Message):
    __slots__ = ("consumer_id", "cost", "quantity_of_products")
    CONSUMER_ID_FIELD_NUMBER: _ClassVar[int]
    COST_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_OF_PRODUCTS_FIELD_NUMBER: _ClassVar[int]
    consumer_id: str
    cost: int
    quantity_of_products: int
    def __init__(self, consumer_id: _Optional[str] = ..., cost: _Optional[int] = ..., quantity_of_products: _Optional[int] = ...) -> None: ...

class UpdateTenderRequest(_message.Message):
    __slots__ = ("tender_id", "consumer_id", "cost", "quantity_of_products")
    TENDER_ID_FIELD_NUMBER: _ClassVar[int]
    CONSUMER_ID_FIELD_NUMBER: _ClassVar[int]
    COST_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_OF_PRODUCTS_FIELD_NUMBER: _ClassVar[int]
    tender_id: str
    consumer_id: str
    cost: int
    quantity_of_products: int
    def __init__(self, tender_id: _Optional[str] = ..., consumer_id: _Optional[str] = ..., cost: _Optional[int] = ..., quantity_of_products: _Optional[int] = ...) -> None: ...

class DeleteTenderRequest(_message.Message):
    __slots__ = ("tender_id",)
    TENDER_ID_FIELD_NUMBER: _ClassVar[int]
    tender_id: str
    def __init__(self, tender_id: _Optional[str] = ...) -> None: ...

class GetAllTendersResponse(_message.Message):
    __slots__ = ("tenders", "total_count")
    TENDERS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    tenders: _containers.RepeatedCompositeFieldContainer[Tender]
    total_count: int
    def __init__(self, tenders: _Optional[_Iterable[_Union[Tender, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class GetAllSuppliersRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetAllWorkersRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetAllLogistsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetAllWorkplacesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetAllConsumersRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetAllTendersRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PingRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CreateEquipmentRequest(_message.Message):
    __slots__ = ("name", "reliability", "maintenance_period", "maintenance_cost", "cost", "repair_cost", "repair_time")
    NAME_FIELD_NUMBER: _ClassVar[int]
    RELIABILITY_FIELD_NUMBER: _ClassVar[int]
    MAINTENANCE_PERIOD_FIELD_NUMBER: _ClassVar[int]
    MAINTENANCE_COST_FIELD_NUMBER: _ClassVar[int]
    COST_FIELD_NUMBER: _ClassVar[int]
    REPAIR_COST_FIELD_NUMBER: _ClassVar[int]
    REPAIR_TIME_FIELD_NUMBER: _ClassVar[int]
    name: str
    reliability: float
    maintenance_period: int
    maintenance_cost: int
    cost: int
    repair_cost: int
    repair_time: int
    def __init__(self, name: _Optional[str] = ..., reliability: _Optional[float] = ..., maintenance_period: _Optional[int] = ..., maintenance_cost: _Optional[int] = ..., cost: _Optional[int] = ..., repair_cost: _Optional[int] = ..., repair_time: _Optional[int] = ...) -> None: ...

class UpdateEquipmentRequest(_message.Message):
    __slots__ = ("equipment_id", "name", "reliability", "maintenance_period", "maintenance_cost", "cost", "repair_cost", "repair_time")
    EQUIPMENT_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    RELIABILITY_FIELD_NUMBER: _ClassVar[int]
    MAINTENANCE_PERIOD_FIELD_NUMBER: _ClassVar[int]
    MAINTENANCE_COST_FIELD_NUMBER: _ClassVar[int]
    COST_FIELD_NUMBER: _ClassVar[int]
    REPAIR_COST_FIELD_NUMBER: _ClassVar[int]
    REPAIR_TIME_FIELD_NUMBER: _ClassVar[int]
    equipment_id: str
    name: str
    reliability: float
    maintenance_period: int
    maintenance_cost: int
    cost: int
    repair_cost: int
    repair_time: int
    def __init__(self, equipment_id: _Optional[str] = ..., name: _Optional[str] = ..., reliability: _Optional[float] = ..., maintenance_period: _Optional[int] = ..., maintenance_cost: _Optional[int] = ..., cost: _Optional[int] = ..., repair_cost: _Optional[int] = ..., repair_time: _Optional[int] = ...) -> None: ...

class DeleteEquipmentRequest(_message.Message):
    __slots__ = ("equipment_id",)
    EQUIPMENT_ID_FIELD_NUMBER: _ClassVar[int]
    equipment_id: str
    def __init__(self, equipment_id: _Optional[str] = ...) -> None: ...

class GetAllEquipmentRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetAllEquipmentResopnse(_message.Message):
    __slots__ = ("equipments", "total_count")
    EQUIPMENTS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    equipments: _containers.RepeatedCompositeFieldContainer[Equipment]
    total_count: int
    def __init__(self, equipments: _Optional[_Iterable[_Union[Equipment, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...
