import os
import datetime
import traceback
import json
from urllib.parse import quote
import requests
import logging

from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, MapAttribute, NumberAttribute, ListAttribute, UTCDateTimeAttribute, BooleanAttribute


DEBUG = False
if not DEBUG:
    logging.getLogger('boto3').setLevel(logging.WARNING)
    logging.getLogger('botocore').setLevel(logging.WARNING)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# naver_shopping_api = "https://openapi.naver.com/v1/search/shop.json?"
naver_shopping_api = "https://openapi.naver.com/v1/search/shop.json?query={}&display={}&sort={}"
naver_client_id = os.getenv('NAVER_CLIENT_ID')
naver_client_secret = os.getenv('NAVER_CLIENT_SECRET')
naver_api_header = {
    'X-Naver-Client-Id': naver_client_id,
    'X-Naver-Client-Secret': naver_client_secret
}

DEFAULT_DISPLAY = 50
DEFAULT_SORT = 'sim'
EMAIL_ERROR_LEVEL = 'ERROR'


SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')
SLACK_MESSAGE_COLOR = {
    'NORMAL': "good",
    'WARNING': 'warning',
    'ERROR': "danger",
}


class ShoppingQuery(MapAttribute):
    # ref: https://developers.naver.com/docs/search/shopping/
    query = UnicodeAttribute()
    display = NumberAttribute(default=50)
    sort = UnicodeAttribute(default='sim')


class PriceRecord(Model):
    class Meta:
        table_name = "price_record"
        region = 'ap-northeast-2'

    product_id = UnicodeAttribute(hash_key=True)
    crawled_at = UTCDateTimeAttribute(range_key=True)

    item = MapAttribute()


class Product(Model):
    class Meta:
        table_name = "product"
        region = 'ap-northeast-2'

    id = UnicodeAttribute(hash_key=True)
    do_crawl = BooleanAttribute(default=False)
    created_at = UnicodeAttribute()
    last_crawled_at = UTCDateTimeAttribute(null=True)
    min_price = NumberAttribute(default=0)      # min_price 가격 이상인 결과만 사용

    queries = ListAttribute(of=ShoppingQuery)

    lprice = NumberAttribute(null=True)     # 현재까지 최저 가격
    lprice_item = MapAttribute(null=True)   # 최저가격의 item 정보

    def update_lprice(self, lprice_item):
        self.last_crawled_at = datetime.datetime.utcnow()

        if lprice_item:
            self.lprice_item = lprice_item
            self.lprice = int(lprice_item['lprice'])

            record = PriceRecord(self.id, self.last_crawled_at)
            record.item = lprice_item
            record.save()

        return self.save()

    def update_last_crawled_at(self):
        self.last_crawled_at = datetime.datetime.utcnow()
        return self.save()

    def search_lowest_price(self):
        # 최저가를 찾고, 최저가 발견시 알림
        min_price_criterion = self.min_price

        lprice = self.lprice or 100000000
        lprice_item = None

        try:
            for q in self.queries:
                api = naver_shopping_api.format(quote(q.query), q.display or DEFAULT_DISPLAY, q.sort or DEFAULT_SORT)

                api_response = requests.get(api, headers=naver_api_header)
                if api_response.status_code == 200:
                    response_json = api_response.json()

                    if not response_json.get('total', 0):
                        # TODO: no item warning noti
                        pass

                    for item in response_json.get('items', {}):
                        item_lprice = int(item['lprice'])
                        if min_price_criterion <= item_lprice < lprice:
                            lprice = item_lprice
                            lprice_item = item
                            lprice_item['query'] = q.attribute_values
                else:
                    error_message = {
                        'message': 'Naver API Error for {}'.format(self.id),
                        'status_code': api_response.status_code,
                        'text': api_response.text,
                        'api': api,
                        'query': q.attribute_values
                    }
                    send_slack_notification(build_naver_warning_slack_message(error_message))
        except Exception as e:
            error_message = {
                'message': 'Exception occurs by {}'.format(self.id),
                'exception': e,
                'traceback': traceback.format_exc()
            }
            send_slack_notification(build_error_slack_message(error_message))

        self.update_lprice(lprice_item)

        if lprice_item:
            # print(build_normal_slack_message(self))
            status_code = send_slack_notification(build_normal_slack_message(self))

        return lprice_item


def lambda_handler(event, context):
    # print(naver_client_id)
    # print(naver_client_secret)

    products = list(Product.scan(Product.do_crawl==True))

    for product in products:
        product.search_lowest_price()

    print('{} product(s) crawled'.format(len(products)))


def exclude_keywords_exist(exclude_keywords, title):
    for keyword in exclude_keywords:
        if keyword in title:
            return True
    return False


def build_normal_slack_message(product):
    # ref: https://api.slack.com/docs/messages/builder
    lprice_item = product.lprice_item
    return {
        "text": "*{}* 최저가가 *{}* 로 갱신되었습니다.".format(product.id, "{:,}".format(product.lprice)),
        "attachments": [
            {
                "color": SLACK_MESSAGE_COLOR['NORMAL'],
                "title": lprice_item['title'],
                "title_link": lprice_item['link'],
                "image_url": lprice_item['image'],
            }
        ],
        "mrkdwn": True
    }


def build_naver_warning_slack_message(error_body):
    return {
        "text": "*{}* ".format(error_body['message']),
        "attachments": [
            {
                "color": SLACK_MESSAGE_COLOR['WARNING'],
                "text": "status: {}\napi: {}\nquery: {}\ntext: {}\n".format(error_body['status_code'], error_body['api'], error_body['query'], error_body['text']),
            }
        ],
        "mrkdwn": True
    }


def build_error_slack_message(error_body):
    return {
        "text": "*{}* ".format(error_body['message']),
        "attachments": [
            {
                "color": SLACK_MESSAGE_COLOR['ERROR'],
                "text": "exception: {}\ntraceback: {}".format(error_body['exception'], error_body['traceback']),
            }
        ],
        "mrkdwn": True
    }


def send_slack_notification(payload):

    resp = requests.post(SLACK_WEBHOOK_URL, json.dumps(payload))

    return resp.status_code


