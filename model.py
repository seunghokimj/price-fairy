import datetime
import traceback
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, MapAttribute, NumberAttribute, ListAttribute, UTCDateTimeAttribute, BooleanAttribute


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
