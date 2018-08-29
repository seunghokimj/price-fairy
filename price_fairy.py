import os
import json
import requests
import datetime
import logging
import boto3
from boto3.dynamodb.conditions import Attr
from aws import ses

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


dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2', )

product_table = dynamodb.Table('product')
search_result_table = dynamodb.Table('search_result')

DEFAULT_DISPLAY = 50
DEFAULT_SORT = 'sim'
EMAIL_ERROR_LEVEL = 'ERROR'


def lambda_handler(event, context):
    # print(naver_client_id)
    # print(naver_client_secret)

    scan_response = product_table.scan(
        FilterExpression=Attr('do_crawl').eq(True),
        # Limit=20
    )

    products = scan_response.get('Items', {})

    for product in products:
        search_lowest_price(product)

    print('{} product(s) crawled'.format(len(products)))


def search_lowest_price(product):
    lprice = product.get('lprice') or 100000000
    min_price = product.get('min_price', 0)
    lprice_item = None

    queries = product.get('queries', [])
    try:
        for q in queries:
            api = naver_shopping_api.format(q['query'], q.get('display', DEFAULT_DISPLAY), q.get('sort', DEFAULT_SORT))

            api_response = requests.get(api, headers=naver_api_header)
            if api_response.status_code == 200:
                response_json = api_response.json()

                if response_json.get('total', 0):
                    # no item warning email
                    pass

                for item in response_json.get('items', {}):
                    item_lprice = int(item['lprice'])
                    if (min_price <= item_lprice < lprice) \
                            and not exclude_keywords_exist(q.get('exclude', []), item.get('title','')):
                        lprice = item['lprice'] = int(item['lprice'])
                        lprice_item = item
                        lprice_item['query'] = q
            else:
                error_message = {
                    'status_code': api_response.status_code,
                    'text': api_response.text,
                    'api': api,
                    'query': q
                }
                send_email('Naver API Error {}'.format(product['id']), error_message, EMAIL_ERROR_LEVEL)
    except Exception as e:
        subject = 'Exception occurs {} / {}'.format(e, product['id'])
        error_message = {
            'exception': e,
            'product': product
        }
        send_email(subject, error_message, EMAIL_ERROR_LEVEL)

    if lprice_item:
        update_product_lprice(product, lprice_item)
        email_subject = 'Lowest price: {} / {}'.format(product['id'], product.get('last_crawled_at','whenever'))
        send_email(email_subject, product, 'NORMAL')
    else:
        update_last_crawled_at(product)

    return lprice_item


def exclude_keywords_exist(exclude_keywords, title):
    for keyword in exclude_keywords:
        if keyword in title:
            return True
    return False


def update_product_lprice(product, lprice_item):
    str_now = (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).strftime('%Y-%m-%d')
    lprice_result = {
        'product_id': product['id'],
        'crawled_at': str_now,
        'item': lprice_item,
    }

    search_result_table.put_item(Item=lprice_result)

    product['lprice_item'] = lprice_item
    product['lprice'] = int(lprice_item['lprice'])
    product['last_crawled_at'] = str((datetime.datetime.utcnow() + datetime.timedelta(hours=9)))[:19]

    product_table.put_item(Item=product)

    return lprice_item


def update_last_crawled_at(product):
    product['last_crawled_at'] = str((datetime.datetime.utcnow() + datetime.timedelta(hours=9)))[:19]
    product_table.put_item(Item=product)


def send_email(subject, message, level):
    subject = "[Price Fairy][{}] {}".format(level, subject)

    htmlbody = """<p>
                    message: {}<br>
                    At {} UTC<br></p>""".format(message, datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))

    contents = {
        'htmlbody': htmlbody,
        'subject': subject,
    }

    ses.send_email(**contents)

    return contents


