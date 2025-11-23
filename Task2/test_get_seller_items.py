import pytest
import random
from api_client import ApiClient
from test_data import get_valid_item_data, generate_seller_id, get_multiple_items_data


class TestGetSellerItems:
    """Тесты для эндпоинта GET /api/1/:sellerID/item - Получить все объявления пользователя"""

    def setup_method(self):
        self.api_client = ApiClient()

    def test_get_seller_items_success(self):
        """Успешное получение объявлений существующего продавца"""
        # Создаем продавца и несколько его объявлений
        seller_id = generate_seller_id()

        # Создаем 2 объявления для одного продавца
        items_data = []
        for i in range(2):
            data = get_multiple_items_data(seller_id, i + 1)
            create_response = self.api_client.create_item(data)
            assert create_response.status_code == 200
            items_data.append(data)

        # Получаем все объявления продавца
        get_response = self.api_client.get_seller_items(seller_id)
        assert get_response.status_code == 200

        response_data = get_response.json()

        # Проверяем структуру ответа
        assert isinstance(response_data, list)
        assert len(response_data) >= 2  # Может быть больше, если были предыдущие

        # Проверяем, что все объявления принадлежат этому продавцу
        for item in response_data:
            assert item["sellerId"] == seller_id
            required_fields = ["id", "sellerId", "name", "price", "statistics", "createdAt"]
            for field in required_fields:
                assert field in item, f"Missing field '{field}' in response"

    def test_get_seller_items_empty_list(self):
        """Получение объявлений продавца без объявлений"""
        seller_id = generate_seller_id()

        response = self.api_client.get_seller_items(seller_id)
        assert response.status_code == 200

        response_data = response.json()
        assert isinstance(response_data, list)
        # Может быть пустым списком или содержать 0 элементов

    def test_get_seller_items_nonexistent_seller(self):
        """Получение объявлений несуществующего продавца"""
        # Используем случайный ID вне диапазона
        nonexistent_seller_id = random.randint(100000, 111110)  # Ниже минимального

        response = self.api_client.get_seller_items(nonexistent_seller_id)
        # Ожидаем 200 с пустым списком или 404
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            response_data = response.json()
            assert isinstance(response_data, list)

    def test_get_seller_items_boundary_seller_id(self):
        """Проверка граничных значений sellerID"""
        for seller_id in [111111, 999999]:
            response = self.api_client.get_seller_items(seller_id)
            # Должен возвращать 200 (даже если пустой список)
            assert response.status_code == 200
            assert isinstance(response.json(), list)

    def test_get_seller_items_invalid_seller_id_format(self):
        """Попытка получения с невалидным форматом sellerID"""
        invalid_seller_ids = [
            "invalid_string",
            "123abc",
            "@#$%^",
            "",
            " ",
            "123.45",
            "-123456",
            "100000",  # Ниже минимального
            "1000000"  # Выше максимального
        ]

        for invalid_id in invalid_seller_ids:
            response = self.api_client.get_seller_items(invalid_id)
            # Ожидаем ошибку клиента
            assert response.status_code in [400, 404]

    def test_get_seller_items_special_characters(self):
        """Проверка защиты от специальных символов в sellerID"""
        test_cases = [
            "123; DROP TABLE items; --",
            "<script>alert('xss')</script>",
            "../../etc/passwd",
            "123' OR '1'='1"
        ]

        for test_id in test_cases:
            response = self.api_client.get_seller_items(test_id)
            assert response.status_code in [400, 404]

    def test_get_seller_items_response_structure(self):
        """Проверка структуры ответа для непустого списка"""
        seller_id = generate_seller_id()

        # Создаем одно объявление для проверки структуры
        data = get_valid_item_data()
        data["sellerID"] = seller_id
        create_response = self.api_client.create_item(data)
        assert create_response.status_code == 200

        # Получаем объявления продавца
        get_response = self.api_client.get_seller_items(seller_id)
        assert get_response.status_code == 200

        response_data = get_response.json()
        assert isinstance(response_data, list)

        if len(response_data) > 0:
            item = response_data[0]
            # Проверяем типы данных
            assert isinstance(item["id"], str)
            assert isinstance(item["sellerId"], int)
            assert isinstance(item["name"], str)
            assert isinstance(item["price"], int)
            assert isinstance(item["createdAt"], str)
            assert isinstance(item["statistics"], dict)

            # Проверяем статистику
            stats = item["statistics"]
            assert isinstance(stats["likes"], int)
            assert isinstance(stats["viewCount"], int)
            assert isinstance(stats["contacts"], int)

    def test_get_seller_items_data_consistency(self):
        """Проверка согласованности данных при создании и получении"""
        seller_id = generate_seller_id()
        original_data = get_valid_item_data()
        original_data["sellerID"] = seller_id

        # Создаем объявление
        create_response = self.api_client.create_item(original_data)
        assert create_response.status_code == 200

        # Получаем объявления продавца
        get_response = self.api_client.get_seller_items(seller_id)
        assert get_response.status_code == 200

        seller_items = get_response.json()
        assert isinstance(seller_items, list)

        # Ищем наше объявление в списке
        found_item = None
        for item in seller_items:
            if item.get("name") == original_data["name"]:
                found_item = item
                break

        if found_item:
            # Проверяем соответствие данных
            assert found_item["sellerId"] == original_data["sellerID"]
            assert found_item["name"] == original_data["name"]
            assert found_item["price"] == original_data["price"]

            # Проверяем статистику
            original_stats = original_data["statistics"]
            found_stats = found_item["statistics"]
            assert found_stats["likes"] == original_stats["likes"]
            assert found_stats["viewCount"] == original_stats["viewCount"]
            assert found_stats["contacts"] == original_stats["contacts"]

    def test_get_seller_items_multiple_sellers(self):
        """Проверка изоляции данных между разными продавцами"""
        seller1_id = generate_seller_id()
        seller2_id = generate_seller_id()

        # Создаем по одному объявлению для каждого продавца
        data1 = get_valid_item_data()
        data1["sellerID"] = seller1_id
        data1["name"] = "Item for Seller 1"

        data2 = get_valid_item_data()
        data2["sellerID"] = seller2_id
        data2["name"] = "Item for Seller 2"

        create_response1 = self.api_client.create_item(data1)
        create_response2 = self.api_client.create_item(data2)
        assert create_response1.status_code == 200
        assert create_response2.status_code == 200

        # Получаем объявления первого продавца
        response1 = self.api_client.get_seller_items(seller1_id)
        assert response1.status_code == 200
        items1 = response1.json()

        # Проверяем, что в списке только объявления первого продавца
        for item in items1:
            assert item["sellerId"] == seller1_id

    def test_get_seller_items_ordering(self):
        """Проверка порядка объявлений в ответе"""
        seller_id = generate_seller_id()

        # Создаем несколько объявлений
        items_count = 3
        for i in range(items_count):
            data = get_multiple_items_data(seller_id, i + 1)
            create_response = self.api_client.create_item(data)
            assert create_response.status_code == 200

        # Получаем объявления
        response = self.api_client.get_seller_items(seller_id)
        assert response.status_code == 200
        items = response.json()

        # Проверяем, что все созданные объявления присутствуют
        # (может быть больше, если были предыдущие)
        assert len(items) >= items_count

        # Можно проверить порядок по createdAt, если он есть
        for i in range(1, len(items)):
            if "createdAt" in items[i - 1] and "createdAt" in items[i]:
                # Проверяем, что createdAt присутствует
                assert items[i - 1]["createdAt"] is not None
                assert items[i]["createdAt"] is not None


class TestGetSellerItemsPerformance:
    """Тесты производительности для эндпоинта GET /api/1/:sellerID/item"""

    def setup_method(self):
        self.api_client = ApiClient()

    def test_get_seller_items_response_time(self):
        """Проверка времени ответа"""
        seller_id = generate_seller_id()

        import time
        start_time = time.time()
        response = self.api_client.get_seller_items(seller_id)
        end_time = time.time()

        assert response.status_code == 200
        response_time = end_time - start_time

        # Операция должна выполняться быстро
        assert response_time < 3, f"Response time too slow: {response_time} seconds"

    def test_get_seller_items_with_many_items(self):
        """Проверка работы с большим количеством объявлений"""
        seller_id = generate_seller_id()

        # Создаем несколько объявлений
        for i in range(5):
            data = get_multiple_items_data(seller_id, i + 1)
            create_response = self.api_client.create_item(data)
            assert create_response.status_code == 200

        # Получаем все объявления
        response = self.api_client.get_seller_items(seller_id)
        assert response.status_code == 200

        items = response.json()
        assert isinstance(items, list)
        assert len(items) >= 5


class TestGetSellerItemsEdgeCases:
    """Тесты граничных случаев для эндпоинта GET /api/1/:sellerID/item"""

    def setup_method(self):
        self.api_client = ApiClient()

    def test_get_seller_items_very_large_seller_id(self):
        """Проверка очень большого sellerID"""
        large_seller_id = 10 ** 10  # Очень большое число
        response = self.api_client.get_seller_items(large_seller_id)
        assert response.status_code in [200, 400, 404]

    def test_get_seller_items_negative_seller_id(self):
        """Проверка отрицательного sellerID"""
        response = self.api_client.get_seller_items(-123456)
        assert response.status_code in [400, 404]

    def test_get_seller_items_zero_seller_id(self):
        """Проверка sellerID = 0"""
        response = self.api_client.get_seller_items(0)
        assert response.status_code in [200, 400, 404]

    def test_get_seller_items_float_seller_id(self):
        """Проверка дробного sellerID"""
        response = self.api_client.get_seller_items(123456.78)
        # Должен преобразоваться в int или вернуть ошибку
        assert response.status_code in [200, 400, 404]

    def test_get_seller_items_unicode_seller_id(self):
        """Проверка unicode символов в sellerID"""
        response = self.api_client.get_seller_items("🐸🐸🐸")
        assert response.status_code in [400, 404]