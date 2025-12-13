"""Enum-ы для справочных данных."""
from enum import Enum


class SalesStrategy(str, Enum):
    """Стратегии продаж."""
    LOW_PRICES = "Низкие цены"
    DIFFERENTIATION = "Дифференциация"
    PREMIUM = "Премиум"
    FOCUS = "Фокусировка"


class DefectPolicy(str, Enum):
    """Политики работы с браком."""
    DISPOSE = "Утилизировать"
    REWORK = "Переделать"
    SELL_AS_IS = "Продать как есть"
    RETURN_TO_SUPPLIER = "Вернуть поставщику"


class Certification(str, Enum):
    """Сертификации."""
    GOST_R = "ГОСТ Р"
    ISO_9001 = "ISO 9001"
    EUROSTANDARD_CE = "Евростандарт CE"
    ISO_14001 = "ISO 14001"


class Improvement(str, Enum):
    """LEAN улучшения."""
    SYSTEM_5S = "5S система"
    KANBAN = "Канбан"
    TPM = "Всеобщее обслуживание оборудования"
    SUGGESTION_SYSTEM = "Система подачи предложений"


class CompanyType(str, Enum):
    """Типы компаний."""
    GOVERNMENT = "Государственная"
    PRIVATE = "Частная"
    FOREIGN = "Иностранная"


class VehicleType(str, Enum):
    """Типы транспорта."""
    VAN = "Грузовой фургон"
    TRUCK = "Фура"
    ELECTRIC = "Электрокар"
    NONE = "None"


class UnitSize(str, Enum):
    """Размеры юнитов."""
    U1 = "1U"
    U2 = "2U"
    U3 = "3U"
    U6 = "6U"


class ProductModel(str, Enum):
    """Модели продукции."""
    COMMUNICATION_SATELLITE = "Спутник связи"
    SCIENCE_SATELLITE = "Научный спутник"
    NAVIGATION_SATELLITE = "Навигационный спутник"


class PaymentForm(str, Enum):
    """Формы оплаты."""
    FULL_ADVANCE = "100% аванс"
    PARTIAL_ADVANCE = "50% аванс, 50% по факту"
    ON_DELIVERY = "100% по факту"


class WorkplaceType(str, Enum):
    """Типы рабочих мест."""
    ASSEMBLY_AREA = "Слесарный участок"
    ASSEMBLY_LINE = "Сборочный участок"
    QUALITY_CONTROL = "Контроль качества"
    MATERIAL_WAREHOUSE = "Склад материалов"

