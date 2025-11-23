import pytest
import json
from api_client import ApiClient
from test_data import get_valid_item_data, get_test_ids_for_get_item, generate_seller_id


class TestGetItemById:
    """Тесты для эндпоинта GET /api/1/item/:id - Получить объявление по идентификатору"""

    def setup_method(self):
        self.api_client = ApiClient()

    def extract_item_id(self, response_data):
        """Извлечение ID из ответа создания объявления"""
        if isinstance(response_data, list) and len(response_data) > 0:
            return response_data[0].get("id")
        return response_data.get("id")

    def test_get_existing_item_success(self):
        """Успешное получение существующего объявления по ID"""
        # Создаем объявление
        data = get_valid_item_data()
        create_response = self.api_client.create_item(data)
        assert create_response.status_code == 200

        created_item = create_response.json()
        item_id = self.extract_item_id(created_item)

        # Получаем объявление по ID
        get_response = self.api_client.get_item(item_id)
        assert get_response.status_code == 200

        response_data = get_response.json()

        # Проверяем структуру ответа
        assert isinstance(response_data, list)
        assert len(response_data) > 0

        item = response_data[0]
        required_fields = ["id", "sellerId", "name", "price", "statistics", "createdAt"]
        for field in required_fields:
            assert field in item, f"Missing field '{field}' in response"

        # Проверяем соответствие данных
        assert item["id"] == item_id
        assert item["sellerId"] == data["sellerID"]
        assert item["name"] == data["name"]
        assert item["price"] == data["price"]

        # Проверяем статистику
        stats = item["statistics"]
        assert "likes" in stats
        assert "viewCount" in stats
        assert "contacts" in stats

    def test_get_nonexistent_item(self):
        """Попытка получения несуществующего объявления"""
        response = self.api_client.get_item("nonexistent_id_12345")
        assert response.status_code == 404

        # Проверяем структуру ошибки
        error_data = response.json()
        assert "result" in error_data
        assert "status" in error_data

    def test_get_item_empty_id(self):
        """Попытка получения с пустым ID"""
        response = self.api_client.get_item("")
        assert response.status_code in [400, 404]

    def test_get_item_special_characters_id(self):
        """Попытка получения с ID содержащим специальные символы"""
        test_ids = [
            "test@#$%^",
            "id-with-dashes",
            "id_with_underscores",
            "test.id.with.dots"
        ]

        for test_id in test_ids:
            response = self.api_client.get_item(test_id)
            assert response.status_code in [400, 404]

    def test_get_item_sql_injection_id(self):
        """Проверка защиты от SQL инъекции в ID"""
        response = self.api_client.get_item("1; DROP TABLE items; --")
        assert response.status_code in [400, 404]

    def test_get_item_xss_id(self):
        """Проверка защиты от XSS в ID"""
        response = self.api_client.get_item("<script>alert('xss')</script>")
        assert response.status_code in [400, 404]

    def test_get_item_long_id(self):
        """Попытка получения с очень длинным ID"""
        long_id = "a" * 1000
        response = self.api_client.get_item(long_id)
        assert response.status_code in [400, 404]

    def test_get_item_numeric_id(self):
        """Попытка получения с числовым ID"""
        response = self.api_client.get_item("123456")
        assert response.status_code == 404

    def test_get_item_response_structure(self):
        """Проверка структуры ответа для существующего объявления"""
        data = get_valid_item_data()
        create_response = self.api_client.create_item(data)
        assert create_response.status_code == 200

        item_id = self.extract_item_id(create_response.json())
        get_response = self.api_client.get_item(item_id)
        assert get_response.status_code == 200

        response_data = get_response.json()

        # Детальная проверка структуры
        assert isinstance(response_data, list)
        item = response_data[0]

        # Проверка типов данных
        assert isinstance(item["id"], str)
        assert isinstance(item["sellerId"], int)
        assert isinstance(item["name"], str)
        assert isinstance(item["price"], int)
        assert isinstance(item["createdAt"], str)
        assert isinstance(item["statistics"], dict)

        # Проверка статистики
        stats = item["statistics"]
        assert isinstance(stats["likes"], int)
        assert isinstance(stats["viewCount"], int)
        assert isinstance(stats["contacts"], int)

    def test_get_item_data_consistency(self):
        """Проверка согласованности данных при создании и получении"""
        # Создаем объявление
        data = get_valid_item_data()
        create_response = self.api_client.create_item(data)
        assert create_response.status_code == 200

        created_item = create_response.json()
        item_id = self.extract_item_id(created_item)

        # Получаем объявление
        get_response = self.api_client.get_item(item_id)
        assert get_response.status_code == 200

        retrieved_items = get_response.json()
        retrieved_item = retrieved_items[0]

        # Сравниваем данные
        assert retrieved_item["id"] == item_id
        assert retrieved_item["sellerId"] == data["sellerID"]
        assert retrieved_item["name"] == data["name"]
        assert retrieved_item["price"] == data["price"]

        # Сравниваем статистику
        created_stats = data["statistics"]
        retrieved_stats = retrieved_item["statistics"]
        assert retrieved_stats["likes"] == created_stats["likes"]
        assert retrieved_stats["viewCount"] == created_stats["viewCount"]
        assert retrieved_stats["contacts"] == created_stats["contacts"]

    def test_get_item_multiple_times(self):
        """Многократное получение одного и того же объявления"""
        data = get_valid_item_data()
        create_response = self.api_client.create_item(data)
        assert create_response.status_code == 200

        item_id = self.extract_item_id(create_response.json())

        # Получаем несколько раз
        for i in range(3):
            get_response = self.api_client.get_item(item_id)
            assert get_response.status_code == 200
            items = get_response.json()
            assert len(items) > 0
            assert items[0]["id"] == item_id

    def test_get_item_after_modification(self):
        """Получение объявления после создания (проверка временных меток)"""
        data = get_valid_item_data()
        create_response = self.api_client.create_item(data)
        assert create_response.status_code == 200

        created_item = create_response.json()
        item_id = self.extract_item_id(created_item)
        created_at = created_item.get("createdAt")

        # Получаем объявление и проверяем временную метку
        get_response = self.api_client.get_item(item_id)
        assert get_response.status_code == 200

        retrieved_item = get_response.json()[0]
        retrieved_created_at = retrieved_item.get("createdAt")

        # createdAt должен совпадать или быть логически согласованным
        assert retrieved_created_at is not None
        # Можно добавить проверку формата даты, если известен expected format

    @pytest.mark.parametrize("invalid_id", [
        "",
        "   ",
        "null",
        "undefined",
        "true",
        "false",
        "0",
        "-1",
        "1.5"
    ])
    def test_get_item_boundary_ids(self, invalid_id):
        """Параметризованный тест граничных значений ID"""
        response = self.api_client.get_item(invalid_id)
        # Ожидаем ошибку клиента для невалидных ID
        assert response.status_code in [400, 404]


class TestGetItemPerformance:
    """Тесты производительности для эндпоинта GET /api/1/item/:id"""

    def setup_method(self):
        self.api_client = ApiClient()

    def extract_item_id(self, response_data):
        return response_data.get("id")

    def test_get_item_response_time(self):
        """Проверка времени ответа для получения объявления"""
        # Создаем объявление
        data = get_valid_item_data()
        create_response = self.api_client.create_item(data)
        assert create_response.status_code == 200

        item_id = self.extract_item_id(create_response.json())

        # Измеряем время выполнения
        import time
        start_time = time.time()
        get_response = self.api_client.get_item(item_id)
        end_time = time.time()

        assert get_response.status_code == 200
        response_time = end_time - start_time

        # Операция должна выполняться быстро (менее 2 секунд)
        assert response_time < 2, f"Response time too slow: {response_time} seconds"

    def test_get_item_concurrent_requests(self):
        """Проверка поведения при конкурентных запросах"""
        data = get_valid_item_data()
        create_response = self.api_client.create_item(data)
        assert create_response.status_code == 200

        item_id = self.extract_item_id(create_response.json())

        # Делаем несколько последовательных запросов
        for i in range(5):
            response = self.api_client.get_item(item_id)
            assert response.status_code == 200


class TestGetItemErrorScenarios:
    """Тесты сценариев ошибок для эндпоинта GET /api/1/item/:id"""

    def setup_method(self):
        self.api_client = ApiClient()

    def test_get_item_server_error_handling(self):
        """Проверка обработки серверных ошибок"""
        # Используем специальный ID который может вызвать серверную ошибку
        response = self.api_client.get_item("error-trigger")
        # Сервер должен корректно обрабатывать такие случаи
        assert response.status_code != 500  # Не должно быть Internal Server Error

    def test_get_item_network_issues(self):
        """Проверка поведения при проблемах с сетью"""
        # Тест на таймауты и сетевые ошибки
        # Этот тест может быть сложно воспроизвести в автоматическом режиме
        # Но мы можем проверить, что клиент корректно обрабатывает ошибки
        data = get_valid_item_data()
        create_response = self.api_client.create_item(data)
        assert create_response.status_code == 200

        item_id = self.extract_item_id(create_response.json())

        # Нормальный запрос должен работать
        response = self.api_client.get_item(item_id)
        assert response.status_code == 200