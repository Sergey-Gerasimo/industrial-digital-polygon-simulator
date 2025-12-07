from enum import Enum
from typing import List, Optional, Union
from uuid import UUID, uuid4
from dataclasses import dataclass, field

from .process_graph import ProcessGraph
from .supplier import Supplier
from .tender import Tender
from .warehouse import Warehouse
from .logist import Logist

from .base_serializabel import RedisSerializable


class SaleStrategest(str, Enum):
    NONE = "none"


class DealingWithDefects(str, Enum):
    NONE = "none"


class ProductImpruvement(str, Enum):
    NONE = "none"


@dataclass
class SimulationParameters(RedisSerializable):
    dealing_with_defects: DealingWithDefects = field(default=SaleStrategest.NONE)
    sales_strategy: SaleStrategest = field(default=SaleStrategest.NONE)

    product_improvemants: List[ProductImpruvement] = field(default_factory=list)

    tenders: List[Tender] = field(default_factory=list)
    process_graph: ProcessGraph = field(default_factory=lambda: ProcessGraph())
    logist: Optional[Logist] = field(default=None)
    suppliers: List[Supplier] = field(default_factory=list)
    backup_suppliers: List[Supplier] = field(default_factory=list)
    material_warehouse: Warehouse = field(
        default_factory=lambda: Warehouse(size=1000, loading=0)
    )
    product_warehouse: Warehouse = field(
        default_factory=lambda: Warehouse(size=1000, loading=0)
    )
    has_certification: bool = field(default=False)

    def set_dealing_with_defects(self, dealing: DealingWithDefects) -> None:
        self.dealing_with_defects = dealing

    def set_sales_strategy(self, stragegy: SaleStrategest) -> None:
        self.sales_strategy = stragegy

    def add_product_inprovement(
        self, improvement: Union[ProductImpruvement, str]
    ) -> None:
        if isinstance(improvement, str):
            improvement = ProductImpruvement(improvement)

        self.product_improvemants.append(improvement)

    def remove_product_impovement(self, impovement: Union[ProductImpruvement, str]):
        if isinstance(improvement, str):
            improvement = ProductImpruvement(improvement)

        self.product_improvemants.remove(improvement)

    def add_tender(self, tender: Tender) -> None:
        self.tenders.append(tender)


@dataclass
class SimulationResults(RedisSerializable):
    profit: int
    cost: int  # затраты
    profitability: float


@dataclass
class Simulation(RedisSerializable):
    capital: int
    step: int

    simulation_id: UUID = field(default_factory=uuid4)
    simulation_results: SimulationResults = field(
        default_factory=lambda: SimulationResults()
    )
    simulation_parameters: SimulationParameters = field(
        default_factory=lambda: SimulationParameters()
    )
