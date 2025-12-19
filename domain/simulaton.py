from enum import Enum
from typing import List, Optional, Union, Dict, TYPE_CHECKING
from uuid import UUID, uuid4
from dataclasses import dataclass, field, replace
import random

from _pytest.stash import D

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from .supplier import Supplier
from .tender import Tender
from .warehouse import Warehouse
from .logist import Logist
from .worker import Worker
from .production_plan import (
    ProductionSchedule,
    ProductionPlanRow,
)
from .process_graph import ProcessGraph
from .distribution import DistributionStrategy
from .reporting import UnplannedRepair, RequiredMaterial
from .certification import Certification
from .lean_improvement import LeanImprovement
from .metrics import (
    FactoryMetrics,
    WarehouseMetrics,
    ProductionMetrics,
    QualityMetrics,
    EngineeringMetrics,
    CommercialMetrics,
    ProcurementMetrics,
)

from .base_serializabel import RedisSerializable

if TYPE_CHECKING:
    Simulation = "Simulation"


MAX_SIMULATION_STEPS = 3
DAYS_IN_YEAR = 365


def _safe_int(value, default: int = 0) -> int:
    """Безопасное преобразование к int с запасным значением."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


class SaleStrategest(str, Enum):
    NONE = "none"
    LOW_PRICES = "Низкие цены"
    DIFFERENTIATION = "Дифференциация"
    PREMIUM = "Премиум"
    FOCUS = "Фокусировка"


class DealingWithDefects(str, Enum):
    NONE = "none"
    DISPOSE = "Утилизировать"
    REWORK = "Переделать"
    SELL_AS_IS = "Продать как есть"
    RETURN_TO_SUPPLIER = "Вернуть поставщику"


class ProductImpruvement(str, Enum):
    NONE = "none"
    SYSTEM_5S = "5S система"
    KANBAN = "Канбан"
    TPM = "Всеобщее обслуживание оборудования"
    SUGGESTION_SYSTEM = "Система подачи предложений"


@dataclass
class SimulationParameters(RedisSerializable):
    # Константный список требуемых материалов
    REQUIRED_MATERIALS: List[RequiredMaterial] = field(
        default_factory=list, init=False, repr=False, compare=False
    )

    logist: Optional[Logist] = field(default=None)
    suppliers: List[Supplier] = field(default_factory=list)
    backup_suppliers: List[Supplier] = field(default_factory=list)
    materials_warehouse: Warehouse = field(
        default_factory=lambda: Warehouse(size=1000, materials={})
    )
    product_warehouse: Warehouse = field(
        default_factory=lambda: Warehouse(size=1000, materials={})
    )
    processes: ProcessGraph = field(default_factory=lambda: ProcessGraph())
    tenders: List[Tender] = field(default_factory=list)
    dealing_with_defects: DealingWithDefects = field(default=DealingWithDefects.NONE)
    production_improvements: List[LeanImprovement] = field(default_factory=list)
    sales_strategy: SaleStrategest = field(default=SaleStrategest.NONE)

    # Новые поля из proto
    production_schedule: ProductionSchedule = field(
        default_factory=lambda: ProductionSchedule()
    )
    certifications: List[Certification] = field(default_factory=list)
    lean_improvements: List[LeanImprovement] = field(default_factory=list)
    distribution_strategy: DistributionStrategy = field(
        default=DistributionStrategy.DISTRIBUTION_STRATEGY_UNSPECIFIED
    )
    step: int = field(default=0)

    capital: int = field(default=10000000)

    @staticmethod
    def from_simulation_parameters(
        simulationparameters: "SimulationParameters",
    ) -> "SimulationParameters":
        """Создает копию SimulationParameters из другого SimulationParameters."""
        return replace(simulationparameters)

    def set_sales_strategy(self, stragegy: SaleStrategest) -> None:
        if not isinstance(stragegy, SaleStrategest):
            raise ValueError(
                "Стратегия продаж должна быть объектом класса SaleStrategest"
            )

        self.sales_strategy = stragegy

    def add_product_inprovement(self, improvement_name: str) -> None:
        """Переключает флаг is_implemented для улучшения производства по названию.

        Args:
            improvement_name: название улучшения (improvement_id или name)

        Raises:
            ValueError: если улучшение не найдено в списке
        """
        # Ищем улучшение по improvement_id или name
        improvement = None
        for imp in self.production_improvements:
            if imp.improvement_id == improvement_name or imp.name == improvement_name:
                improvement = imp
                break

        if improvement is None:
            raise ValueError(f"Улучшение '{improvement_name}' не найдено в списке")

        improvement.set_is_implemented(True)

    def remove_product_improvement(self, improvement_name: str) -> None:
        """Переключает флаг is_implemented для улучшения производства по названию.

        Args:
            improvement_name: название улучшения (improvement_id или name)

        Raises:
            ValueError: если улучшение не найдено в списке
        """
        # Ищем улучшение по improvement_id или name
        improvement = None
        for imp in self.production_improvements:
            if imp.improvement_id == improvement_name or imp.name == improvement_name:
                improvement = imp
                break

        if improvement is None:
            raise ValueError(f"Улучшение '{improvement_name}' не найдено в списке")

        improvement.set_is_implemented(False)

    def add_tender(self, tender: Tender) -> None:
        """Добавляет тендер и создает соответствующую строку в производственном плане.

        Args:
            tender: Тендер для добавления

        Raises:
            ValueError: если тендер с таким tender_id уже существует
        """
        # Проверяем на дубликаты, используя стандартный оператор сравнения
        if tender in self.tenders:
            raise ValueError(
                f"Тендер с ID '{tender.tender_id}' уже существует в списке"
            )

        # Добавляем тендер в список
        self.tenders.append(tender)

        # Создаем строку в производственном плане
        row = ProductionPlanRow(
            tender_id=tender.tender_id,
            product_name="",  # Можно оставить пустым или получить из тендера, если есть
            planned_quantity=tender.quantity_of_products,
            actual_quantity=0,
            remaining_to_produce=tender.quantity_of_products,
        )
        self.production_schedule.set_row(row)

    def remove_tender(self, tender_id: str) -> None:
        """Удаляет тендер и соответствующую строку из производственного плана.

        Args:
            tender_id: ID тендера для удаления
        """
        # Удаляем тендер из списка по tender_id
        # Создаем временный тендер для сравнения
        temp_tender = Tender(tender_id=tender_id)
        self.tenders = [t for t in self.tenders if t != temp_tender]

        # Удаляем строку из производственного плана, используя стандартный оператор сравнения
        temp_row = ProductionPlanRow(tender_id=tender_id)
        self.production_schedule.rows = [
            row for row in self.production_schedule.rows if row != temp_row
        ]

    def set_logist(self, logist: Logist) -> None:
        if not isinstance(logist, Logist):
            raise ValueError("Логист должен быть объектом класса Logist")
        self.logist = logist

    def set_has_certification(self, certificate_type: str, is_obtained: bool) -> None:
        """Устанавливает флаг is_obtained для сертификации по типу.

        Args:
            certificate_type: тип сертификации (certificate_type)
            is_obtained: True если сертификация получена, False если нет

        Raises:
            ValueError: если сертификация с таким типом не найдена в списке
        """
        if not isinstance(is_obtained, bool):
            raise ValueError("is_obtained должен быть булевым значением")

        # Ищем сертификацию по certificate_type
        certification = None
        for cert in self.certifications:
            if cert.certificate_type == certificate_type:
                certification = cert
                break

        if certification is None:
            raise ValueError(
                f"Сертификация с типом '{certificate_type}' не найдена в списке"
            )

        certification.set_is_obtained(is_obtained)

    def add_supplier(self, supplier: Supplier) -> None:
        """Добавляет поставщика в список, если его еще нет.

        Args:
            supplier: Поставщик для добавления

        Raises:
            ValueError: если поставщик с таким supplier_id уже существует в списке
        """
        if not isinstance(supplier, Supplier):
            raise ValueError("Поставщик должен быть объектом класса Supplier")

        # Проверяем на дубликаты, используя стандартный оператор сравнения
        if supplier in self.suppliers:
            raise ValueError(
                f"Поставщик с ID '{supplier.supplier_id}' уже существует в списке"
            )

        self.suppliers.append(supplier)

    def remove_supplier(self, supplier_id: str) -> None:
        """Удаляет поставщика из списка по supplier_id.

        Args:
            supplier_id: ID поставщика для удаления
        """
        # Создаем временный объект Supplier для сравнения
        temp_supplier = Supplier(supplier_id=supplier_id)
        self.suppliers = [s for s in self.suppliers if s != temp_supplier]

    def add_backup_supplier(self, supplier: Supplier) -> None:
        """Добавляет резервного поставщика в список, если его еще нет.

        Args:
            supplier: Резервный поставщик для добавления

        Raises:
            ValueError: если резервный поставщик с таким supplier_id уже существует в списке
        """
        if not isinstance(supplier, Supplier):
            raise ValueError("Резервный поставщик должен быть объектом класса Supplier")

        # Проверяем на дубликаты, используя стандартный оператор сравнения
        if supplier in self.backup_suppliers:
            raise ValueError(
                f"Резервный поставщик с ID '{supplier.supplier_id}' уже существует в списке"
            )

        self.backup_suppliers.append(supplier)

    def remove_backup_supplier(self, supplier_id: str) -> None:
        """Удаляет резервного поставщика из списка по supplier_id.

        Args:
            supplier_id: ID резервного поставщика для удаления
        """
        # Создаем временный объект Supplier для сравнения
        temp_supplier = Supplier(supplier_id=supplier_id)
        self.backup_suppliers = [s for s in self.backup_suppliers if s != temp_supplier]

    def set_material_warehouse_inventory_worker(self, worker: Worker) -> None:
        if not isinstance(worker, Worker):
            raise ValueError("Кладовщик должен быть объектом класса Worker")
        self.materials_warehouse.set_inventory_worker(worker)

    def set_product_warehouse_inventory_worker(self, worker: Worker) -> None:
        if not isinstance(worker, Worker):
            raise ValueError("Кладовщик должен быть объектом класса Worker")
        self.product_warehouse.set_inventory_worker(worker)

    def increase_material_warehouse_size(self, size: int) -> None:
        """Увеличивает размер склада материалов на указанное количество единиц.

        Стоимость: 100 денег за одну единицу хранения.

        Args:
            size: количество единиц хранения для добавления (должно быть > 0)

        Raises:
            ValueError: если size <= 0 или недостаточно капитала
        """
        if size <= 0:
            raise ValueError("Размер должен быть больше нуля")

        cost = size * 100
        if self.capital < cost:
            raise ValueError(
                f"Недостаточно капитала. Требуется: {cost}, доступно: {self.capital}"
            )

        self.capital -= cost
        self.materials_warehouse.increase_size(size)

    def increase_product_warehouse_size(self, size: int) -> None:
        """Увеличивает размер склада продукции на указанное количество единиц.

        Стоимость: 100 денег за одну единицу хранения.

        Args:
            size: количество единиц хранения для добавления (должно быть > 0)

        Raises:
            ValueError: если size <= 0 или недостаточно капитала
        """
        if size <= 0:
            raise ValueError("Размер должен быть больше нуля")

        cost = size * 100
        if self.capital < cost:
            raise ValueError(
                f"Недостаточно капитала. Требуется: {cost}, доступно: {self.capital}"
            )

        self.capital -= cost
        self.product_warehouse.increase_size(size)

    def set_process_graph(self, process_graph: ProcessGraph) -> None:
        """Устанавливает граф процесса, сохраняя существующие рабочие места.

        Сохраняет существующие рабочие места (процессы неизменны), обновляет координаты
        существующих рабочих мест и добавляет только новые пути (routes) между рабочими
        местами из нового графа, если их еще нет.

        Args:
            process_graph: Новый граф процесса
        """
        if not isinstance(process_graph, ProcessGraph):
            raise ValueError("Граф процесса должен быть объектом класса ProcessGraph")

        # Проверяем, что все рабочие места из нового графа уже есть в существующем
        # Процессы (рабочие места) должны оставаться неизменными
        # Используем стандартный оператор сравнения Workplace (по workplace_id)
        existing_workplaces = set(self.processes.workplaces)

        # Находим рабочие места из нового графа, которых нет в существующем
        missing_workplaces = []
        for new_wp in process_graph.workplaces:
            if new_wp not in existing_workplaces:
                missing_workplaces.append(new_wp.workplace_id)

        if missing_workplaces:
            raise ValueError(
                f"В новом графе есть рабочие места, которых нет в существующем: {', '.join(missing_workplaces)}. "
                f"Процессы (рабочие места) должны оставаться неизменными."
            )

        # Обновляем ID графа, если он передан
        if process_graph.process_graph_id:
            self.processes.process_graph_id = process_graph.process_graph_id

        # Обновляем координаты существующих рабочих мест
        # Создаем словарь новых рабочих мест по ID для быстрого доступа
        new_workplaces_by_id = {wp.workplace_id: wp for wp in process_graph.workplaces}

        # Обновляем координаты существующих рабочих мест
        for existing_wp in self.processes.workplaces:
            if existing_wp.workplace_id in new_workplaces_by_id:
                new_wp = new_workplaces_by_id[existing_wp.workplace_id]
                # Обновляем координаты, если они указаны в новом графе
                existing_wp.x = new_wp.x
                existing_wp.y = new_wp.y

        # Добавляем только новые пути между существующими рабочими местами
        for new_route in process_graph.routes:
            # Проверяем, существует ли уже такой путь
            existing_route = self.processes.get_route(
                new_route.from_workplace, new_route.to_workplace
            )
            if existing_route is None:
                # Путь не существует, добавляем его используя метод ProcessGraph
                self.processes.add_route(new_route)

    def set_production_plan_row(self, row: ProductionPlanRow) -> None:
        """Обновляет строку производственного плана (set_production_plan_row).

        Строка должна уже существовать в производственном плане. Для добавления новой строки
        используйте метод add_tender, который создает строку автоматически.
        """
        self.production_schedule.update_row(row)

    def set_quality_inspection(self, supplier_id: str, enabled: bool) -> None:
        """Устанавливает проверку качества для материалов от поставщика (set_quality_inspection).

        Args:
            supplier_id: ID поставщика
            enabled: True для включения проверки качества, False для отключения

        Raises:
            ValueError: если поставщик с таким supplier_id не найден
        """
        if not isinstance(enabled, bool):
            raise ValueError("enabled должен быть булевым значением")

        is_found = False

        # Ищем поставщика в основном списке
        for supplier in self.suppliers:
            if supplier.supplier_id == supplier_id:
                supplier.set_quality_inspection(enabled)
                is_found = True
                break

        # Ищем поставщика в резервных поставщиках
        for supplier in self.backup_suppliers:
            if supplier.supplier_id == supplier_id:
                supplier.set_quality_inspection(enabled)
                is_found = True
                break

        if not is_found:
            raise ValueError(
                f"Поставщик с ID '{supplier_id}' не найден в списке поставщиков"
            )

    def set_delivery_period(self, supplier_id: str, delivery_period_days: int) -> None:
        """Устанавливает период поставок в днях для поставщика (set_delivery_period).

        Args:
            supplier_id: ID поставщика
            delivery_period_days: период поставок в днях

        Raises:
            ValueError: если поставщик с таким supplier_id не найден или delivery_period_days < 0
        """
        if delivery_period_days < 0:
            raise ValueError("Период поставок должен быть неотрицательным числом")

        # Создаем временный объект Supplier для поиска по ID
        temp_supplier = Supplier(supplier_id=supplier_id)

        # Ищем поставщика в основном списке
        for supplier in self.suppliers:
            if supplier == temp_supplier:
                supplier.set_delivery_period(delivery_period_days)
                return

        # Ищем поставщика в резервных поставщиках
        for supplier in self.backup_suppliers:
            if supplier == temp_supplier:
                supplier.set_delivery_period(delivery_period_days)
                return

        # Поставщик не найден
        raise ValueError(
            f"Поставщик с ID '{supplier_id}' не найден в списке поставщиков"
        )

    def set_equipment_maintenance_interval(
        self, equipment_id: str, interval_days: int
    ) -> None:
        """Устанавливает интервал обслуживания оборудования (set_equipment_maintenance_interval).

        Оборудование ищется по equipment_id среди всех рабочих мест в processes.

        Args:
            equipment_id: ID оборудования
            interval_days: интервал обслуживания в днях

        Raises:
            ValueError: если интервал < 0 или оборудование с таким equipment_id не найдено
        """
        if interval_days < 0:
            raise ValueError("Интервал обслуживания должен быть неотрицательным числом")

        # Создаем временный объект Equipment для поиска по ID

        # Ищем оборудование во всех рабочих местах
        for workplace in self.processes.workplaces:
            if (
                workplace.equipment is not None
                and workplace.equipment.equipment_id == equipment_id
            ):
                workplace.equipment.set_maintenance_period(interval_days)
                return

        # Оборудование не найдено
        raise ValueError(
            f"Оборудование с ID '{equipment_id}' не найдено на рабочих местах"
        )

    def set_certification_status(
        self, certificate_type: str, is_obtained: bool
    ) -> None:
        """Устанавливает статус сертификации (set_certification_status).

        Args:
            certificate_type: тип сертификации (certificate_type)
            is_obtained: True если сертификация получена, False если нет

        Raises:
            ValueError: если сертификация с таким типом не найдена в списке
        """
        if not isinstance(is_obtained, bool):
            raise ValueError("is_obtained должен быть булевым значением")

        # Создаем временный объект Certification для поиска по certificate_type

        # Ищем сертификацию в списке, используя стандартный оператор сравнения
        for cert in self.certifications:
            if cert.certificate_type == certificate_type:
                cert.set_is_obtained(is_obtained)
                return

        # Сертификация не найдена
        raise ValueError(
            f"Сертификация с типом '{certificate_type}' не найдена в списке"
        )

    def set_lean_improvement_status(self, name: str, is_implemented: bool) -> None:
        """Устанавливает статус LEAN улучшения (set_lean_improvement_status).

        Args:
            name: название улучшения (name)
            is_implemented: True если улучшение реализовано, False если нет

        Raises:
            ValueError: если улучшение с таким name не найдено в списке
        """
        if not isinstance(is_implemented, bool):
            raise ValueError("is_implemented должен быть булевым значением")

        # Ищем улучшение в списке по name
        for improvement in self.lean_improvements:
            if improvement.name == name:
                improvement.set_is_implemented(is_implemented)
                return

        # Улучшение не найдено
        raise ValueError(f"Улучшение с названием '{name}' не найдено в списке")

    def set_dealing_with_defects(self, policy: DealingWithDefects) -> None:
        """Устанавливает политику работы с дефектами.

        Args:
            policy: объект enum DealingWithDefects

        Raises:
            ValueError: если policy не является объектом класса DealingWithDefects
        """
        if not isinstance(policy, DealingWithDefects):
            raise ValueError(
                "Политика работы с дефектами должна быть объектом класса DealingWithDefects"
            )
        self.dealing_with_defects = policy

    def set_sales_strategy(
        self,
        strategy: str,
    ) -> None:
        """Устанавливает стратегию продаж (set_sales_strategy).

        Args:
            strategy: строка со значением стратегии продаж (значение enum SaleStrategest)

        Raises:
            ValueError: если strategy не является валидным значением SaleStrategest
        """
        if not isinstance(strategy, str):
            raise ValueError("Стратегия продаж должна быть строкой")

        # Пытаемся создать enum из строки
        try:
            sales_strategy = SaleStrategest(strategy)
        except ValueError:
            raise ValueError(
                f"Недопустимое значение стратегии продаж: '{strategy}'. "
                f"Допустимые значения: {[s.value for s in SaleStrategest]}"
            )

        self.sales_strategy = sales_strategy

    def get_required_materials(self) -> List[RequiredMaterial]:
        """Получает список требуемых материалов (get_required_materials).

        Returns:
            Список требуемых материалов (константный список класса)
        """
        return self.REQUIRED_MATERIALS

    def get_available_improvements(self) -> List[str]:
        """Получает список доступных LEAN улучшений (get_available_improvements).

        Returns:
            Список названий улучшений из production_improvements
        """
        return [improvement.name for improvement in self.production_improvements]

    def get_defect_policies(self) -> tuple[List[str], str]:
        """Получает доступные политики обработки дефектов и текущую (get_defect_policies).

        Returns:
            tuple: (список доступных политик, текущая политика)
        """
        # Получаем все доступные политики из enum
        available_policies = [policy.value for policy in DealingWithDefects]
        # Текущая политика - значение enum объекта
        current_policy = self.dealing_with_defects.value
        return (available_policies, current_policy)

    @property
    def is_simulation_parameters_empty(self) -> bool:
        return _is_empty_simulation_parameters(self)


def _is_empty_simulation_parameters(
    simulation_parameters: SimulationParameters,
) -> bool:
    if simulation_parameters is None:
        return True

    if simulation_parameters.logist is None:
        return True

    if (
        simulation_parameters.suppliers is None
        or len(simulation_parameters.suppliers) == 0
    ):
        return True

    if (
        simulation_parameters.backup_suppliers is None
        or len(simulation_parameters.backup_suppliers) == 0
    ):
        return True

    if (
        simulation_parameters.product_warehouse is None
        or simulation_parameters.product_warehouse.size == 0
    ):
        return True

    if (
        simulation_parameters.materials_warehouse is None
        or simulation_parameters.materials_warehouse.size == 0
    ):
        return True

    if (
        simulation_parameters.processes is None
        or simulation_parameters.processes.process_graph_id is None
    ):
        return True

    if simulation_parameters.tenders is None or len(simulation_parameters.tenders) == 0:
        return True

    if simulation_parameters.dealing_with_defects is None:
        return True

    if (
        simulation_parameters.production_improvements is None
        or len(simulation_parameters.production_improvements) == 0
    ):
        return True

    if simulation_parameters.sales_strategy is None:
        return True

    if simulation_parameters.production_schedule is None:
        return True

    if (
        simulation_parameters.certifications is None
        or len(simulation_parameters.certifications) == 0
    ):
        return True

    if (
        simulation_parameters.lean_improvements is None
        or len(simulation_parameters.lean_improvements) == 0
    ):
        return True

    if simulation_parameters.distribution_strategy is None:
        return True

    if simulation_parameters.step is None:
        return True


@dataclass
class SimulationResults(RedisSerializable):
    """Результаты симуляции. Соответствует proto message SimulationResults."""

    profit: int = 0  # int64 в proto
    cost: int = 0  # int64 в proto, затраты
    profitability: float = 0.0
    factory_metrics: Optional[FactoryMetrics] = field(default=None)
    production_metrics: Optional[ProductionMetrics] = field(default=None)
    quality_metrics: Optional[QualityMetrics] = field(default=None)
    engineering_metrics: Optional[EngineeringMetrics] = field(default=None)
    commercial_metrics: Optional[CommercialMetrics] = field(default=None)
    procurement_metrics: Optional[ProcurementMetrics] = field(default=None)
    product_warehouse_metrics: Optional[WarehouseMetrics] = field(default=None)
    materials_warehouse_metrics: Optional[WarehouseMetrics] = field(default=None)
    step: int = field(default=0)  # uint32 в proto


@dataclass
class Simulation(RedisSerializable):
    """Симуляция. Соответствует proto message Simulation."""

    capital: int = 0  # uint32 в proto
    simulation_id: str = ""  # string в proto
    parameters: List[SimulationParameters] = field(
        default_factory=list
    )  # repeated в proto
    results: List[SimulationResults] = field(default_factory=list)  # repeated в proto
    room_id: str = ""  # string в proto
    is_completed: bool = field(default=False)  # bool в proto

    def get_procurement_metrics(self, step: int) -> Optional[ProcurementMetrics]:
        """Получает метрики закупок для указанного шага симуляции (get_procurement_metrics).

        Args:
            step: номер шага симуляции

        Returns:
            ProcurementMetrics из результатов симуляции для указанного шага
        """
        # Ищем результат с указанным шагом
        for result in self.results:
            if result.step == step:
                if result.procurement_metrics is not None:
                    return result.procurement_metrics
                return None

        return None

    def get_factory_metrics(self, step: int) -> Optional[FactoryMetrics]:
        """Получает метрики завода для указанного шага симуляции (get_factory_metrics).

        Args:
            step: номер шага симуляции

        Returns:
            FactoryMetrics из результатов симуляции для указанного шага, или None если не найден
        """
        # Ищем результат с указанным шагом
        for result in self.results:
            if result.step == step:
                return result.factory_metrics

        return None

    def get_production_metrics(self, step: int) -> Optional[ProductionMetrics]:
        """Получает метрики производства для указанного шага симуляции (get_production_metrics).

        Args:
            step: номер шага симуляции

        Returns:
            ProductionMetrics из результатов симуляции для указанного шага, или None если не найден
        """
        # Ищем результат с указанным шагом
        for result in self.results:
            if result.step == step:
                return result.production_metrics

        return None

    def get_quality_metrics(self, step: int) -> Optional[QualityMetrics]:
        """Получает метрики качества для указанного шага симуляции (get_quality_metrics).

        Args:
            step: номер шага симуляции

        Returns:
            QualityMetrics из результатов симуляции для указанного шага, или None если не найден
        """
        # Ищем результат с указанным шагом
        for result in self.results:
            if result.step == step:
                return result.quality_metrics

        return None

    def get_engineering_metrics(self, step: int) -> Optional[EngineeringMetrics]:
        """Получает инженерные метрики для указанного шага симуляции (get_engineering_metrics).

        Args:
            step: номер шага симуляции

        Returns:
            EngineeringMetrics из результатов симуляции для указанного шага, или None если не найден
        """
        # Ищем результат с указанным шагом
        for result in self.results:
            if result.step == step:
                return result.engineering_metrics

        return None

    def get_commercial_metrics(self, step: int) -> Optional[CommercialMetrics]:
        """Получает коммерческие метрики для указанного шага симуляции (get_commercial_metrics).

        Args:
            step: номер шага симуляции

        Returns:
            CommercialMetrics из результатов симуляции для указанного шага, или None если не найден
        """
        # Ищем результат с указанным шагом
        for result in self.results:
            if result.step == step:
                return result.commercial_metrics

        return None

    def get_all_metrics(
        self,
        step: int,
    ) -> Dict[
        str,
        Optional[
            Union[
                FactoryMetrics,
                ProductionMetrics,
                QualityMetrics,
                EngineeringMetrics,
                CommercialMetrics,
                ProcurementMetrics,
            ]
        ],
    ]:
        """Получает все метрики для указанного шага симуляции (get_all_metrics).

        Args:
            step: номер шага симуляции

        Returns:
            Dict с ключами: factory, production, quality, engineering, commercial, procurement
            Значения могут быть None, если метрика не найдена для указанного шага
        """
        # Ищем результат с указанным шагом
        result = None
        for res in self.results:
            if res.step == step:
                result = res
                break

        # Если результат не найден, возвращаем все метрики как None
        if result is None:
            return {
                "factory": None,
                "production": None,
                "quality": None,
                "engineering": None,
                "commercial": None,
                "procurement": None,
            }

        # Возвращаем все метрики из найденного результата
        return {
            "factory": result.factory_metrics,
            "production": result.production_metrics,
            "quality": result.quality_metrics,
            "engineering": result.engineering_metrics,
            "commercial": result.commercial_metrics,
            "procurement": result.procurement_metrics,
        }

    def get_unplanned_repair(self, step: int) -> Optional[UnplannedRepair]:
        """Получает информацию о внеплановых ремонтах для указанного шага симуляции (get_unplanned_repair).

        Args:
            step: номер шага симуляции

        Returns:
            UnplannedRepair из результатов симуляции для указанного шага, или None если не найден
        """
        # Ищем результат с указанным шагом
        for result in self.results:
            if result.step == step:
                # Проверяем наличие поля unplanned_repair (может быть добавлено в будущем)
                if hasattr(result, "unplanned_repair"):
                    return result.unplanned_repair
                return None

        return None

    def get_workshop_plan(self, step: int) -> Optional[ProcessGraph]:
        """Получает план цеха для указанного шага симуляции (get_workshop_plan).

        Args:
            step: номер шага симуляции

        Returns:
            ProcessGraph (workshop plan) из parameters для указанного шага, или None если не найден
        """
        # Ищем параметры с указанным шагом
        for params in self.parameters:
            if params.step == step:
                return params.processes

        # Если не найдено, возвращаем None
        return None

    def get_production_schedule(self, step: int) -> Optional[ProductionSchedule]:
        """Получает производственный план для указанного шага симуляции (get_production_schedule).

        Args:
            step: номер шага симуляции

        Returns:
            ProductionSchedule из parameters для указанного шага, или None если не найден
        """
        # Ищем параметры с указанным шагом
        for params in self.parameters:
            if params.step == step:
                return params.production_schedule

        # Если не найдено, возвращаем None
        return None

    def get_warehouse_load_chart(self, warehouse_type: str, step: int) -> Dict:
        """Получает график загрузки склада для указанного типа и шага (get_warehouse_load_chart).

        Args:
            warehouse_type: тип склада (например, "materials" или "products")
            step: номер шага симуляции

        Returns:
            Dict с ключами:
                - "load": List[int] - массив загруженности от времени
                - "max_capacity": List[int] - массив максимальной вместимости от времени
            Или пустой словарь, если данные не найдены
        """
        # Получаем метрики завода для указанного шага
        factory_metrics = self.get_factory_metrics(step)

        if factory_metrics is None:
            return {}

        # Ищем метрики склада по типу
        warehouse_metrics = factory_metrics.warehouse_metrics.get(warehouse_type)

        if warehouse_metrics is None:
            return {}

        # Возвращаем данные для графика
        return {
            "load": warehouse_metrics.load_over_time,
            "max_capacity": warehouse_metrics.max_capacity_over_time,
        }

    def run_simulation(self) -> None:
        if len(self.results) >= MAX_SIMULATION_STEPS:
            # прикол в том что при зупуске у нас уже есть один инстнс настроек симуляции
            # то есть условновня итерация
            # parameters = 1 rsults = 0
            # parameters = 2 rsults = 1
            # parameters = 3 rsults = 2
            # parameters = 4 rsults = 3
            # parameters = 4 parameters = 4
            # дальше идет raise

            raise ValueError("Максимальное количество шагов симуляции уже достигнуто")

        try:
            parameters = max(self.parameters, key=lambda p: p.step)

        except ValueError:
            raise ValueError("Отсутвуют параметры для выполнения симуляции")

        results = _run_simulation(parameters)

        self.results.append(results)
        # Создаем копию параметров с увеличенным step для следующего запуска
        next_parameters = SimulationParameters.from_simulation_parameters(parameters)
        next_parameters.step = parameters.step + 1
        self.parameters.append(next_parameters)

    def validate_configuration(self) -> Dict[str, Union[bool, List[str]]]:
        """Валидирует конфигурацию симуляции (validate_configuration).

        Returns:
            Dict с ключами: is_valid (bool), errors (List[str]), warnings (List[str])
        """
        # Всегда возвращаем, что валидация корректна
        return {
            "is_valid": True,
            "errors": [],
            "warnings": [],
        }


def _calculate_cost(simulation_parameters: SimulationParameters) -> int:
    cost = 0
    four_year_in_days = 4 * DAYS_IN_YEAR

    for supplier in simulation_parameters.suppliers:
        delivery_period = _safe_int(getattr(supplier, "delivery_period", 0), 1)
        supplier_cost = _safe_int(getattr(supplier, "cost", 0), 0)
        cost += supplier_cost * (four_year_in_days // max(1, delivery_period))

    for workplace in simulation_parameters.processes.workplaces:
        if workplace.equipment is not None:
            cost += _safe_int(workplace.equipment.cost, 0)
        if workplace.worker is not None:
            cost += _safe_int(workplace.worker.salary, 0) * (four_year_in_days // 12)

    # В proto у Route есть только length; используем его как основу стоимости.
    for route in simulation_parameters.processes.routes:
        route_length = _safe_int(getattr(route, "length", 0), 0)
        cost += route_length

    return cost


def _calculate_profit(simulation_parameters: SimulationParameters) -> int:
    profit = 0
    for tender in simulation_parameters.tenders:
        profit += tender.cost
    return profit


def _run_simulation(
    simulation_parameters: SimulationParameters,
) -> SimulationResults:
    if simulation_parameters.is_simulation_parameters_empty:
        raise ValueError("Отсутвуют параметры для выполнения симуляции")

    try:
        cost = _calculate_cost(simulation_parameters)
        profit = _calculate_profit(simulation_parameters)
        profitability = profit / cost
        return SimulationResults(
            cost=cost,
            profit=profit,
            profitability=profitability,
            step=simulation_parameters.step,
            factory_metrics=_calculate_fatory_metrics(simulation_parameters),
            production_metrics=_calculate_production_metrics(simulation_parameters),
            quality_metrics=_calculate_quality_metrics(simulation_parameters),
            engineering_metrics=_calculate_engineering_metrics(simulation_parameters),
            commercial_metrics=_calculate_commercial_metrics(simulation_parameters),
            procurement_metrics=_calculate_procurement_metrics(simulation_parameters),
        )
    except Exception as exc:  # pragma: no cover - диагностическое ветвление
        import traceback

        raise ValueError(
            f"Ошибка расчета симуляции: {exc}; stack: {traceback.format_exc()}"
        ) from exc


def _calculate_deffect_rate(simulation_parameters: SimulationParameters) -> float:
    defect_rate = 0.0
    for supplier in simulation_parameters.suppliers:
        defect_rate += max(0, (1.0 - supplier.product_quality))

    return defect_rate


def _calculate_on_time_delivery_rate(
    simulation_parameters: SimulationParameters,
) -> float:
    # Используем среднюю надежность поставщиков как базу для своевременных поставок.
    if not simulation_parameters.suppliers:
        return 0.0

    reliability_values = [
        supplier.reliability for supplier in simulation_parameters.suppliers
    ]
    avg_reliability = sum(reliability_values) / len(reliability_values)

    # Учитываем влияние резервных поставщиков: повышают вероятность своевременных поставок.
    backup_bonus = 0.02 * len(simulation_parameters.backup_suppliers)

    # Пенальти за длинный интервал поставки (сравниваем с недельным тактом).
    interval_penalties = []
    for supplier in simulation_parameters.suppliers:
        delivery_period_days = _safe_int(
            getattr(supplier, "delivery_period_days", 0), 0
        )
        if delivery_period_days > 14:
            interval_penalties.append(0.15)
        elif delivery_period_days > 7:
            interval_penalties.append(0.05)
        else:
            interval_penalties.append(0.0)

    interval_penalty = (
        sum(interval_penalties) / len(interval_penalties) if interval_penalties else 0.0
    )

    rate = avg_reliability + backup_bonus - interval_penalty
    return max(0.0, min(1.0, rate))


def _collect_improvements(simulation_parameters: SimulationParameters) -> set:
    """Возвращает множество идентификаторов внедренных улучшений."""
    improvements = set()
    for imp in simulation_parameters.production_improvements:
        if imp.is_implemented:
            normalized = imp.name.strip().lower()
            if "5s" in normalized:
                improvements.add("5s")
            if "poka" in normalized or "пока" in normalized:
                improvements.add("poka_yoke")
            if "kanban" in normalized or "канбан" in normalized:
                improvements.add("kanban")
            if "smed" in normalized:
                improvements.add("smed")
            if "sop" in normalized or "стандарт" in normalized:
                improvements.add("sop")
            if "tpm" in normalized:
                improvements.add("tpm")
            if "предиктив" in normalized:
                improvements.add("predictive")
    return improvements


def _maintenance_interval_penalty(interval_days: int, kind: str) -> float:
    """Возвращает штраф за интервал ТО. kind: availability|performance|quality."""
    if interval_days >= 14:
        return (
            0.5 if kind == "availability" else (0.6 if kind == "performance" else 0.30)
        )
    if interval_days >= 7:
        return (
            0.10
            if kind == "availability"
            else (0.20 if kind == "performance" else 0.07)
        )
    if interval_days >= 1:
        return (
            0.03
            if kind == "availability"
            else (0.07 if kind == "performance" else 0.015)
        )
    return 0.0


def _qualification_penalty(required: int, actual: int, quality: bool = False) -> float:
    if required <= 0:
        return 0.0
    diff = max(0, required - actual)
    deviation = diff / required

    if deviation >= 0.5:
        return 0.5 if quality else 0.6
    if deviation >= 0.25:
        return 0.20 if quality else 0.25
    if deviation >= 0.10:
        return 0.08 if quality else 0.11
    if deviation >= 0.01:
        return 0.03 if quality else 0.05
    return 0.0


def _human_factor_penalty(qualification: int) -> float:
    if qualification >= 7:
        return 0.025
    if qualification >= 4:
        return 0.04
    if qualification >= 1:
        return 0.10
    return 0.0


def _calculate_availability_factor(
    simulation_parameters: SimulationParameters,
) -> float:
    penalties = []
    improvements = _collect_improvements(simulation_parameters)
    predictive_bonus = 0.02 if "predictive" in improvements else 0.0

    for workplace in simulation_parameters.processes.workplaces:
        if workplace.equipment:
            penalties.append(
                _maintenance_interval_penalty(
                    workplace.equipment.maintenance_period, "availability"
                )
            )
        if workplace.worker:
            penalties.append(
                _qualification_penalty(
                    workplace.required_qualification,
                    workplace.worker.qualification,
                    False,
                )
            )

    penalty = sum(penalties) / len(penalties) if penalties else 0.0
    availability = 1.0 - penalty + predictive_bonus
    return max(0.0, min(1.0, availability))


def _calculate_performance_factor(simulation_parameters: SimulationParameters) -> float:
    penalties = []
    improvements = _collect_improvements(simulation_parameters)

    for workplace in simulation_parameters.processes.workplaces:
        # Интервалы ТО
        if workplace.equipment:
            penalties.append(
                _maintenance_interval_penalty(
                    workplace.equipment.maintenance_period, "performance"
                )
            )

        # Квалификация
        if workplace.worker:
            penalties.append(
                _qualification_penalty(
                    workplace.required_qualification,
                    workplace.worker.qualification,
                    False,
                )
            )

        # Человеческий фактор
        if workplace.worker and "poka_yoke" not in improvements:
            penalties.append(_human_factor_penalty(workplace.worker.qualification))

    # Положительный эффект улучшений
    bonus = 0.0
    bonus += 0.10 if "5s" in improvements else 0.0
    bonus += 0.07 if "poka_yoke" in improvements else 0.0
    bonus += 0.05 if "kanban" in improvements else 0.0
    bonus += 0.08 if "smed" in improvements else 0.0
    bonus += 0.15 if "sop" in improvements else 0.0
    bonus += 0.06 if "tpm" in improvements else 0.0

    penalty = sum(penalties) / len(penalties) if penalties else 0.0
    performance = 1.0 - penalty + bonus
    return max(0.0, min(1.2, performance))


def _market_growth_multiplier(strategy: SaleStrategest) -> float:
    if strategy == SaleStrategest.NONE:
        return -0.1
    if strategy == SaleStrategest.LOW_PRICES:
        return 0.05
    if strategy == SaleStrategest.DIFFERENTIATION:
        return 0.10
    if strategy == SaleStrategest.PREMIUM:
        return 0.15
    if strategy == SaleStrategest.FOCUS:
        return 0.08
    return 0.0


def _calculate_oee(simulation_parameters: SimulationParameters) -> float:
    availability = _calculate_availability_factor(simulation_parameters)
    performance = _calculate_performance_factor(simulation_parameters)
    quality = max(0.0, 1.0 - _calculate_defect_percentage(simulation_parameters))

    oee = availability * performance * quality
    return max(0.0, min(1.0, oee))


def _calculate_fatory_metrics(
    simulation_parameters: SimulationParameters,
) -> FactoryMetrics:
    warehouse_metrics = {
        "product_warehouse": _calculate_product_warehouse_metrics(
            simulation_parameters
        ),
        "materials_warehouse": _calculate_materials_warehouse_metrics(
            simulation_parameters
        ),
    }

    cost = _calculate_cost(simulation_parameters)
    profit = _calculate_profit(simulation_parameters)
    profitability = profit / cost

    return FactoryMetrics(
        profitability=profitability,
        warehouse_metrics=warehouse_metrics,
        total_procurement_cost=cost,
        defect_rate=_calculate_deffect_rate(simulation_parameters),
        on_time_delivery_rate=_calculate_on_time_delivery_rate(simulation_parameters),
        oee=_calculate_oee(simulation_parameters),
    )


def _calculate_monthly_productivity(
    simulation_parameters: SimulationParameters,
) -> List[ProductionMetrics.MonthlyProductivity]:
    months = [
        "Январь",
        "Февраль",
        "Март",
        "Апрель",
        "Май",
        "Июнь",
        "Июль",
        "Август",
        "Сентябрь",
        "Октябрь",
        "Ноябрь",
        "Декабрь",
    ]
    productivity: List[ProductionMetrics.MonthlyProductivity] = []

    performance = _calculate_performance_factor(simulation_parameters)
    availability = _calculate_availability_factor(simulation_parameters)
    quality = max(0.1, 1.0 - _calculate_defect_percentage(simulation_parameters))

    base_units = 1200
    for month in months:
        multiplier = performance * availability * quality
        units = int(base_units * multiplier)
        productivity.append(
            ProductionMetrics.MonthlyProductivity(
                month=month,
                units_produced=units,
            )
        )

    return productivity


def _calculate_average_equipment_utilization(
    simulation_parameters: SimulationParameters,
) -> float:
    # Используем фактор производительности как приближение коэффициента загрузки.
    utilization = _calculate_performance_factor(simulation_parameters)
    return max(0.0, min(1.0, utilization))


def _calculate_wip_count(
    simulation_parameters: SimulationParameters,
) -> int:
    # Приблизительно оцениваем WIP как количество рабочих мест * (1 - доступность).
    availability = _calculate_availability_factor(simulation_parameters)
    workplaces_count = len(simulation_parameters.processes.workplaces)
    return int(workplaces_count * max(0.0, 1.0 - availability))


def _calculate_finished_goods_count(
    simulation_parameters: SimulationParameters,
) -> int:
    # Используем произведенные единицы за месяц как оценку готовой продукции.
    monthly = _calculate_monthly_productivity(simulation_parameters)
    return sum(item.units_produced for item in monthly)


def _calculate_material_reserves(
    simulation_parameters: SimulationParameters,
) -> Dict[str, int]:
    return {
        k: int(v)
        for k, v in simulation_parameters.materials_warehouse.materials.items()
    }


def _calculate_production_metrics(
    simulation_parameters: SimulationParameters,
) -> ProductionMetrics:

    return ProductionMetrics(
        monthly_productivity=_calculate_monthly_productivity(simulation_parameters),
        average_equipment_utilization=_calculate_average_equipment_utilization(
            simulation_parameters
        ),
        wip_count=_calculate_wip_count(simulation_parameters),
        finished_goods_count=_calculate_finished_goods_count(simulation_parameters),
        material_reserves=_calculate_material_reserves(simulation_parameters),
    )


def _calculate_defect_percentage(
    simulation_parameters: SimulationParameters,
) -> float:
    base_defect = 0.15  # Изначальные потери по таблице

    maintenance_penalties = []
    qualification_penalties = []
    human_factor_penalties = []

    # Улучшения качества
    quality_improvements = _collect_improvements(simulation_parameters)
    has_poka_yoke = "poka_yoke" in quality_improvements
    has_sop = "sop" in quality_improvements

    for workplace in simulation_parameters.processes.workplaces:
        # Пенальти за квалификацию
        qual_penalty = _qualification_penalty(
            workplace.required_qualification,
            workplace.worker.qualification if workplace.worker else 0,
            quality=True,
        )
        qualification_penalties.append(qual_penalty)

        # Человеческий фактор (если нет poka-yoke)
        if not has_poka_yoke and workplace.worker:
            human_factor_penalties.append(
                _human_factor_penalty(workplace.worker.qualification)
            )

        # Пенальти за ТО оборудования
        if workplace.equipment:
            maintenance_penalties.append(
                _maintenance_interval_penalty(
                    workplace.equipment.maintenance_period, "quality"
                )
            )

    maintenance_penalty = (
        sum(maintenance_penalties) / len(maintenance_penalties)
        if maintenance_penalties
        else 0.0
    )
    qualification_penalty = (
        sum(qualification_penalties) / len(qualification_penalties)
        if qualification_penalties
        else 0.0
    )
    human_penalty = (
        sum(human_factor_penalties) / len(human_factor_penalties)
        if human_factor_penalties
        else 0.0
    )

    # Влияние поставщиков (рандомный брак, если нет входного контроля)
    supplier_defects = []
    for supplier in simulation_parameters.suppliers:
        if supplier.quality_inspection_enabled:
            supplier_defects.append(0.0)
            continue

        if supplier.reliability >= 0.9:
            supplier_defects.append(0.01)
        elif supplier.reliability >= 0.75:
            supplier_defects.append(0.05)
        else:
            supplier_defects.append(0.15)

    supplier_penalty = (
        sum(supplier_defects) / len(supplier_defects) if supplier_defects else 0.0
    )

    improvement_bonus = 0.0
    if has_poka_yoke:
        improvement_bonus += 0.10
    if has_sop:
        improvement_bonus += 0.05

    defect = (
        base_defect
        + maintenance_penalty
        + qualification_penalty
        + human_penalty
        + supplier_penalty
    )
    defect = max(0.0, defect - improvement_bonus)
    return min(defect, 0.99)


def _calculate_good_output_percentage(
    simulation_parameters: SimulationParameters,
) -> float:
    defect = _calculate_defect_percentage(simulation_parameters)
    return max(0.0, 1.0 - defect)


def _calculate_defect_causes(
    simulation_parameters: SimulationParameters,
) -> List[QualityMetrics.DefectCause]:
    defects = []
    defect_percentage = _calculate_defect_percentage(simulation_parameters)

    # Распределяем основные причины: оборудование, человек, материалы.
    equipment_share = 0.4 * defect_percentage
    human_share = 0.35 * defect_percentage
    material_share = defect_percentage - equipment_share - human_share

    defects.append(
        QualityMetrics.DefectCause(
            cause="Оборудование (интервалы ТО)",
            count=int(equipment_share * 100),
            percentage=equipment_share,
        )
    )
    defects.append(
        QualityMetrics.DefectCause(
            cause="Человеческий фактор",
            count=int(human_share * 100),
            percentage=human_share,
        )
    )
    defects.append(
        QualityMetrics.DefectCause(
            cause="Материалы/поставщики",
            count=int(material_share * 100),
            percentage=material_share,
        )
    )

    return defects


def _calculate_average_material_quality(
    simulation_parameters: SimulationParameters,
) -> float:
    if not simulation_parameters.suppliers:
        return 0.0
    qualities = [
        supplier.product_quality for supplier in simulation_parameters.suppliers
    ]
    return sum(qualities) / len(qualities)


def _calculate_average_supplier_failure_probability(
    simulation_parameters: SimulationParameters,
) -> float:
    if not simulation_parameters.suppliers:
        return 0.0
    failures = [
        1.0 - supplier.reliability for supplier in simulation_parameters.suppliers
    ]
    return sum(failures) / len(failures)


def _calculate_procurement_volume(
    simulation_parameters: SimulationParameters,
) -> int:
    base_volume = len(simulation_parameters.suppliers)
    failure_multiplier = 1.0 + _calculate_average_supplier_failure_probability(
        simulation_parameters
    )
    return int(base_volume * failure_multiplier)


def _calculate_quality_metrics(
    simulation_parameters: SimulationParameters,
) -> QualityMetrics:
    return QualityMetrics(
        defect_percentage=_calculate_defect_percentage(simulation_parameters),
        good_output_percentage=_calculate_good_output_percentage(simulation_parameters),
        defect_causes=_calculate_defect_causes(simulation_parameters),
        average_material_quality=_calculate_average_material_quality(
            simulation_parameters
        ),
        average_supplier_failure_probability=_calculate_average_supplier_failure_probability(
            simulation_parameters
        ),
        procurement_volume=_calculate_procurement_volume(simulation_parameters),
    )


def _calculate_engineering_metrics(
    simulation_parameters: SimulationParameters,
) -> EngineeringMetrics:
    return EngineeringMetrics(
        operation_timings=_calculate_operation_timings(simulation_parameters),
        downtime_records=_calculate_downtime_records(simulation_parameters),
        defect_analysis=_calculate_defect_analysis(simulation_parameters),
    )


def _calculate_operation_timings(
    simulation_parameters: SimulationParameters,
) -> List[EngineeringMetrics.OperationTiming]:
    timings = []
    # Берем время цикла как функцию требуемой и фактической квалификации.
    for workplace in simulation_parameters.processes.workplaces:
        required = workplace.required_qualification or 1
        actual = workplace.worker.qualification if workplace.worker else 0
        mismatch = max(0, required - actual) / required

        base_cycle = 60  # минут
        if mismatch >= 0.5:
            base_cycle *= 1.6
        elif mismatch >= 0.25:
            base_cycle *= 1.25
        elif mismatch >= 0.1:
            base_cycle *= 1.11
        elif mismatch >= 0.01:
            base_cycle *= 1.05

        timings.append(
            EngineeringMetrics.OperationTiming(
                operation_name=workplace.workplace_name or workplace.workplace_id,
                cycle_time=int(base_cycle),
                takt_time=int(base_cycle),
                timing_cost=int(base_cycle * 10),
            )
        )

    return timings


def _calculate_downtime_records(
    simulation_parameters: SimulationParameters,
) -> List[EngineeringMetrics.DowntimeRecord]:
    records = []
    for workplace in simulation_parameters.processes.workplaces:
        if workplace.equipment is None:
            continue
        equipment = workplace.equipment
        penalty = _maintenance_interval_penalty(
            equipment.maintenance_period, "availability"
        )

        total_minutes = int(penalty * int(equipment.repair_time) * 60)
        records.append(
            EngineeringMetrics.DowntimeRecord(
                cause=f"ТО {equipment.name}" if equipment.name else "ТО оборудования",
                total_minutes=total_minutes,
                average_per_shift=total_minutes / 3 if total_minutes else 0,
            )
        )

    return records


def _calculate_defect_analysis(
    simulation_parameters: SimulationParameters,
) -> List[EngineeringMetrics.DefectAnalysis]:
    causes = _calculate_defect_causes(simulation_parameters)
    analysis = []
    cumulative = 0.0
    for cause in causes:
        cumulative += cause.percentage
        analysis.append(
            EngineeringMetrics.DefectAnalysis(
                defect_type=cause.cause,
                count=cause.count,
                percentage=cause.percentage,
                cumulative_percentage=min(1.0, cumulative),
            )
        )
    return analysis


def _calculate_yearly_revenues(
    simulation_parameters: SimulationParameters,
) -> List[CommercialMetrics.YearlyRevenue]:
    revenues = []
    base = _calculate_profit(simulation_parameters)
    for year in range(1, 5):
        growth = _market_growth_multiplier(simulation_parameters.sales_strategy)
        revenue = int(base * (1 + growth) * year)
        revenues.append(CommercialMetrics.YearlyRevenue(year=year, revenue=revenue))
    return revenues


def _calculate_tender_revenue_plan(
    simulation_parameters: SimulationParameters,
) -> int:
    return sum(int(tender.cost) for tender in simulation_parameters.tenders)


def _calculate_total_payments(
    simulation_parameters: SimulationParameters,
) -> int:
    equipment_costs = sum(
        int(wp.equipment.cost)
        for wp in simulation_parameters.processes.workplaces
        if wp.equipment
    )
    maintenance_costs = sum(
        int(wp.equipment.maintenance_cost)
        for wp in simulation_parameters.processes.workplaces
        if wp.equipment
    )
    supplier_costs = sum(
        int(supplier.cost) for supplier in simulation_parameters.suppliers
    )
    improvement_costs = sum(
        int(imp.implementation_cost)
        for imp in simulation_parameters.production_improvements
        if imp.is_implemented
    )

    return equipment_costs + maintenance_costs + supplier_costs + improvement_costs


def _calculate_total_receipts(
    simulation_parameters: SimulationParameters,
) -> int:
    return _calculate_profit(simulation_parameters)


def _calculate_sales_forecast(
    simulation_parameters: SimulationParameters,
) -> Dict[str, float]:
    growth = _market_growth_multiplier(simulation_parameters.sales_strategy)
    return {"market_growth": growth}


def _calculate_strategy_costs(
    simulation_parameters: SimulationParameters,
) -> Dict[str, int]:
    strategy = simulation_parameters.sales_strategy
    costs = {
        "strategy": strategy.value if hasattr(strategy, "value") else str(strategy)
    }
    if strategy == SaleStrategest.LOW_PRICES:
        costs["marketing"] = 10000
    elif strategy == SaleStrategest.DIFFERENTIATION:
        costs["marketing"] = 15000
    elif strategy == SaleStrategest.PREMIUM:
        costs["marketing"] = 20000
    elif strategy == SaleStrategest.FOCUS:
        costs["marketing"] = 8000
    else:
        costs["marketing"] = 0
    return costs


def _calculate_tender_graph(
    simulation_parameters: SimulationParameters,
) -> List[CommercialMetrics.TenderGraphPoint]:
    points = []
    for tender in simulation_parameters.tenders:
        points.append(
            CommercialMetrics.TenderGraphPoint(
                strategy=(
                    str(simulation_parameters.sales_strategy.value)
                    if hasattr(simulation_parameters.sales_strategy, "value")
                    else str(simulation_parameters.sales_strategy)
                ),
                unit_size=str(tender.quantity_of_products),
                is_mastered=tender.cost > 0,
            )
        )
    return points


def _calculate_project_profitabilities(
    simulation_parameters: SimulationParameters,
) -> List[CommercialMetrics.ProjectProfitability]:
    profitabilities = []
    total_cost = _calculate_total_payments(simulation_parameters)
    for tender in simulation_parameters.tenders:
        profitability = (tender.cost - total_cost) / total_cost if total_cost else 0
        profitabilities.append(
            CommercialMetrics.ProjectProfitability(
                project_name=tender.tender_id, profitability=profitability
            )
        )
    return profitabilities


def _calculate_on_time_completed_orders(
    simulation_parameters: SimulationParameters,
) -> int:
    reliability = _calculate_on_time_delivery_rate(simulation_parameters)
    return int(len(simulation_parameters.tenders) * reliability)


def _calculate_commercial_metrics(
    simulation_parameters: SimulationParameters,
) -> CommercialMetrics:
    return CommercialMetrics(
        yearly_revenues=_calculate_yearly_revenues(simulation_parameters),
        tender_revenue_plan=_calculate_tender_revenue_plan(simulation_parameters),
        total_payments=_calculate_total_payments(simulation_parameters),
        total_receipts=_calculate_total_receipts(simulation_parameters),
        sales_forecast=_calculate_sales_forecast(simulation_parameters),
        strategy_costs=_calculate_strategy_costs(simulation_parameters),
        tender_graph=_calculate_tender_graph(simulation_parameters),
        project_profitabilities=_calculate_project_profitabilities(
            simulation_parameters
        ),
        on_time_completed_orders=_calculate_on_time_completed_orders(
            simulation_parameters
        ),
    )


def _calculate_procurement_metrics(
    simulation_parameters: SimulationParameters,
) -> ProcurementMetrics:
    return ProcurementMetrics(
        supplier_performances=_calculate_supplier_performances(simulation_parameters),
        total_procurement_value=_calculate_total_procurement_value(
            simulation_parameters
        ),
    )


def _calculate_supplier_performances(
    simulation_parameters: SimulationParameters,
) -> List[ProcurementMetrics.SupplierPerformance]:
    performances = []
    for supplier in simulation_parameters.suppliers:
        planned_cost = int(supplier.cost)
        actual_cost = int(supplier.cost)

        if supplier.product_quality > 0.9:
            projected_defect = random.uniform(0.0, 0.01)
        elif supplier.product_quality > 0.75:
            projected_defect = random.uniform(0.01, 0.05)
        else:
            projected_defect = random.uniform(0.05, 0.15)

        if supplier.delivery_period_days > 14:
            actual_cost = int(planned_cost * 1.2)
        elif supplier.delivery_period_days > 7:
            actual_cost = int(planned_cost * 1.05)

        performances.append(
            ProcurementMetrics.SupplierPerformance(
                supplier_id=supplier.supplier_id,
                delivered_quantity=_safe_int(
                    getattr(supplier, "delivery_period_days", 0), 0
                ),
                projected_defect_rate=projected_defect,
                planned_reliability=supplier.reliability,
                actual_reliability=supplier.reliability,
                planned_cost=planned_cost,
                actual_cost=actual_cost,
                actual_defect_count=int(projected_defect * 100),
            )
        )

    return performances


def _calculate_total_procurement_value(
    simulation_parameters: SimulationParameters,
) -> int:
    performances = _calculate_supplier_performances(simulation_parameters)
    return sum(int(perf.actual_cost) for perf in performances)


def _calculate_fill_level(warehouse: Warehouse) -> float:
    if warehouse.size == 0:
        return 0.0
    return int(warehouse.loading) / int(warehouse.size)


def _calculate_current_load(warehouse: Warehouse) -> int:
    return int(warehouse.loading)


def _calculate_max_capacity(warehouse: Warehouse) -> int:
    return int(warehouse.size)


def _calculate_material_levels(warehouse: Warehouse) -> Dict[str, int]:
    return {k: int(v) for k, v in warehouse.materials.items()}


def _calculate_load_over_time(warehouse: Warehouse) -> List[int]:
    # Линейный рост загрузки для демонстрации графика медианной загрузки.
    loading = int(warehouse.loading)
    return [max(0, loading - step * 2) for step in range(5)] + [
        loading + step * 2 for step in range(5)
    ]


def _calculate_max_capacity_over_time(warehouse: Warehouse) -> List[int]:
    capacity = int(warehouse.size)
    return [capacity for _ in range(10)]


def _calculate_product_warehouse_metrics(
    simulation_parameters: SimulationParameters,
) -> WarehouseMetrics:
    return WarehouseMetrics(
        fill_level=_calculate_fill_level(simulation_parameters.product_warehouse),
        current_load=_calculate_current_load(simulation_parameters.product_warehouse),
        max_capacity=_calculate_max_capacity(simulation_parameters.product_warehouse),
        material_levels=_calculate_material_levels(
            simulation_parameters.product_warehouse
        ),
        load_over_time=_calculate_load_over_time(
            simulation_parameters.product_warehouse
        ),
        max_capacity_over_time=_calculate_max_capacity_over_time(
            simulation_parameters.product_warehouse
        ),
    )


def _calculate_materials_warehouse_metrics(
    simulation_parameters: SimulationParameters,
) -> WarehouseMetrics:
    return WarehouseMetrics(
        fill_level=_calculate_fill_level(simulation_parameters.materials_warehouse),
        current_load=_calculate_current_load(simulation_parameters.materials_warehouse),
        max_capacity=_calculate_max_capacity(simulation_parameters.materials_warehouse),
        material_levels=_calculate_material_levels(
            simulation_parameters.materials_warehouse
        ),
        load_over_time=_calculate_load_over_time(
            simulation_parameters.materials_warehouse
        ),
        max_capacity_over_time=_calculate_max_capacity_over_time(
            simulation_parameters.materials_warehouse
        ),
    )
