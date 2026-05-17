import os
from typing import Any

import requests

API_BASE_URL = os.getenv("POMODORO_HUB_API_URL", "http://127.0.0.1:8000")


class PomodoroApiClient:
    def __init__(self, base_url: str = API_BASE_URL) -> None:
        self.base_url = base_url.rstrip("/")

    def _request(self, method: str, path: str, json: dict[str, Any] | None = None):
        url = f"{self.base_url}{path}"
        try:
            response = requests.request(method, url, json=json, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as error:
            message = str(error)
            if error.response is not None:
                try:
                    detail = error.response.json().get("detail")
                    if detail:
                        message = str(detail)
                except ValueError:
                    message = error.response.text or message
            raise RuntimeError(message) from error

    def register(self, name: str, password: str):
        payload = {"name": name, "password": password}
        return self._request("POST", "/users/register", json=payload)

    def login(self, name: str, password: str):
        payload = {"name": name, "password": password}
        return self._request("POST", "/users/login", json=payload)

    def start(self, name: str, password: str, duration: int):
        payload = {"name": name, "password": password, "duration": duration}
        return self._request("POST", "/pomodoro/start", json=payload)

    def stop(self, name: str, password: str):
        payload = {"name": name, "password": password}
        return self._request("POST", "/pomodoro/stop", json=payload)

    def get_active(self):
        return self._request("GET", "/pomodoro/active")
