import time

import requests
from requests.adapters import HTTPAdapter, Retry


class RequestAPI:
    def __init__(self):
        self._session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=0.5,
        )
        self._session.mount("http://", HTTPAdapter(max_retries=retries))
        self._session.mount("https://", HTTPAdapter(max_retries=retries))

    def get(
        self, url: str, headers: dict, params: dict, timeout: int = 5
    ):
        print(f"making get request to url: {url}")
        try:
            response = self._session.get(url=url, headers=headers, params=params, timeout=timeout)
            if response.ok:
                return response
            else:
                print(f"error code: {response.status_code}, text: {response.text}")
        except Exception as e:
            print(f"exception : {e}")
        raise Exception(f"Возникла проблема при запросе к стороннему апи.")

    def post(
        self, url: str, headers: dict, params: dict, body: dict, timeout: int = 5
    ):
        print(f"making post request to url: {url}")
        try:
            response = self._session.post(url=url, headers=headers, params=params, json=body, timeout=timeout)
            if response.ok:
                return response
            else:
                print(f"error code: {response.status_code}, text: {response.text}")
        except Exception as e:
            print(f"exception : {e}")
        raise Exception(f"Возникла проблема при запросе к стороннему апи.")

    def patch(
        self, url: str, headers: dict, params: dict, body: dict, timeout: int = 5
    ):
        print(f"making patch request to url: {url}")
        try:
            response = self._session.patch(
                url=url, headers=headers, params=params, json=body, timeout=timeout
            )
            if response.ok:
                return response
            else:
                print(f"error code: {response.status_code}, text: {response.text}")
        except Exception as e:
            print(f"exception : {e}")
        raise Exception(f"Возникла проблема при запросе к стороннему апи.")
