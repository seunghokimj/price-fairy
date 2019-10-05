import os
import requests
from urllib.parse import quote


# naver_shopping_api = "https://openapi.naver.com/v1/search/shop.json?"
naver_shopping_api_endpoint = "https://openapi.naver.com/v1/search/shop.json?query={}&display={}&sort={}"
naver_client_id = os.getenv('NAVER_CLIENT_ID')
naver_client_secret = os.getenv('NAVER_CLIENT_SECRET')
naver_api_header = {
    'X-Naver-Client-Id': naver_client_id,
    'X-Naver-Client-Secret': naver_client_secret
}

DEFAULT_DISPLAY = 50
DEFAULT_SORT = 'sim'
EMAIL_ERROR_LEVEL = 'ERROR'


def call_naver_api(query, display=DEFAULT_DISPLAY, sort=DEFAULT_SORT):
    api = naver_shopping_api_endpoint.format(quote(query), display, sort)
    return requests.get(api, headers=naver_api_header)
