from enum import Enum
from typing import List, Optional, Union, Dict, TYPE_CHECKING
from uuid import UUID, uuid4
from dataclasses import dataclass, field, replace
import random

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
        """Выполняет одну симуляцию (run_simulation).

        Логика:
        - При создании симуляции: 1 параметр (step=1), 0 результатов
        - После 1-го запуска: 2 параметра (step 1, 2), 1 результат (step 1)
        - После 2-го запуска: 3 параметра (step 1, 2, 3), 2 результата (step 1, 2)
        - После 3-го запуска: 4 параметра (step 1, 2, 3, 4), 3 результата (step 1, 2, 3)
        - После 4-го запуска: 4 параметра (не создаем новый), 4 результата (step 1, 2, 3, 4)
        - После 5-го запуска: выбрасывается ValueError

        Максимальное количество шагов - 4 (1, 2, 3, 4). Нумерация начинается с 1.

        Raises:
            ValueError: если достигнуто максимальное количество шагов (4) или
                       если нет параметров для выполнения симуляции.
        """
        if not self.parameters:
            raise ValueError("У симуляции нет параметров для выполнения")

        # Фильтруем только результаты с валидным step (игнорируем пустые)
        non_empty_results = [
            r for r in self.results if hasattr(r, "step") and r.step > 0
        ]

        # Проверяем максимальный step результатов перед определением следующего шага
        if non_empty_results:
            max_result_step = max(result.step for result in non_empty_results)
            if max_result_step >= 4:
                raise ValueError(
                    "Максимальное количество шагов симуляции (4) уже достигнуто. "
                    "Дальнейшие запуски невозможны."
                )

        # Определяем следующий step для результата на основе непустых результатов
        next_result_step = len(non_empty_results) + 1

        # Максимальный шаг - 4
        if next_result_step > 4:
            raise ValueError(
                "Максимальное количество шагов симуляции (4) уже достигнуто. "
                "Дальнейшие запуски невозможны."
            )

        # Находим последние параметры (с максимальным step) для расчета результатов
        current_params = max(self.parameters, key=lambda p: p.step)

        # Проверяем, не существует ли уже результат для этого шага
        # Если существует, не создаем новый (предотвращаем дубликаты)
        if any(
            hasattr(result, "step") and result.step == next_result_step
            for result in self.results
        ):
            return

        # Рассчитываем результаты на основе параметров (пока просто похожие на правду данные)
        # Прибыль = капитал * коэффициент (базовая логика)
        base_profit = current_params.capital // 10  # 10% от капитала
        base_cost = current_params.capital // 20  # 5% от капитала

        # Учитываем количество тендеров
        tender_bonus = len(current_params.tenders) * 10000
        profit = base_profit + tender_bonus
        cost = base_cost

        # Рассчитываем рентабельность
        profitability = (profit - cost) / cost if cost > 0 else 0.0

        # Создаем метрики склада на основе текущих складов
        materials_warehouse_metrics = WarehouseMetrics(
            fill_level=(
                current_params.materials_warehouse.loading
                / current_params.materials_warehouse.size
                if current_params.materials_warehouse.size > 0
                else 0.0
            ),
            current_load=current_params.materials_warehouse.loading,
            max_capacity=current_params.materials_warehouse.size,
            material_levels=dict(current_params.materials_warehouse.materials),
            load_over_time=[current_params.materials_warehouse.loading],
            max_capacity_over_time=[current_params.materials_warehouse.size],
        )

        product_warehouse_metrics = WarehouseMetrics(
            fill_level=(
                current_params.product_warehouse.loading
                / current_params.product_warehouse.size
                if current_params.product_warehouse.size > 0
                else 0.0
            ),
            current_load=current_params.product_warehouse.loading,
            max_capacity=current_params.product_warehouse.size,
            material_levels=dict(current_params.product_warehouse.materials),
            load_over_time=[current_params.product_warehouse.loading],
            max_capacity_over_time=[current_params.product_warehouse.size],
        )

        # Создаем метрики завода
        factory_metrics = FactoryMetrics(
            profitability=profitability,
            on_time_delivery_rate=0.85,  # Базовое значение
            oee=0.75,  # Базовое значение
            warehouse_metrics={
                "materials": materials_warehouse_metrics,
                "products": product_warehouse_metrics,
            },
            total_procurement_cost=cost,
            defect_rate=0.02,  # 2% брака
        )

        # Создаем метрики производства
        monthly_productivity = []
        months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь"]
        total_units = 0
        for month in months:
            units = random.randint(50, 200)
            monthly_productivity.append(
                ProductionMetrics.MonthlyProductivity(month=month, units_produced=units)
            )
            total_units += units

        # Средняя загрузка оборудования (на основе количества рабочих мест)
        equipment_count = sum(
            1 for wp in current_params.processes.workplaces if wp.equipment is not None
        )
        avg_utilization = (
            min(0.85, equipment_count * 0.1)
            if equipment_count > 0
            else random.uniform(0.5, 0.8)
        )

        production_metrics = ProductionMetrics(
            monthly_productivity=monthly_productivity,
            average_equipment_utilization=avg_utilization,
            wip_count=random.randint(10, 50),  # Work In Progress
            finished_goods_count=product_warehouse_metrics.current_load,
            material_reserves=dict(current_params.materials_warehouse.materials),
        )

        # Создаем метрики качества
        # Средний процент дефектов из поставщиков или случайный
        avg_defect_rate = (
            sum(s.product_quality for s in current_params.suppliers)
            / len(current_params.suppliers)
            if current_params.suppliers
            else 0.02
        )
        # Инвертируем качество в процент дефектов (ниже качество = больше дефектов)
        defect_percentage = (
            max(0.0, (1.0 - avg_defect_rate) * 100)
            if avg_defect_rate > 0
            else random.uniform(1.0, 5.0)
        )
        good_output_percentage = 100.0 - defect_percentage

        # Причины дефектов (случайные)
        defect_causes = []
        causes = ["Некачественное сырье", "Ошибка оборудования", "Человеческий фактор"]
        remaining_percentage = defect_percentage
        for i, cause in enumerate(causes):
            if i == len(causes) - 1:
                count = int(remaining_percentage * 10)
                percentage = remaining_percentage
            else:
                percentage = random.uniform(0.2, remaining_percentage * 0.5)
                count = int(percentage * 10)
                remaining_percentage -= percentage
            defect_causes.append(
                QualityMetrics.DefectCause(
                    cause=cause, count=count, percentage=percentage
                )
            )

        avg_material_quality = (
            sum(s.product_quality for s in current_params.suppliers)
            / len(current_params.suppliers)
            if current_params.suppliers
            else random.uniform(0.85, 0.95)
        )

        avg_supplier_failure = (
            sum(1.0 - s.reliability for s in current_params.suppliers)
            / len(current_params.suppliers)
            if current_params.suppliers
            else random.uniform(0.05, 0.15)
        )

        procurement_volume = sum(
            row.planned_quantity
            for row in current_params.production_schedule.rows
            if hasattr(row, "planned_quantity")
        )

        quality_metrics = QualityMetrics(
            defect_percentage=defect_percentage,
            good_output_percentage=good_output_percentage,
            defect_causes=defect_causes,
            average_material_quality=avg_material_quality,
            average_supplier_failure_probability=avg_supplier_failure,
            procurement_volume=(
                procurement_volume
                if procurement_volume > 0
                else random.randint(100, 1000)
            ),
        )

        # Создаем инженерные метрики
        operation_timings = []
        # Берем данные из процессов, если есть рабочие места
        if current_params.processes.workplaces:
            for wp in current_params.processes.workplaces[:5]:  # Ограничим 5 операциями
                operation_timings.append(
                    EngineeringMetrics.OperationTiming(
                        operation_name=wp.workplace_name
                        or f"Операция {wp.workplace_id}",
                        cycle_time=random.randint(10, 60),
                        takt_time=random.randint(5, 30),
                        timing_cost=random.randint(1000, 5000),
                    )
                )
        else:
            # Случайные операции
            for i in range(3):
                operation_timings.append(
                    EngineeringMetrics.OperationTiming(
                        operation_name=f"Операция {i+1}",
                        cycle_time=random.randint(10, 60),
                        takt_time=random.randint(5, 30),
                        timing_cost=random.randint(1000, 5000),
                    )
                )

        downtime_causes = ["Профилактика", "Поломка", "Переналадка"]
        downtime_records = []
        for cause in downtime_causes:
            total_minutes = random.randint(60, 480)
            downtime_records.append(
                EngineeringMetrics.DowntimeRecord(
                    cause=cause,
                    total_minutes=total_minutes,
                    average_per_shift=total_minutes / 3.0,
                )
            )

        defect_analysis = []
        defect_types = ["Тип A", "Тип B", "Тип C"]
        cumulative = 0.0
        remaining_defect = defect_percentage
        for i, defect_type in enumerate(defect_types):
            if i == len(defect_types) - 1:
                percentage = remaining_defect
                count = int(percentage * 10)
            else:
                percentage = random.uniform(0.1, remaining_defect * 0.4)
                count = int(percentage * 10)
                remaining_defect -= percentage
            cumulative += percentage
            defect_analysis.append(
                EngineeringMetrics.DefectAnalysis(
                    defect_type=defect_type,
                    count=count,
                    percentage=percentage,
                    cumulative_percentage=cumulative,
                )
            )

        engineering_metrics = EngineeringMetrics(
            operation_timings=operation_timings,
            downtime_records=downtime_records,
            defect_analysis=defect_analysis,
        )

        # Создаем коммерческие метрики
        # Годовые доходы (случайные)
        yearly_revenues = []
        current_year = 2024
        for i in range(3):
            yearly_revenues.append(
                CommercialMetrics.YearlyRevenue(
                    year=current_year - 2 + i,
                    revenue=random.randint(1000000, 5000000),
                )
            )

        # План выручки по тендерам
        tender_revenue_plan = (
            sum(
                row.planned_quantity * 1000
                for row in current_params.production_schedule.rows
                if hasattr(row, "planned_quantity")
            )
            if hasattr(current_params.production_schedule, "rows")
            else random.randint(500000, 2000000)
        )

        # График тендеров
        tender_graph = []
        for tender in current_params.tenders[:5]:  # Ограничим 5 тендерами
            tender_graph.append(
                CommercialMetrics.TenderGraphPoint(
                    strategy=current_params.sales_strategy.value,
                    unit_size=str(tender.quantity_of_products),
                    is_mastered=random.choice([True, False]),
                )
            )

        # Прибыльность проектов
        project_profitabilities = []
        for i, tender in enumerate(current_params.tenders[:3]):
            project_profitabilities.append(
                CommercialMetrics.ProjectProfitability(
                    project_name=tender.tender_id or f"Проект {i+1}",
                    profitability=random.uniform(0.1, 0.3),
                )
            )

        sales_forecast = {
            "Q1": random.uniform(0.8, 1.2),
            "Q2": random.uniform(0.9, 1.3),
            "Q3": random.uniform(0.85, 1.25),
            "Q4": random.uniform(0.95, 1.35),
        }

        strategy_costs = {
            current_params.sales_strategy.value: cost,
        }

        commercial_metrics = CommercialMetrics(
            yearly_revenues=yearly_revenues,
            tender_revenue_plan=tender_revenue_plan,
            total_payments=cost,
            total_receipts=profit,
            sales_forecast=sales_forecast,
            strategy_costs=strategy_costs,
            tender_graph=tender_graph,
            project_profitabilities=project_profitabilities,
            on_time_completed_orders=random.randint(5, 15),
        )

        # Создаем метрики закупок
        supplier_performances = []
        all_suppliers = current_params.suppliers + current_params.backup_suppliers

        for supplier in all_suppliers:
            delivered_quantity = random.randint(100, 1000)
            projected_defect_rate = (
                (1.0 - supplier.product_quality) * 100
                if supplier.product_quality > 0
                else random.uniform(1.0, 5.0)
            )
            planned_reliability = supplier.reliability
            actual_reliability = planned_reliability + random.uniform(-0.1, 0.1)
            actual_reliability = max(0.0, min(1.0, actual_reliability))
            planned_cost = supplier.cost * delivered_quantity
            actual_cost = planned_cost * random.uniform(0.95, 1.05)
            actual_defect_count = int(
                delivered_quantity * projected_defect_rate / 100.0
            )

            supplier_performances.append(
                ProcurementMetrics.SupplierPerformance(
                    supplier_id=supplier.supplier_id,
                    delivered_quantity=delivered_quantity,
                    projected_defect_rate=projected_defect_rate,
                    planned_reliability=planned_reliability,
                    actual_reliability=actual_reliability,
                    planned_cost=int(planned_cost),
                    actual_cost=int(actual_cost),
                    actual_defect_count=actual_defect_count,
                )
            )

        # Если нет поставщиков, создадим один случайный
        if not supplier_performances:
            supplier_performances.append(
                ProcurementMetrics.SupplierPerformance(
                    supplier_id="supplier_1",
                    delivered_quantity=random.randint(100, 1000),
                    projected_defect_rate=random.uniform(1.0, 5.0),
                    planned_reliability=random.uniform(0.8, 0.95),
                    actual_reliability=random.uniform(0.75, 0.98),
                    planned_cost=random.randint(50000, 200000),
                    actual_cost=random.randint(48000, 210000),
                    actual_defect_count=random.randint(5, 25),
                )
            )

        total_procurement_value = sum(sp.actual_cost for sp in supplier_performances)

        procurement_metrics = ProcurementMetrics(
            supplier_performances=supplier_performances,
            total_procurement_value=total_procurement_value,
        )

        # Создаем результаты симуляции для следующего step
        result = SimulationResults(
            profit=profit,
            cost=cost,
            profitability=profitability,
            factory_metrics=factory_metrics,
            production_metrics=production_metrics,
            quality_metrics=quality_metrics,
            engineering_metrics=engineering_metrics,
            commercial_metrics=commercial_metrics,
            procurement_metrics=procurement_metrics,
            step=next_result_step,
        )

        # Добавляем результаты
        self.results.append(result)

        # Определяем следующий step для параметров (текущий максимальный step параметров + 1)
        max_param_step = max(param.step for param in self.parameters)
        next_param_step = max_param_step + 1

        # Создаем новые параметры только если следующий step <= 4
        # На 4-м запуске (когда next_result_step == 4) не создаем новые параметры
        if next_param_step <= 4:
            # Создаем копию текущих параметров для следующего шага
            next_params = SimulationParameters.from_simulation_parameters(
                current_params
            )
            next_params.step = next_param_step
            # Сбрасываем некоторые поля для нового шага (опционально)
            # Можно оставить все как есть или сбросить определенные поля
            self.parameters.append(next_params)

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
