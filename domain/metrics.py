"""Доменные сущности для метрик симуляции."""

from typing import List, Dict, Optional
from dataclasses import dataclass, field

from .base_serializabel import RedisSerializable


@dataclass
class WarehouseMetrics(RedisSerializable):
    """Метрики склада."""

    fill_level: float = 0.0
    current_load: int = 0
    max_capacity: int = 0
    material_levels: Dict[str, int] = field(default_factory=dict)
    load_over_time: List[int] = field(
        default_factory=list
    )  # Массив загруженности от времени
    max_capacity_over_time: List[int] = field(
        default_factory=list
    )  # Массив максимальной вместимости от времени


@dataclass
class FactoryMetrics(RedisSerializable):
    """Метрики завода."""

    profitability: float = 0.0
    on_time_delivery_rate: float = 0.0
    oee: float = 0.0  # Overall Equipment Effectiveness
    warehouse_metrics: Dict[str, WarehouseMetrics] = field(default_factory=dict)
    total_procurement_cost: int = 0
    defect_rate: float = 0.0


@dataclass
class ProductionMetrics(RedisSerializable):
    """Метрики производства."""

    @dataclass
    class MonthlyProductivity(RedisSerializable):
        """Месячная производительность."""

        month: str = ""
        units_produced: int = 0

    monthly_productivity: List[MonthlyProductivity] = field(default_factory=list)
    average_equipment_utilization: float = 0.0
    wip_count: int = 0  # Work In Progress
    finished_goods_count: int = 0
    material_reserves: Dict[str, int] = field(default_factory=dict)


@dataclass
class QualityMetrics(RedisSerializable):
    """Метрики качества."""

    @dataclass
    class DefectCause(RedisSerializable):
        """Причина дефекта."""

        cause: str = ""
        count: int = 0
        percentage: float = 0.0

    defect_percentage: float = 0.0
    good_output_percentage: float = 0.0
    defect_causes: List[DefectCause] = field(default_factory=list)
    average_material_quality: float = 0.0
    average_supplier_failure_probability: float = 0.0
    procurement_volume: int = 0


@dataclass
class EngineeringMetrics(RedisSerializable):
    """Инженерные метрики."""

    @dataclass
    class OperationTiming(RedisSerializable):
        """Время операции."""

        operation_name: str = ""
        cycle_time: int = 0
        takt_time: int = 0
        timing_cost: int = 0

    @dataclass
    class DowntimeRecord(RedisSerializable):
        """Запись простоя."""

        cause: str = ""
        total_minutes: int = 0
        average_per_shift: float = 0.0

    @dataclass
    class DefectAnalysis(RedisSerializable):
        """Анализ дефектов."""

        defect_type: str = ""
        count: int = 0
        percentage: float = 0.0
        cumulative_percentage: float = 0.0

    operation_timings: List[OperationTiming] = field(default_factory=list)
    downtime_records: List[DowntimeRecord] = field(default_factory=list)
    defect_analysis: List[DefectAnalysis] = field(default_factory=list)


@dataclass
class CommercialMetrics(RedisSerializable):
    """Коммерческие метрики."""

    @dataclass
    class YearlyRevenue(RedisSerializable):
        """Годовая выручка."""

        year: int = 0
        revenue: int = 0

    @dataclass
    class TenderGraphPoint(RedisSerializable):
        """Точка графика тендера."""

        strategy: str = ""
        unit_size: str = ""
        is_mastered: bool = False

    @dataclass
    class ProjectProfitability(RedisSerializable):
        """Прибыльность проекта."""

        project_name: str = ""
        profitability: float = 0.0

    yearly_revenues: List[YearlyRevenue] = field(default_factory=list)
    tender_revenue_plan: int = 0
    total_payments: int = 0
    total_receipts: int = 0
    sales_forecast: Dict[str, float] = field(default_factory=dict)
    strategy_costs: Dict[str, int] = field(default_factory=dict)
    tender_graph: List[TenderGraphPoint] = field(default_factory=list)
    project_profitabilities: List[ProjectProfitability] = field(default_factory=list)
    on_time_completed_orders: int = 0


@dataclass
class ProcurementMetrics(RedisSerializable):
    """Метрики закупок."""

    @dataclass
    class SupplierPerformance(RedisSerializable):
        """Производительность поставщика."""

        supplier_id: str = ""
        delivered_quantity: int = 0
        projected_defect_rate: float = 0.0
        planned_reliability: float = 0.0
        actual_reliability: float = 0.0
        planned_cost: int = 0
        actual_cost: int = 0
        actual_defect_count: int = 0

    supplier_performances: List[SupplierPerformance] = field(default_factory=list)
    total_procurement_value: int = 0
