import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from slack_api import *

result_msg = {
    'product_id': '테스트',
    'lprice': 1000000,
    'title': '테스트 아이템',
    'link': 'www.amazon.com',
    'image_url': 'www.amazon.com',
}
send_slack_notification(build_normal_slack_message(**result_msg))


warning_msg = {
    'message': 'Naver API Error for Test',
    'status_code': '400',
    'text': 'Error Text',
    'api': 'Error URL',
    'query': 'Error Query',
}

send_slack_notification(build_naver_warning_slack_message(**warning_msg))

error_message = {
    'message': 'Exception occurs by 테스트',
    'exception_text': 'Test Error Exception',
    'traceback_text': 'No traceback'
}

send_slack_notification(build_error_slack_message(**error_message))
