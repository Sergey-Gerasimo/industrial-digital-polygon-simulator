.PHONY: generate_code clean

# Генерация gRPC кода
generate_code:
	@echo "Генерирую код..."
	python -m grpc_tools.protoc \
		-I. \
		--python_out=./grpc_generated \
		--grpc_python_out=./grpc_generated \
		--pyi_out=./grpc_generated \
		simulator.proto
	@touch grpc_generated/__init__.py
	@echo "Генерация прошла успешно! Файлы в директории grpc_generated/:"
	@ls -la grpc_generated/

# Очистка сгенерированного кода
clean:
	@echo "Очищаю..."
	rm -rf grpc_generated/*
	@echo "Все чисто!"

# Полная перегенерация
regenerate: clean generate_code
	@echo "Заново генерирую код!"
