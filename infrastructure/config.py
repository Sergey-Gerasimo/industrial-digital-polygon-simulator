from typing import Optional, Dict, Any
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

import sys
import logging
from pathlib import Path
from loguru import logger


class GRPCSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="")
    host: str = Field(default="0.0.0.0", alias="GRPC_HOST")
    simulation_port: str = Field(default="50051", alias="GRPC_SIMULATION_PORT")
    db_manager_port: str = Field(default="50052", alias="GRPC_DB_MANAGER_PORT")
    max_workers: int = Field(default=10, alias="GRPC_MAX_WORKERS")
    max_message_length: int = Field(
        default=50 * 1024 * 1024, alias="GRPC_MAX_MESSAGE_LENGTH"
    )


class LogSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="", case_sensitive=False)

    debug: bool = Field(default=True, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(default="json", alias="LOG_FORMAT")
    enable_grpc_access_log: bool = Field(default=True, alias="ENABLE_GRPC_ACCESS_LOG")


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="REDIS_")

    host: str = Field(default="localhost", alias="REDIS_HOST")
    port: int = Field(default=6379, alias="REDIS_PORT")
    db: int = Field(default=0, alias="REDIS_DB")
    max_connections: int = Field(default=10, alias="REDIS_MAX_CONNECTIONS")
    decode_responses: bool = Field(default=True, alias="REDIS_DECODE_RESPONSES")
    password: Optional[str] = Field(default=None, alias="REDIS_PASSWORD")
    default_timeout: int = Field(default=300, alias="REDIS_DEFAULT_TIMEOUT")

    @property
    def url(self) -> str:
        """Генерирует URL для подключения к Redis.

        Returns:
            str: Redis URL в формате redis://[user:password@]host:port/db

        Example:
            >>> redis = RedisSettings()
            >>> print(redis.url)
            'redis://localhost:6379/0'
        """
        if self.password is None:
            return f"redis://{self.host}:{self.port}/{self.db}"

        return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="")
    db: str = Field(default="postgres", alias="POSTGRES_DB")
    user: str = Field(default="postgres", alias="POSTGRES_USER")
    password: str = Field(default="password", alias="POSTGRES_PASSWORD")
    host: str = Field(default="localhost", alias="POSTGRES_HOST")
    port: int = Field(default=5432, alias="POSTGRES_PORT")
    pool_size: int = Field(default=10, alias="POSTGRES_POOL_SIZE")
    max_overflow: int = Field(default=20, alias="POSTGRES_MAX_OVERFLOW")
    echo: bool = Field(default=False, alias="POSTGRES_ECHO")

    @property
    def url_asyncpg(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"

    @property
    def url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


class Settings(BaseSettings):
    postgres: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    grpc: GRPCSettings = Field(default_factory=GRPCSettings)
    log: LogSettings = Field(default_factory=LogSettings)


class LoguruInterceptHandler(logging.Handler):
    """Перехватывает логи стандартного logging и перенаправляет в loguru"""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


class GRPCLoggerConfig:
    """Конфигурация логгера для gRPC приложений"""

    # Форматы логов
    CONSOLE_FORMAT = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    JSON_FORMAT = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | "
        "{name}:{function}:{line} | {message}"
    )

    # gRPC-specific форматы
    GRPC_CONSOLE_FORMAT = (
        "<magenta>{time:YYYY-MM-DD HH:mm:ss.SSS}</magenta> | "
        "<level>{level: <8}</level> | "
        "<cyan>gRPC</cyan> | "
        "<level>{message}</level>"
    )

    GRPC_ACCESS_FORMAT = (
        "<blue>{time:YYYY-MM-DD HH:mm:ss.SSS}</blue> | "
        "gRPC | {extra[method]} | {extra[service]} | "
        "duration: {extra[duration]:.3f}s | status: {extra[status]}"
    )

    @staticmethod
    def _ensure_logs_directory() -> None:
        """Создает директорию для логов если не существует"""
        Path("logs").mkdir(exist_ok=True)

    @staticmethod
    def _configure_console_logging(level: str, debug: bool) -> None:
        """Настраивает консольный вывод"""
        logger.add(
            sys.stderr,
            format=GRPCLoggerConfig.CONSOLE_FORMAT,
            level=level,
            colorize=True,
            backtrace=debug,
            diagnose=debug,
            filter=lambda record: "grpc" not in record["name"].lower(),
        )

        # Отдельный обработчик для gRPC логов в консоли
        logger.add(
            sys.stderr,
            format=GRPCLoggerConfig.GRPC_CONSOLE_FORMAT,
            level=level,
            colorize=True,
            backtrace=debug,
            diagnose=debug,
            filter=lambda record: "grpc" in record["name"].lower(),
        )

    @staticmethod
    def _configure_file_logging(level: str, debug: bool, log_format: str) -> None:
        """Настраивает файловый вывод"""
        if not debug:
            file_format = (
                GRPCLoggerConfig.JSON_FORMAT
                if log_format == "json"
                else GRPCLoggerConfig.CONSOLE_FORMAT
            )

            # Основной лог файл
            logger.add(
                "logs/app.log",
                rotation="50 MB",
                retention="30 days",
                compression="gz",
                format=file_format,
                level=level,
                serialize=(log_format == "json"),
                backtrace=True,
                diagnose=False,
            )

        # Лог ошибок
        logger.add(
            "logs/error.log",
            rotation="10 MB",
            retention="15 days",
            compression="gz",
            level="ERROR",
            format=GRPCLoggerConfig.JSON_FORMAT,
            serialize=True,
            backtrace=True,
            diagnose=True,
        )

        # gRPC access log
        logger.add(
            "logs/grpc_access.log",
            rotation="20 MB",
            retention="7 days",
            compression="gz",
            format=GRPCLoggerConfig.JSON_FORMAT,
            level="INFO",
            serialize=True,
            filter=lambda record: "grpc.access" in record["name"].lower(),
        )

        console_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{module}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )

        logger.add(
            sys.stderr,
            format=console_format,
            level="DEBUG",
            colorize=True,
            serialize=False,  # Не сериализуем в JSON для консоли
            backtrace=True,
            diagnose=debug,
        )

    @staticmethod
    def _configure_intercept_handler(level: str) -> None:
        """Настраивает перехват стандартного logging"""
        intercept_handler = LoguruInterceptHandler()

        # Корневой логгер
        logging.root.handlers = [intercept_handler]
        logging.root.setLevel(getattr(logging, level))

        # gRPC-specific логгеры
        grpc_loggers = [
            "grpc",
            "grpc.aio",
            "grpc_channelz",
            "grpc.reflection",
        ]

        # Общие логгеры
        common_loggers = [
            "uvicorn",
            "uvicorn.access",
            "uvicorn.error",
            "fastapi",
            "sqlalchemy",
            "aiosqlite",
        ]

        # Настраиваем все логгеры
        for logger_name in grpc_loggers + common_loggers:
            logging_logger = logging.getLogger(logger_name)
            logging_logger.handlers = [intercept_handler]
            logging_logger.setLevel(getattr(logging, level))
            logging_logger.propagate = False

    @staticmethod
    def configure(
        log_level: str = "INFO",
        debug: bool = False,
        log_format: str = "json",
        enable_grpc_access_log: bool = True,
    ) -> None:
        """
        Конфигурирует логгер для gRPC приложения

        Args:
            log_level: Уровень логирования (DEBUG, INFO, WARNING, ERROR)
            debug: Режим отладки
            log_format: Формат логов (json, console)
            enable_grpc_access_log: Включить логирование gRPC запросов
        """
        # Удаляем стандартные обработчики
        logger.remove()

        # Создаем директорию для логов
        GRPCLoggerConfig._ensure_logs_directory()

        # Настраиваем вывод
        GRPCLoggerConfig._configure_console_logging(log_level, debug)
        GRPCLoggerConfig._configure_file_logging(log_level, debug, log_format)
        GRPCLoggerConfig._configure_intercept_handler(log_level)

        # Логируем успешную конфигурацию
        logger.info(
            "gRPC logger configured",
            extra={
                "level": log_level,
                "debug": debug,
                "format": log_format,
                "grpc_access_log": enable_grpc_access_log,
            },
        )


# Утилиты для gRPC логирования
class GRPCLoggingUtils:
    """Утилиты для логирования gRPC событий"""

    @staticmethod
    def log_grpc_request(
        method: str,
        service: str,
        duration: float,
        status: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Логирует gRPC запрос"""
        extra_data = {
            "method": method,
            "service": service,
            "duration": duration,
            "status": status,
            "type": "grpc_request",
        }

        if metadata:
            extra_data["metadata"] = metadata

        logger.bind(**extra_data).info("gRPC request completed")

    @staticmethod
    def log_grpc_error(
        method: str, service: str, error: str, details: Optional[str] = None
    ) -> None:
        """Логирует gRPC ошибку"""
        extra_data = {
            "method": method,
            "service": service,
            "error": error,
            "type": "grpc_error",
        }

        if details:
            extra_data["details"] = details

        logger.bind(**extra_data).error("gRPC error occurred")

    @staticmethod
    def get_grpc_logger(service_name: str):
        """Возвращает логгер для конкретного gRPC сервиса"""
        return logger.bind(service=service_name, type="grpc_service")


app_logger = logger
app_settings = Settings()
