#!/bin/bash

echo "Запуск currency-manager (порт 5001)..."
python currency-manager.py &   # Запускает сервис в фоне (& — самое важное)
sleep 1     # Небольшая пауза, чтобы сервис успел стартовать

echo "Запуск data-manager (порт 5002)..."
python data_manager.py &
sleep 1

echo "Запуск gateway (порт 5000)..."
python gateway.py &

echo ""
echo "Все сервисы запущены!"
echo "Frontend: http://localhost:5000"
echo "Чтобы остановить: pkill -f 'currency-manager.py|data_manager.py|gateway.py'"  # Команда, которой потом можно убить все три процесса сразу