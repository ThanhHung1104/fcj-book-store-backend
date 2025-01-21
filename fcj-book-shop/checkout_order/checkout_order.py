import json
import boto3
import os

headers = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,DELETE",
    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token"
}


def lambda_handler(event, context):
    sqs = boto3.client('sqs')
    sns = boto3.client('sns')

    sqs_queue_url = os.environ['SQS_QUEUE_URL']
    sns_topic_arn = os.environ['SNS_TOPIC_ARN']
    sns_topic_subject = "New order received. Please process."

    try:
        body = json.loads(event['body'])

        print(f"body: {body}")

        # Send to SQS
        sqs_response = sqs.send_message(
            QueueUrl=sqs_queue_url,
            MessageBody=json.dumps(body)
        )

        # Send to SNS
        sns_response = sns.publish(
            TopicArn=sns_topic_arn,
            Message=f"New order received: {json.dumps(body)}",
            Subject=sns_topic_subject
        )

        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'message': 'Order processed successfully',
                'sqs_message_id': sqs_response['MessageId'],
                'sns_message_id': sns_response['MessageId']
            })
        }

    except Exception as e:
        print(f"Error processing order: {e}")
        raise Exception(f"Error processing order: {e}")
