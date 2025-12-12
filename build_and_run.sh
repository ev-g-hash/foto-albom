#!/bin/bash
# Скрипт для локальной сборки и запуска

echo "Собираем Docker образ..."
docker build -t foto-album .

echo "Запускаем контейнер..."
docker run -d \
  --name foto-album-app \
  -p 8000:8000 \
  -v $(pwd)/data:/data \
  foto-album

echo "Приложение запущено на http://localhost:8000"