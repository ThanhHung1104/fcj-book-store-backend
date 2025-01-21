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

    # Extract the necessary information from the event
    username = body["username"]
    confirmation_code = body["confirmation_code"]

    # Get Client ID and Client Secret from environment variables
    client_id = os.environ["CLIENT_ID"]
    client_secret = os.environ["CLIENT_SECRET"]

    # Generate the secret hash
    message = bytes(username + client_id, "utf-8")
    key = bytes(client_secret, "utf-8")
    secret_hash = base64.b64encode(
        hmac.new(key, message, digestmod=hashlib.sha256).digest()).decode()

    try:
        # Confirm the user
        response = client.confirm_sign_up(
            ClientId=client_id,
            SecretHash=secret_hash,
            Username=username,
            ConfirmationCode=confirmation_code
        )

        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps("User confirmed successfully")
        }

    except Exception as e:
        print(f"Error confirming user: {e}")
        raise Exception(f"Error confirming user: {e}")
