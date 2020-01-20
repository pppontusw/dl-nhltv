from time import sleep
import requests

max_retries = 5


def get(*args, **kwargs):
    for i in range(max_retries):
        try:
            req = requests.get(*args, **kwargs)
            return req
        except Exception as e:
            if i == max_retries - 1:
                raise e
            else:
                sleep(15)


def post(*args, **kwargs):
    for i in range(max_retries):
        try:
            req = requests.post(*args, **kwargs)
            return req
        except Exception as e:
            if i == max_retries - 1:
                raise e
            else:
                sleep(15)
