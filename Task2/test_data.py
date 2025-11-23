import random
import time


def generate_seller_id():
    """Генерация sellerID в допустимом диапазоне"""
    return random.randint(111111, 999999)


def get_valid_item_data():
    """Валидные данные для создания объявления"""
    return {
        "sellerID": generate_seller_id(),
        "name": f"Test Item {int(time.time())}",
        "price": 9900,
        "statistics": {
            "likes": 21,
            "viewCount": 11,
            "contacts": 43
        }
    }


def get_negative_price_data():
    """Данные с отрицательной ценой"""
    data = get_valid_item_data()
    data["price"] = -100
    return data


def get_zero_price_data():
    """Данные с нулевой ценой"""
    data = get_valid_item_data()
    data["price"] = 0
    return data


def get_minimal_price_data():
    """Данные с минимальной ценой"""
    data = get_valid_item_data()
    data["price"] = 1
    return data


def get_empty_name_data():
    """Данные с пустым названием"""
    data = get_valid_item_data()
    data["name"] = ""
    return data


def get_negative_statistics_data():
    """Данные с отрицательной статистикой"""
    data = get_valid_item_data()
    data["statistics"] = {"likes": -5, "viewCount": -10, "contacts": -1}
    return data


def get_zero_statistics_data():
    """Данные с нулевой статистикой"""
    data = get_valid_item_data()
    data["statistics"] = {"likes": 0, "viewCount": 0, "contacts": 0}
    return data


def get_max_values_data():
    """Данные с максимальными значениями"""
    data = get_valid_item_data()
    data["price"] = 2147483647
    data["statistics"] = {
        "likes": 2147483647,
        "viewCount": 2147483647,
        "contacts": 2147483647
    }
    return data


def get_special_characters_data():
    """Данные со специальными символами"""
    data = get_valid_item_data()
    data["name"] = "Тест @#$% 100%"
    return data


def get_boundary_seller_data(seller_id):
    """Данные с граничным sellerID"""
    data = get_valid_item_data()
    data["sellerID"] = seller_id
    return data


def get_multiple_items_data(seller_id, item_number):
    """Данные для нескольких объявлений одного продавца"""
    data = get_valid_item_data()
    data["sellerID"] = seller_id
    data["name"] = f"Товар {item_number}"
    return data

def get_invalid_types_data():
    """Данные с неверными типами"""
    return {
        "sellerID": "string_instead_of_int",
        "name": 12345,  # число вместо строки
        "price": "string_price",
        "statistics": "not_an_object"
    }

def get_extra_fields_data():
    """Данные с лишними полями"""
    data = get_valid_item_data()
    data["extra_field"] = "should_be_ignored"
    return data

def get_sql_injection_data():
    """Данные с SQL инъекцией"""
    data = get_valid_item_data()
    data["name"] = "test'; DROP TABLE items; --"
    return data

def get_xss_data():
    """Данные с XSS"""
    data = get_valid_item_data()
    data["name"] = "<script>alert('xss')</script>"
    return data

def get_test_ids_for_get_item():
    """Тестовые ID для проверки получения объявлений"""
    return [
        "valid_existing_id",  # будет заменен в тестах на реальный ID
        "nonexistent_id_12345",
        "invalid@id#format",
        "123-invalid-456",
        "script_alert_xss_script",
        "1;DROP TABLE items;--",
        "a" * 100,  # очень длинный ID
        "123456",  # числовой ID
        "",  # пустой ID
        "   ",  # пробелы
        "test\nid",  # ID с переносом строки
        "null",
        "undefined",
        "true",
        "false",
        "0",
        "-1",
        "1.5",  # дробный ID
    ]


def get_test_seller_ids():
    """Тестовые sellerID для проверки получения объявлений продавца"""
    return [
        111111,  # Минимальный валидный
        999999,  # Максимальный валидный
        123456,  # Случайный валидный
        100000,  # Ниже минимального
        1000000,  # Выше максимального
        -123456,  # Отрицательный
        0,  # Ноль
        123456.78,  # Дробный
    ]


def get_invalid_seller_ids():
    """Невалидные sellerID для негативного тестирования"""
    return [
        "invalid_string",
        "123abc",
        "@#$%^",
        "",
        " ",
        "123; DROP TABLE items; --",
        "<script>alert('xss')</script>",
        "../../etc/passwd",
        "123' OR '1'='1",
        "a" * 1000,  # Очень длинная строка
    ]


