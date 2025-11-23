import requests

class ApiClient:
    def __init__(self):
        self.base_url = "https://qa-internship.avito.com"
        self.timeout = 10

    def _make_request(self, method, url, **kwargs):
        try:
            response = requests.request(method, url, timeout=self.timeout, **kwargs)
            return response
        except requests.exceptions.Timeout:
            raise Exception(f"Request timeout: {url}")
        except requests.exceptions.ConnectionError:
            raise Exception(f"Connection error: {url}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")

    def create_item(self, item_data):
        url = f"{self.base_url}/api/1/item"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        return self._make_request("POST", url, headers=headers, json=item_data)

    def get_item(self, item_id):
        url = f"{self.base_url}/api/1/item/{item_id}"
        headers = {"Accept": "application/json"}
        return self._make_request("GET", url, headers=headers)

    def get_seller_items(self, seller_id):
        url = f"{self.base_url}/api/1/{seller_id}/item"
        headers = {"Accept": "application/json"}
        return self._make_request("GET", url, headers=headers)

    def get_statistics(self, item_id):
        """Получить статистику через API v1"""
        url = f"{self.base_url}/api/1/statistic/{item_id}"
        headers = {"Accept": "application/json"}
        return self._make_request("GET", url, headers=headers)

    def get_statistics_v2(self, item_id):
        """Получить статистику через API v2"""
        url = f"{self.base_url}/api/2/statistic/{item_id}"
        headers = {"Accept": "application/json"}
        return self._make_request("GET", url, headers=headers)

    def delete_item(self, item_id):
        url = f"{self.base_url}/api/2/item/{item_id}"
        headers = {"Accept": "application/json"}
        return self._make_request("DELETE", url, headers=headers)