import os
import datetime
import traceback
import json
import requests
import logging



DEBUG = False
if not DEBUG:
    logging.getLogger('boto3').setLevel(logging.WARNING)
    logging.getLogger('botocore').setLevel(logging.WARNING)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):

    pass
