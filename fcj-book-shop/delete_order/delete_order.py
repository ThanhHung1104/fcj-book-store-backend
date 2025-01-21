import json
import boto3
import os

headers = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,DELETE",
    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token"
}

sqs = boto3.client('sqs')

# Get value of the environment variables
queue_url = os.getenv('SQS_QUEUE_URL')


def lambda_handler(event, context):
    order = json.loads(event['body'])

    try:
        if 'receiptHandle' in order and order['receiptHandle']:
            sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=order['receiptHandle']
            )

        else:
            raise Exception("No receiptHandle provided")

    except Exception as e:
        print(f"Error deleting order: {e}")
        raise Exception(f"Error deleting order: {e}")

    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps('Order deleted successfully')
    }
