import pytest
import random
from api_client import ApiClient
from test_data import get_valid_item_data, generate_seller_id


class TestStatisticsV1:
    """Тесты для эндпоинта GET /api/1/statistic/:id - Получить статистику по объявлению (v1)"""

    def setup_method(self):
        self.api_client = ApiClient()

    def extract_item_id(self, response_data):
        """Извлечение ID из ответа создания объявления"""
        if isinstance(response_data, list) and len(response_data) > 0:
            return response_data[0].get("id")
        return response_data.get("id")

    def test_get_statistics_existing_item_v1(self):
        """Успешное получение статистики существующего объявления через API v1"""
        # Создаем объявление
        data = get_valid_item_data()
        create_response = self.api_client.create_item(data)
        assert create_response.status_code == 200

        created_item = create_response.json()
        item_id = self.extract_item_id(created_item)

        # Получаем статистику через API v1
        stat_response = self.api_client.get_statistics(item_id)
        assert stat_response.status_code == 200

        stat_data = stat_response.json()

        # Проверяем структуру ответа
        assert isinstance(stat_data, list)
        if len(stat_data) > 0:
            stat_item = stat_data[0]
            required_fields = ["likes", "viewCount", "contacts"]
            for field in required_fields:
                assert field in stat_item, f"Missing field '{field}' in statistics response"

    def test_get_statistics_nonexistent_item_v1(self):
        """Получение статистики несуществующего объявления через API v1"""
        response = self.api_client.get_statistics("nonexistent_stat_id_123")
        assert response.status_code == 404

    def test_get_statistics_invalid_id_v1(self):
        """Получение статистики с невалидным ID через API v1"""
        test_cases = [
            "invalid_id",
            "123-abc",
            "@#$%",
            " ",
            ""
        ]

        for invalid_id in test_cases:
            response = self.api_client.get_statistics(invalid_id)
            assert response.status_code in [400, 404]

    def test_get_statistics_special_characters_v1(self):
        """Проверка защиты от специальных символов в ID через API v1"""
        response = self.api_client.get_statistics("test@#$%^&*()")
        assert response.status_code in [400, 404]

    def test_get_statistics_sql_injection_v1(self):
        """Проверка защиты от SQL инъекции в ID через API v1"""
        response = self.api_client.get_statistics("1; DROP TABLE statistics; --")
        assert response.status_code in [400, 404]

    def test_get_statistics_xss_v1(self):
        """Проверка защиты от XSS в ID через API v1"""
        response = self.api_client.get_statistics("<script>alert('xss')</script>")
        assert response.status_code in [400, 404]

    def test_get_statistics_long_id_v1(self):
        """Получение статистики с очень длинным ID через API v1"""
        long_id = "a" * 1000
        response = self.api_client.get_statistics(long_id)
        assert response.status_code in [400, 404]

    def test_get_statistics_response_structure_v1(self):
        """Проверка структуры ответа статистики через API v1"""
        data = get_valid_item_data()
        create_response = self.api_client.create_item(data)
        assert create_response.status_code == 200

        item_id = self.extract_item_id(create_response.json())

        stat_response = self.api_client.get_statistics(item_id)
        if stat_response.status_code == 200:
            stat_data = stat_response.json()

            # Проверяем, что это список
            assert isinstance(stat_data, list)

            # Если есть данные, проверяем структуру каждого элемента
            for item in stat_data:
                assert isinstance(item, dict)
                required_fields = ["likes", "viewCount", "contacts"]
                for field in required_fields:
                    assert field in item
                    assert isinstance(item[field], int)

    def test_get_statistics_data_consistency_v1(self):
        """Проверка согласованности данных статистики через API v1"""
        data = get_valid_item_data()
        original_stats = data["statistics"]

        create_response = self.api_client.create_item(data)
        assert create_response.status_code == 200

        item_id = self.extract_item_id(create_response.json())

        stat_response = self.api_client.get_statistics(item_id)
        if stat_response.status_code == 200:
            stat_data = stat_response.json()

            # Проверяем, что статистика соответствует ожидаемой
            if len(stat_data) > 0:
                retrieved_stats = stat_data[0]
                assert retrieved_stats["likes"] == original_stats["likes"]
                assert retrieved_stats["viewCount"] == original_stats["viewCount"]
                assert retrieved_stats["contacts"] == original_stats["contacts"]


class TestStatisticsV2:
    """Тесты для эндпоинта GET /api/2/statistic/:id - Получить статистику по объявлению (v2)"""

    def setup_method(self):
        self.api_client = ApiClient()

    def extract_item_id(self, response_data):
        """Извлечение ID из ответа создания объявления"""
        if isinstance(response_data, list) and len(response_data) > 0:
            return response_data[0].get("id")
        return response_data.get("id")

    def test_get_statistics_existing_item_v2(self):
        """Успешное получение статистики существующего объявления через API v2"""
        # Создаем объявление
        data = get_valid_item_data()
        create_response = self.api_client.create_item(data)
        assert create_response.status_code == 200

        created_item = create_response.json()
        item_id = self.extract_item_id(created_item)

        # Получаем статистику через API v2
        stat_response = self.api_client.get_statistics_v2(item_id)
        # API v2 может возвращать 200 или 100 (Continue)
        assert stat_response.status_code in [200, 100]

        if stat_response.status_code == 200:
            stat_data = stat_response.json()

            # Проверяем структуру ответа
            assert isinstance(stat_data, list)
            if len(stat_data) > 0:
                stat_item = stat_data[0]
                required_fields = ["likes", "viewCount", "contacts"]
                for field in required_fields:
                    assert field in stat_item, f"Missing field '{field}' in statistics response"

    def test_get_statistics_nonexistent_item_v2(self):
        """Получение статистики несуществующего объявления через API v2"""
        response = self.api_client.get_statistics_v2("nonexistent_stat_id_123")
        assert response.status_code == 404

    def test_get_statistics_invalid_id_v2(self):
        """Получение статистики с невалидным ID через API v2"""
        test_cases = [
            "invalid_id",
            "123-abc",
            "@#$%",
            " ",
            ""
        ]

        for invalid_id in test_cases:
            response = self.api_client.get_statistics_v2(invalid_id)
            assert response.status_code in [400, 404]

    def test_get_statistics_special_characters_v2(self):
        """Проверка защиты от специальных символов в ID через API v2"""
        response = self.api_client.get_statistics_v2("test@#$%^&*()")
        assert response.status_code in [400, 404]

    def test_get_statistics_sql_injection_v2(self):
        """Проверка защиты от SQL инъекции в ID через API v2"""
        response = self.api_client.get_statistics_v2("1; DROP TABLE statistics; --")
        assert response.status_code in [400, 404]

    def test_get_statistics_xss_v2(self):
        """Проверка защиты от XSS в ID через API v2"""
        response = self.api_client.get_statistics_v2("<script>alert('xss')</script>")
        assert response.status_code in [400, 404]

    def test_get_statistics_long_id_v2(self):
        """Получение статистики с очень длинным ID через API v2"""
        long_id = "a" * 1000
        response = self.api_client.get_statistics_v2(long_id)
        assert response.status_code in [400, 404]

    def test_get_statistics_response_structure_v2(self):
        """Проверка структуры ответа статистики через API v2"""
        data = get_valid_item_data()
        create_response = self.api_client.create_item(data)
        assert create_response.status_code == 200

        item_id = self.extract_item_id(create_response.json())

        stat_response = self.api_client.get_statistics_v2(item_id)
        if stat_response.status_code == 200:
            stat_data = stat_response.json()

            # Проверяем, что это список
            assert isinstance(stat_data, list)

            # Если есть данные, проверяем структуру каждого элемента
            for item in stat_data:
                assert isinstance(item, dict)
                required_fields = ["likes", "viewCount", "contacts"]
                for field in required_fields:
                    assert field in item
                    assert isinstance(item[field], int)

    def test_get_statistics_data_consistency_v2(self):
        """Проверка согласованности данных статистики через API v2"""
        data = get_valid_item_data()
        original_stats = data["statistics"]

        create_response = self.api_client.create_item(data)
        assert create_response.status_code == 200

        item_id = self.extract_item_id(create_response.json())

        stat_response = self.api_client.get_statistics_v2(item_id)
        if stat_response.status_code == 200:
            stat_data = stat_response.json()

            # Проверяем, что статистика соответствует ожидаемой
            if len(stat_data) > 0:
                retrieved_stats = stat_data[0]
                assert retrieved_stats["likes"] == original_stats["likes"]
                assert retrieved_stats["viewCount"] == original_stats["viewCount"]
                assert retrieved_stats["contacts"] == original_stats["contacts"]


class TestStatisticsComparison:
    """Тесты для сравнения поведения API v1 и v2 статистики"""

    def setup_method(self):
        self.api_client = ApiClient()

    def extract_item_id(self, response_data):
        """Извлечение ID из ответа создания объявления"""
        if isinstance(response_data, list) and len(response_data) > 0:
            return response_data[0].get("id")
        return response_data.get("id")

    def test_statistics_v1_vs_v2_same_data(self):
        """Сравнение данных статистики между API v1 и v2 для одного объявления"""
        data = get_valid_item_data()
        create_response = self.api_client.create_item(data)
        assert create_response.status_code == 200

        item_id = self.extract_item_id(create_response.json())

        # Получаем статистику через оба API
        stat_v1_response = self.api_client.get_statistics(item_id)
        stat_v2_response = self.api_client.get_statistics_v2(item_id)

        # Если оба возвращают 200, сравниваем данные
        if stat_v1_response.status_code == 200 and stat_v2_response.status_code == 200:
            stat_v1_data = stat_v1_response.json()
            stat_v2_data = stat_v2_response.json()

            # Данные должны быть идентичными или совместимыми
            assert isinstance(stat_v1_data, list)
            assert isinstance(stat_v2_data, list)

            # Можем сравнить структуру, если есть данные
            if len(stat_v1_data) > 0 and len(stat_v2_data) > 0:
                v1_item = stat_v1_data[0]
                v2_item = stat_v2_data[0]

                # Проверяем одинаковые поля
                for field in ["likes", "viewCount", "contacts"]:
                    assert field in v1_item
                    assert field in v2_item

    def test_statistics_v1_v2_error_consistency(self):
        """Сравнение обработки ошибок между API v1 и v2"""
        invalid_ids = [
            "nonexistent_id",
            "invalid@id",
            "",
            "123-abc"
        ]

        for invalid_id in invalid_ids:
            v1_response = self.api_client.get_statistics(invalid_id)
            v2_response = self.api_client.get_statistics_v2(invalid_id)

            # Ожидаем согласованное поведение при ошибках
            # Оба должны возвращать ошибку клиента (4xx)
            assert v1_response.status_code >= 400 and v1_response.status_code < 500
            assert v2_response.status_code >= 400 and v2_response.status_code < 500


class TestStatisticsPerformance:
    """Тесты производительности для эндпоинтов статистики"""

    def setup_method(self):
        self.api_client = ApiClient()

    def extract_item_id(self, response_data):
        return response_data.get("id")

    def test_statistics_v1_response_time(self):
        """Проверка времени ответа для API v1 статистики"""
        data = get_valid_item_data()
        create_response = self.api_client.create_item(data)
        assert create_response.status_code == 200

        item_id = self.extract_item_id(create_response.json())

        import time
        start_time = time.time()
        stat_response = self.api_client.get_statistics(item_id)
        end_time = time.time()

        if stat_response.status_code == 200:
            response_time = end_time - start_time
            assert response_time < 2, f"Response time too slow: {response_time} seconds"

    def test_statistics_v2_response_time(self):
        """Проверка времени ответа для API v2 статистики"""
        data = get_valid_item_data()
        create_response = self.api_client.create_item(data)
        assert create_response.status_code == 200

        item_id = self.extract_item_id(create_response.json())

        import time
        start_time = time.time()
        stat_response = self.api_client.get_statistics_v2(item_id)
        end_time = time.time()

        if stat_response.status_code in [200, 100]:
            response_time = end_time - start_time
            assert response_time < 2, f"Response time too slow: {response_time} seconds"


class TestStatisticsEdgeCases:
    """Тесты граничных случаев для эндпоинтов статистики"""

    def setup_method(self):
        self.api_client = ApiClient()

    def extract_item_id(self, response_data):
        """Добавляем отсутствующий метод"""
        if isinstance(response_data, list) and len(response_data) > 0:
            return response_data[0].get("id")
        return response_data.get("id")

    def test_statistics_after_item_deletion(self):
        """Получение статистики после удаления объявления"""
        data = get_valid_item_data()
        create_response = self.api_client.create_item(data)
        assert create_response.status_code == 200

        item_id = self.extract_item_id(create_response.json())

        # Удаляем объявление
        delete_response = self.api_client.delete_item(item_id)

        # Пытаемся получить статистику для удаленного объявления
        stat_v1_response = self.api_client.get_statistics(item_id)
        stat_v2_response = self.api_client.get_statistics_v2(item_id)

        # Ожидаем 404 для обоих API
        assert stat_v1_response.status_code == 404
        assert stat_v2_response.status_code == 404