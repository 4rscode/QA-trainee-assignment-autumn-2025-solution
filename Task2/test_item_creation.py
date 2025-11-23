import pytest
import re
from api_client import ApiClient
from test_data import (
    get_valid_item_data,
    get_negative_price_data,
    get_zero_price_data,
    get_minimal_price_data,
    get_empty_name_data,
    get_negative_statistics_data,
    get_zero_statistics_data,
    get_max_values_data,
    get_special_characters_data,
    get_boundary_seller_data,
    get_multiple_items_data,
    generate_seller_id
)


class TestItemCreation:

    def setup_method(self):
        self.api_client = ApiClient()

    def extract_item_id(self, response_data):
        return response_data.get("id")

    def test_create_item_valid_data(self):
        """Создание объявления с валидными данными"""
        data = get_valid_item_data()
        response = self.api_client.create_item(data)

        assert response.status_code == 200
        response_data = response.json()

        # БАГ: Формат ответа не соответствует документации
        required_fields = ["id", "sellerId", "name", "price", "statistics", "createdAt"]
        for field in required_fields:
            assert field in response_data, f"Missing field '{field}' in response"

    @pytest.mark.parametrize("missing_field", ["sellerID", "name", "price", "statistics"])
    def test_create_item_missing_required_fields(self, missing_field):
        """Проверка обязательных полей"""
        data = get_valid_item_data()
        del data[missing_field]

        response = self.api_client.create_item(data)
        assert response.status_code == 400

    def test_create_item_negative_price(self):
        """Проверка валидации отрицательной цены - БАГ"""
        data = get_negative_price_data()
        response = self.api_client.create_item(data)
        assert response.status_code == 400, "BUG: Server accepts negative prices"

    def test_create_item_minimal_price(self):
        """Создание объявления с минимальной ценой"""
        data = get_minimal_price_data()
        response = self.api_client.create_item(data)
        assert response.status_code == 200

    def test_create_item_zero_price(self):
        """Создание объявления с нулевой ценой"""
        data = get_zero_price_data()
        response = self.api_client.create_item(data)
        assert response.status_code == 400

    def test_create_item_boundary_seller_id(self):
        """Проверка граничных значений sellerID"""
        for seller_id in [111111, 999999]:
            data = get_boundary_seller_data(seller_id)
            response = self.api_client.create_item(data)
            assert response.status_code == 200

    def test_create_item_empty_name(self):
        """Проверка пустого названия"""
        data = get_empty_name_data()
        response = self.api_client.create_item(data)
        assert response.status_code == 400

    def test_create_item_negative_statistics(self):
        """Проверка отрицательной статистики - БАГ"""
        data = get_negative_statistics_data()
        response = self.api_client.create_item(data)
        assert response.status_code == 400, "BUG: Server accepts negative statistics"

    def test_create_item_zero_statistics(self):
        """Проверка нулевой статистики"""
        data = get_zero_statistics_data()
        response = self.api_client.create_item(data)
        assert response.status_code == 200

    def test_create_multiple_items_same_seller(self):
        """Несколько объявлений от одного продавца"""
        seller_id = generate_seller_id()

        for i in range(2):
            data = get_multiple_items_data(seller_id, i + 1)
            response = self.api_client.create_item(data)
            assert response.status_code == 200

    def test_get_created_item(self):
        """Создание и получение объявления"""
        data = get_valid_item_data()
        create_response = self.api_client.create_item(data)
        assert create_response.status_code == 200

        response_data = create_response.json()
        item_id = self.extract_item_id(response_data)

        if item_id:
            get_response = self.api_client.get_item(item_id)
            assert get_response.status_code in [200, 404]

    def test_create_item_max_values(self):
        """Проверка максимальных значений"""
        data = get_max_values_data()
        response = self.api_client.create_item(data)
        assert response.status_code == 200

    def test_create_item_special_characters(self):
        """Проверка специальных символов в названии"""
        data = get_special_characters_data()
        response = self.api_client.create_item(data)
        assert response.status_code == 200

