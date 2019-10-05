import datetime
import traceback
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, MapAttribute, NumberAttribute, ListAttribute, UTCDateTimeAttribute, BooleanAttribute

from naver_api import call_naver_api
from slack_api import *


class ShoppingQuery(MapAttribute):
    # ref: https://developers.naver.com/docs/search/shopping/
    query = UnicodeAttribute()
    display = NumberAttribute(default=50)
    sort = UnicodeAttribute(default='sim')


class PriceRecord(Model):
    class Meta:
        table_name = "price_fairy_price_record"
        region = 'ap-northeast-2'

    product_id = UnicodeAttribute(hash_key=True)
    crawled_at = UTCDateTimeAttribute(range_key=True)

    item = MapAttribute()


class Product(Model):
    class Meta:
        table_name = "price_fairy_product"
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
                api_response = call_naver_api(q.query, q.display, q.sort)
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
                        'api': api_response.url,
                        'query': q.attribute_values
                    }
                    slack_status_code = send_slack_notification(build_naver_warning_slack_message(**error_message))

        except Exception as e:
            error_message = {
                'message': 'Exception occurs by {}'.format(self.id),
                'exception_text': e,
                'traceback_text': traceback.format_exc()
            }
            slack_status_code = send_slack_notification(build_error_slack_message(**error_message))

        self.update_lprice(lprice_item)

        if lprice_item:
            # print(build_normal_slack_message(self))
            result_msg = {
                'product_id': self.id,
                'lprice': self.lprice,
                'title': self.lprice_item['title'],
                'link': self.lprice_item['link'],
                'image_url': self.lprice_item['image'],
            }
            slack_status_code = send_slack_notification(build_normal_slack_message(**result_msg))

        return lprice_item
