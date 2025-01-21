import base64
from multipart import MultipartParser
from io import BytesIO
import boto3
import os

BUCKET = os.environ['BUCKET_NAME']
BUCKET_RESIZE = os.environ['BUCKET_RESIZE_NAME']
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


def parse_multipart(body, boundary):
    parser = MultipartParser(stream=body, boundary=boundary)

    fields = {}
    files = {}

    for part in parser:
        if part.filename:
            files[part.name] = {
                'file-name': part.filename,
                'content': part.raw
            }

        else:
            fields[part.name] = part.value

    return fields, files


def upload_to_s3(key, bucket, body):
    try:
        s3_client.put_object(Key=key, Bucket=bucket, Body=body)
    except Exception as e:
        print(f"Error uploading image to S3: {e}")
        raise Exception(f'Error uploading image to S3: {e}')


def create_new_item(table, item):
    try:
        table.put_item(Item=item)
    except Exception as e:
        print(f"Error creating new item in DynamoDB table: {e}")
        raise Exception(f'Error creating new item in DynamoDB table: {e}')


def lambda_handler(event, context):
    content_type = event['headers'].get(
        'Content-Type', '') or event['headers'].get('content-type', '')

    try:
        body = event['body']

        if event['isBase64Encoded']:
            body = BytesIO(base64.b64decode(body))

        boundary = content_type.split("boundary=")[1]

        fields, files = parse_multipart(body, boundary)

        # Upload image to s3
        file_name = files['image']['file-name']
        file_content = files['image']['content']

        upload_to_s3(file_name, BUCKET, file_content)
        s3_url = f'https://{BUCKET_RESIZE}.s3.amazonaws.com/{file_name}'

        # Create new item in DB
        item = {
            'id': fields.get('id', 0),
            'rv_id': 0,
            'name': fields.get('name', ''),
            'author': fields.get('author', ''),
            'price': fields.get('price', ''),
            'category': fields.get('category', ''),
            'description': fields.get('description', ''),
            'image': s3_url
        }

        create_new_item(table, item)

        return {
            "statusCode": 200,
            "headers": header_res,
            "body": "Successfully created item!",
        }

    except Exception as e:
        print(f"Error processing form data: {e}")
        raise Exception(f'Error processing form data: {e}')
