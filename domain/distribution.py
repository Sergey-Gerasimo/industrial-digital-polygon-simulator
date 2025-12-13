"""Сущности для распределения производственного плана по рабочим местам."""

from enum import Enum


class DistributionStrategy(int, Enum):
    """Стратегия распределения производственного плана."""

    DISTRIBUTION_STRATEGY_UNSPECIFIED = 0
    DISTRIBUTION_STRATEGY_BALANCED = 1  # равномерное распределение
    DISTRIBUTION_STRATEGY_EFFICIENT = 2  # по эффективности
    DISTRIBUTION_STRATEGY_CUSTOM = 3  # ручное распределение
    DISTRIBUTION_STRATEGY_PRIORITY_BASED = 4  # по приоритету
