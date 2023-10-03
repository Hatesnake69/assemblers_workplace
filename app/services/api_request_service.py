import time
import traceback

import requests


class RequestAPI:
    def get(self, url: str, headers: dict, params: dict, retries: int = 3):
        counter = retries
        while counter > 0:
            print(f"making get request to url: {url}")
            response = requests.get(url=url, headers=headers, params=params)
            if response.ok:
                return response
            counter -= 1
            time.sleep(0.5)
        raise Exception("website is not responding well")

    def post(self, url: str, headers: dict, params: dict, body: dict, retries: int = 3):
        counter = retries
        while counter > 0:
            print(f"making post request to url: {url}")
            response = requests.post(url=url, headers=headers, params=params, json=body)
            if response.ok:
                return response
            counter -= 1
            time.sleep(0.5)
        raise Exception("website is not responding well")

    def patch(self, url: str, headers: dict, params: dict, body: dict, retries: int = 3):
        counter = retries
        while counter > 0:
            print(f"making post request to url: {url}")
            response = requests.patch(url=url, headers=headers, params=params, json=body)
            if response.ok:
                return response
            counter -= 1
            time.sleep(0.5)
        raise Exception("website is not responding well")