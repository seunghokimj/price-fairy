import os
import datetime
import traceback
import json
import requests
import logging

from model import Product
from naver_api import naver_client_id, naver_client_secret


DEBUG = False
if not DEBUG:
    logging.getLogger('boto3').setLevel(logging.WARNING)
    logging.getLogger('botocore').setLevel(logging.WARNING)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    # print(naver_client_id)
    # print(naver_client_secret)

    products = list(Product.scan(Product.do_crawl==True))

    for product in products:
        product.search_lowest_price()

    print('{} product(s) crawled'.format(len(products)))

