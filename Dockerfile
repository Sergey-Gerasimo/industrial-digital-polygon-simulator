FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt update -y && \
    apt install -y python3-dev \
    gcc \
    musl-dev \
    protobuf-compiler

RUN pip install --upgrade pip
RUN pip install poetry

RUN poetry config virtualenvs.create false

# Копируем только файлы зависимостей для кэширования
COPY pyproject.toml poetry.lock* /app/

# Устанавливаем зависимости (этот слой будет кэшироваться)
# Если poetry.lock устарел или отсутствует, обновляем его автоматически
RUN poetry install --no-root --no-interaction --no-ansi || \
    (echo "Lock file outdated or missing, updating..." && \
    poetry lock && \
    poetry install --no-root --no-interaction --no-ansi)

# Копируем proto файлы и генерируем код (отдельный слой для лучшего кэширования)
COPY simulator.proto /app/
RUN mkdir -p grpc_generated && \
    pip install grpcio-tools && \
    python -m grpc_tools.protoc \
    -I. \
    --python_out=./grpc_generated \
    --grpc_python_out=./grpc_generated \
    --pyi_out=./grpc_generated \
    simulator.proto && \
    if [ -f "grpc_generated/simulator_pb2_grpc.py" ]; then \
    sed -i 's/import simulator_pb2/from . import simulator_pb2/' grpc_generated/simulator_pb2_grpc.py; \
    fi

# Копируем остальной код
# Используем ARG для инвалидации кэша при изменении кода
ARG BUILD_DATE
ARG COMMIT_SHA
# Добавляем метаданные для отслеживания версии
LABEL org.opencontainers.image.created="${BUILD_DATE}" \
    org.opencontainers.image.revision="${COMMIT_SHA}"

# Копируем код (используем COMMIT_SHA в команде для инвалидации кэша)
# Если COMMIT_SHA изменился, этот слой не будет взят из кэша
RUN echo "Building for commit: ${COMMIT_SHA:-unknown}" && \
    echo "Build date: ${BUILD_DATE:-unknown}"

COPY . /app/

RUN mkdir -p logs

# Проверяем структуру проекта
RUN echo "Project structure:" && find . -name "*.py" -type f | head -20

# Порт gRPC сервера
EXPOSE 50051

# Запускаем приложение
CMD ["python", "main.py"]