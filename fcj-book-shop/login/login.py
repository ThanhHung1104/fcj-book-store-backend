import json
import boto3
import os
import hmac
import hashlib
import base64

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
        response = client.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": username,
                "PASSWORD": password,
                "SECRET_HASH": secret_hash
            },
            ClientId=client_id,
        )

        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps({
                "message": "Login successful",
                "id_token": response["AuthenticationResult"]["IdToken"],
                "access_token": response["AuthenticationResult"]["AccessToken"],
                "refresh_token": response["AuthenticationResult"]["RefreshToken"]
            })
        }

    except Exception as e:
        print(f"Error login: {e}")
        raise Exception(f"Error login: {e}")
