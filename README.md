# Price Fairy

Python과 AWS lambda로 동작하는 최저가 알림 기능 입니다.

가격 요정(..)이 네이버 쇼핑 API를 사용하여 등록한 item의 최저가를 알려줍니다.

혼자서 개발한 toy project 이지만 python과 serverless 개념을 이해하는데 도움이 될 수 있을것 같아 repo 공유합니다.

버그나 설계에 대한 피드백 환영합니다.


## Getting Started
<!-- These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system. -->

### Prerequisites

[python serverless demo](https://github.com/seunghokimj/python-serverless-demo)를 참고하여 "Cloud 9 시작하기", "AWS Credentials 설정
", "S3 Bucket 생성하기", "Python 개발 환경 설정" 을 진행합니다.

## 

## Step 0 Initial Setup

```sh
ec2-user:~/environment $ sudo yum install -y tree

ec2-user:~/environment $ git clone --single-branch --branch step0 https://github.com/seunghokimj/price-fairy.git

ec2-user:~/environment $ cd price-fairy/
ec2-user:~/environment/price-fairy (step0) $ tree
.
├── aws
│   └── ses.py
├── callback.py
├── price_fairy_policy.json
├── price_fairy.py
├── README.md
├── requirements.txt
└── zappa_settings.json

```

### virtualenv 설정
```
ec2-user:~/environment/price-fairy (step0) $ virtualenv -p python3 venv
Running virtualenv with interpreter /usr/bin/python3
Using base prefix '/usr'
New python executable in /home/ec2-user/environment/price-fairy/venv/bin/python3
Also creating executable in /home/ec2-user/environment/price-fairy/venv/bin/python
Installing setuptools, pip, wheel...
done.
ec2-user:~/environment/price-fairy (step0) $ . venv/bin/activate
(venv) ec2-user:~/environment/price-fairy (step0) $ 
```

### package 설치
```
(venv) ec2-user:~/environment/price-fairy (step0) $ pip install -r requirements.txt                                                      
 
```

## Step 1 DB Modeling
### Product Table, Price Record Table 생성
슬라이드 참고

#### model.py
```
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

```

#### Example item 추가 
```
(venv) ec2-user:~/environment/price-fairy (step0) $ git pull
(venv) ec2-user:~/environment/price-fairy (step0) $ git checkout origin/step1
(venv) ec2-user:~/environment/price-fairy (step1) $ python step1/add_example_item.py 

```

## Step 2 Shopping API
Naver Shopping API를 호출하는 기능을 개발합니다.

### Naver Open API 등록
[Naver Open API 등록](https://developers.naver.com/docs/common/openapiguide/appregister.md#애플리케이션-등록)


#### Naver API Test
```
(venv) ec2-user:~/environment/price-fairy (step1) $ git checkout -t origin/step2

 
```

## Step 3 Slack Push Setup


## Step 4 Zappa



<!--
### Installing

TBD


## Running the tests

TBD


## Deployment

TBD
-->
<!-- ## Contributing -->
<!-- Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us. -->

## Versioning

버전 관리는 [SemVer](http://semver.org/) 를 따릅니다. 각 버전은 tag 로 관리 합니다.

## Authors

* **Seungho Kim** - *Initial work* - [seunghkimj](https://github.com/seunghkimj)

<!-- See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project. -->

## License

MIT License
<!-- MIT License - see the [LICENSE.md](LICENSE.md) file for details -->

