import boto3
import os

BUCKET = os.environ['BUCKET_NAME']
TABLE = os.environ['TABLE_NAME']

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE)

header_res = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,DELETE",
    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
}


def lambda_handler(event, context):
    delete_id = event.get('pathParameters', {})
    delete_id['rv_id'] = 0

    try:
        # Get item from id
        try:
            delete_item = table.get_item(Key=delete_id)
            image_path = delete_item['Item'].get('image', '')
            image_name = image_path.split('/')[-1]

        except Exception as e:
            print(f"Error getting item with that {delete_id['id']}")
            raise Exception(f"Error getting item with that {delete_id['id']}")

        # Delete item in DynamoDB and s3 bucket
        try:
            items_with_same_id = table.query(
                TableName=TABLE,
                ProjectionExpression='rv_id',
                KeyConditionExpression='id = :id',
                ExpressionAttributeValues={':id': delete_id['id']}
            )

            for item in items_with_same_id['Items']:
                delete_id['rv_id'] = item['rv_id']
                table.delete_item(Key=delete_id)

            s3_client.delete_object(Bucket=BUCKET, Key=image_name)

        except Exception as e:
            print(f"Error getting item with that {delete_id['id']}")
            raise Exception(f"Error getting item with that {delete_id['id']}")

        return {
            'statusCode': 200,
            'body': 'Successfully delete item!',
            'headers': header_res
        }

    except Exception as e:
        print(f'Error deleting item: {e}')
        raise Exception(f'Error deleting item: {e}')
