import boto3
import os
import simplejson as json

TABLE = os.environ['TABLE_NAME']

# Get the service resource
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE)

header_res = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,DELETE",
    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
}

secondary_index = "name-index"


def lambda_handler(event, context):
    try:
        books_data = table.scan(
            TableName=TABLE,
            IndexName=secondary_index
        )

        books = books_data.get('Items', [])

        for book in books:
            data_comment = table.query(
                TableName=TABLE,
                KeyConditionExpression="id = :id AND rv_id > :rv_id",
                ExpressionAttributeValues={
                    ":id": book['id'],
                    ":rv_id": 0
                }
            )

            book['comments'] = data_comment['Items']

        return {
            "statusCode": 200,
            "headers": header_res,
            "body": json.dumps(books, use_decimal=True)
        }
    except Exception as e:
        print(f'Error getting items: {e}')
        raise Exception(f'Error getting items: {e}')
