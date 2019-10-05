import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import datetime
from model import Product

nintendo = Product()
nintendo.id = '닌텐도스위치'
nintendo.do_crawl = True
nintendo.created_at = datetime.date.today().strftime('%Y-%m-%d')
nintendo.min_price = 300000
nintendo.queries = [{
      "display": 50,
      "query": "닌텐도 스위치",
      "sort": "sim"
    }]

nintendo.save()
