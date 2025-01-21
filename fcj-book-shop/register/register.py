import json
import boto3
import os
import hmac
import hashlib
import base64

# Initialize the Cognito client
client = boto3.client("cognito-idp")

headers = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET,DELETE",
    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token"
}


def lambda_handler(event, context):
    # Get the body from the event and parse it as JSON
    body = json.loads(event["body"])

    # Get the username and password from the body
    username = body["username"]
    password = body["password"]

    # Get Client ID and Client Secret from environment variables
    client_id = os.environ["CLIENT_ID"]
    client_secret = os.environ["CLIENT_SECRET"]

    # Generate the secret hash
    message = bytes(username + client_id, 'utf-8')
    key = bytes(client_secret, 'utf-8')
    secret_hash = base64.b64encode(
        hmac.new(key, message, digestmod=hashlib.sha256).digest()).decode()

    try:
        # Sign up the user
        client.sign_up(
            ClientId=client_id,
            SecretHash=secret_hash,
            Username=username,
            Password=password
        )

        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps("User registration successful")
        }

    except Exception as e:
        print(f"Error registering user: {e}")
        raise Exception(f"Error registering user: {e}")
