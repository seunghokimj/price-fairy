import os
import json
import requests

__all__ = [
    'build_normal_slack_message',
    'build_naver_warning_slack_message',
    'build_error_slack_message',
    'send_slack_notification'
]

SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')
SLACK_MESSAGE_COLOR = {
    'NORMAL': "good",
    'WARNING': 'warning',
    'ERROR': "danger",
}


def build_normal_slack_message(product_id, lprice, title, link, image_url):
    # ref: https://api.slack.com/docs/messages/builder
    return {
        "text": "*{}* 최저가가 *{}* 로 갱신되었습니다.".format(product_id, "{:,}".format(lprice)),
        "attachments": [
            {
                "color": SLACK_MESSAGE_COLOR['NORMAL'],
                "title": title,
                "title_link": link,
                "image_url": image_url,
            }
        ],
        "mrkdwn": True
    }


def build_naver_warning_slack_message(
        message,
        status_code,
        text,
        api,
        query):
    return {
        "text": f"*{message}* ",
        "attachments": [
            {
                "color": SLACK_MESSAGE_COLOR['WARNING'],
                "text": f"status: {status_code}\napi: {api}\nquery: {query}\ntext: {text}\n",
            }
        ],
        "mrkdwn": True
    }


def build_error_slack_message(message, exception_text, traceback_text):
    return {
        "text": "*{}* ".format(message),
        "attachments": [
            {
                "color": SLACK_MESSAGE_COLOR['ERROR'],
                "text": f"exception: {exception_text}\ntraceback: {traceback_text}"
            }
        ],
        "mrkdwn": True
    }


def send_slack_notification(payload):
    resp = requests.post(SLACK_WEBHOOK_URL, json.dumps(payload))
    print(f'status: {resp.status_code}, payload: {payload}')

    return resp.status_code

