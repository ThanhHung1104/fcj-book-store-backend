import os
import json
import boto3

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


def get_messages_from_sqs(messages):
    # Get the total number of messages in the queue
    response = sqs.get_queue_attributes(
        QueueUrl=queue_url,
        AttributeNames=['ApproximateNumberOfMessages']
    )
    total_messages = int(response['Attributes']['ApproximateNumberOfMessages'])

    while len(messages) < total_messages:
        # Receive messages from SQS queue
        received_message_res = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=20
        )

        if 'Messages' in received_message_res:
            for message in received_message_res['Messages']:
                messages.append({
                    "receiptHandle": message["ReceiptHandle"],
                    "books": json.loads(message["Body"])['books'],
                    "price": json.loads(message["Body"])['price'],
                    "status": "Unprocessed"
                })


def get_messages_from_dynamodb(messages):
    table = dynamodb.Table(table_name)

    try:
        res = table.scan()
        orders = res.get('Items', [])
        aggregated_orders = {}

        for order in orders:
            order_id = order['id']

            book = {
                'id': order['book_id'],
                'name': order['name'],
                'qty': order['qty'],
            }

            if order_id not in aggregated_orders:
                aggregated_orders[order_id] = {
                    'id': order_id,
                    'books': [book],
                    'price': order['price']
                }

            else:
                aggregated_orders[order_id]['books'].append(book)

        for order in aggregated_orders.values():
            messages.append({
                "receiptHandle": "",
                "books": order['books'],
                "price": order['price'],
                "status": "Processed"
            })

    except Exception as e:
        print(f"Error reading from DynamoDB: {e}")
        raise Exception(f"Error reading from DynamoDB: {e}")


def lambda_handler(event, context):
    messages = []

    # Get messages from sqs
    get_messages_from_sqs(messages)

    # Get Messages from DynamoDB
    get_messages_from_dynamodb(messages)

    return {
        'statusCode': 200,
        'body': json.dumps(messages),
        'headers': headers
    }
