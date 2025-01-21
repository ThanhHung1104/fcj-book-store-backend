import json
import boto3
import os

headers = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,DELETE",
    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token"
}

dynamodb = boto3.resource('dynamodb')
sqs = boto3.client('sqs')

# Get value of the environment variables
table_name = os.getenv('ORDER_TABLE_NAME')
queue_url = os.getenv('SQS_QUEUE_URL')


def lambda_handler(event, context):
    # Get product body info from the event
    products = json.loads(event['body'])
    books = products['books']
    receipt_handle = products['receiptHandle']

    # Write product info to DynamoDB
    table = dynamodb.Table(table_name)
    try:
        for book in books:
            data = {
                'id': str(products['id']),
                'book_id': book['id'],
                'name': book['name'],
                'qty': str(book['qty']),
                'price': str(products['price'])
            }

            table.put_item(Item=data)

    except Exception as e:
        print(f"Error writing to DynamoDB: {e}")
        raise Exception(f"Error writing to DynamoDB: {e}")

    # Delete message in SQS
    try:
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )

    except Exception as e:
        print(f"Error deleting message from SQS: {e}")
        raise Exception(f"Error deleting message from SQS: {e}")

    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps('Order processed successfully')
    }
