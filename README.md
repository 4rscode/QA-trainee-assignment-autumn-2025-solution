# Автотесты для API микросервиса объявлений

## Описание
Автоматизированные тесты для REST API микросервиса управления объявлениями. Тесты покрывают все основные эндпоинты API версий 1 и 2.

## Требования
- Python 3.7 или выше
- Доступ к интернету для установки зависимостей

## Быстрый старт

### 1. Клонирование репозитория
```bash
git clone https://github.com/your-username/QA-trainee-assignment-autumn-2025-solution.git
cd QA-trainee-assignment-autumn-2025-solution/Task2
```

### 2. Создание виртуального окружения
```bash
python -m venv .venv
```

### 3. Активация виртуального окружения
```bash
# Для Windows:
.venv\Scripts\activate

# Для Linux/MacOS:
source .venv/bin/activate
```

### 4. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 5. Запуск тестов
```bash
pytest -v
```

## Подробная инструкция

### Проверка установки Python
Убедитесь, что Python установлен:
```bash
python --version
```
Если Python не установлен, скачайте его с [официального сайта](https://www.python.org/downloads/) и во время установки отметьте галочку "Add Python to PATH".

### Установка зависимостей
Все необходимые библиотеки указаны в файле `requirements.txt`:
```bash
pip install -r requirements.txt
```

Если команда не работает, попробуйте:
```bash
pip3 install -r requirements.txt
```

### Запуск тестов
После установки зависимостей запустите тесты:

**Все тесты:**
```bash
pytest -v
```

**Конкретные группы тестов:**
```bash
# Тесты создания объявлений
pytest test_create_item.py -v

# Тесты получения объявлений
pytest test_get_item.py -v

# Тесты статистики
pytest test_statistics.py -v
```

**С генерацией отчета:**
```bash
pytest -v --html=report.html
```

## Структура проекта
```
Task2/
├── README.md                 # Эта инструкция
├── TESTCASES.md              # Тест-кейсы
├── BUGS.md                   # Баг-репорты
├── requirements.txt          # Зависимости
├── api_client.py             # Клиент для работы с API
├── test_data.py              # Генератор тестовых данных
├── test_create_item.py       # Тесты создания объявлений
├── test_get_item.py          # Тесты получения по ID
├── test_get_seller_items.py  # Тесты получения по продавцу
└── test_statistics.py        # Тесты статистики
```

## Тестируемые эндпоинты

### API v1
- `POST /api/1/item` - Создать объявление
- `GET /api/1/item/{id}` - Получить объявление по ID  
- `GET /api/1/{sellerID}/item` - Получить все объявления продавца
- `GET /api/1/statistic/{id}` - Получить статистику по объявлению

### API v2
- `DELETE /api/2/item/{id}` - Удалить объявление
- `GET /api/2/statistic/{id}` - Получить статистику по объявлению (v2)
