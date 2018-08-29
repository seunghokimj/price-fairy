import os
import boto3
from botocore.exceptions import ClientError

client = boto3.client('ses', region_name='us-east-1',)


def send_email(subject, htmlbody, recipients=[], *args, **kwargs):
    # ref: http://docs.aws.amazon.com/ko_kr/ses/latest/DeveloperGuide/send-using-sdk-python.html
    charset = "UTF-8"

    sender = os.getenv('SENDER_EMAIL')

    if not recipients:
        recipients = [os.getenv('RECIPIENT_EMAIL'),]

    response = None

    try:
        response = client.send_email(
            Destination={
                'ToAddresses': recipients
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': charset,
                        'Data': htmlbody,
                    },
                    # 'Text': {
                    #     'Charset': charset,
                    #     'Data': textbody,
                    # },
                },
                'Subject': {
                    'Charset': charset,
                    'Data': subject,
                },
            },
            Source=sender,
        )

    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID: {}".format(response['ResponseMetadata']['RequestId']))

    return response