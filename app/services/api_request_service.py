import time
import traceback

import requests


class RequestAPI:
    def get(
        self, url: str, headers: dict, params: dict, retries: int = 5, timeout: int = 5
    ):
        counter = retries
        while counter > 0:
            print(f"making get request to url: {url}")
            try:
                response = requests.get(url=url, headers=headers, params=params, timeout=timeout)
                if response.ok:
                    return response
                else:
                    print(f"error code: {response.status_code}, text: {response.text}")
            except Exception as e:
                print(f"exception : {e}")
            counter -= 1
            time.sleep(0.5 + counter * 0.1)
        raise Exception(f"Возникла проблема при запросе к стороннему апи.")

    def post(
        self, url: str, headers: dict, params: dict, body: dict, retries: int = 5, timeout: int = 5
    ):
        counter = retries
        while counter > 0:
            print(f"making post request to url: {url}")
            try:
                response = requests.post(url=url, headers=headers, params=params, json=body, timeout=timeout)
                if response.ok:
                    return response
                else:
                    print(f"error code: {response.status_code}, text: {response.text}")
            except Exception as e:
                print(f"exception : {e}")
            counter -= 1
            time.sleep(0.5 + counter * 0.1)
        raise Exception(f"Возникла проблема при запросе к стороннему апи.")

    def patch(
        self, url: str, headers: dict, params: dict, body: dict, retries: int = 5, timeout: int = 5
    ):
        counter = retries
        while counter > 0:
            print(f"making patch request to url: {url}")
            try:
                response = requests.patch(
                    url=url, headers=headers, params=params, json=body, timeout=timeout
                )
                if response.ok:
                    return response
                else:
                    print(f"error code: {response.status_code}, text: {response.text}")
            except Exception as e:
                print(f"exception : {e}")
            counter -= 1
            time.sleep(0.5 + counter * 0.1)
        raise Exception(f"Возникла проблема при запросе к стороннему апи.")
