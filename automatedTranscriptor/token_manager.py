import os
import json
from datetime import datetime, timedelta
import requests
import boto3
from botocore.exceptions import ClientError

class DropboxTokenManager:
    TABLE_NAME = 'DropboxTokens'

    def __init__(self):
        self.app_key = os.environ.get('DROPBOX_APP_KEY')
        self.app_secret = os.environ.get('DROPBOX_APP_SECRET')
        self.refresh_token = os.environ.get('DROPBOX_REFRESH_TOKEN')
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.ensure_table_exists()

    def ensure_table_exists(self):
        try:
            table = self.dynamodb.Table(self.TABLE_NAME)
            table.load()
            return table
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                return self.create_table()
            else:
                raise

    def create_table(self):
        table = self.dynamodb.create_table(
            TableName=self.TABLE_NAME,
            KeySchema=[
                {
                    'AttributeName': 'token_type',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'token_type',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        table.wait_until_exists()
        return table

    def get_access_token(self):
        token_data = self._read_token_from_dynamodb()
        if token_data:
            print(f"Token data read from DynamoDB: {token_data}")
        if token_data and self._is_token_valid(token_data):
            print("Using existing valid access token.")
            return token_data['access_token']
        else:
            print("Token is invalid or not found, refreshing access token.")
            return self._refresh_access_token()

    def _read_token_from_dynamodb(self):
        try:
            response = self.table.get_item(Key={'token_type': 'access_token'})
            return response.get('Item')
        except ClientError as e:
            print(f"Error reading token from DynamoDB: {str(e)}")
            return None

    def _write_token_to_dynamodb(self, token_data):
        try:
            self.table.put_item(Item=token_data)
        except ClientError as e:
            print(f"Error writing token to DynamoDB: {str(e)}")

    def _is_token_valid(self, token_data):
        expiry = datetime.fromisoformat(token_data['expiry'])
        is_valid = datetime.now() < expiry - timedelta(minutes=10)
        print(f"Token valid: {is_valid}, expiry: {expiry}")
        return is_valid

    def _refresh_access_token(self):
        url = 'https://api.dropboxapi.com/oauth2/token'
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'client_id': self.app_key,
            'client_secret': self.app_secret
        }

        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            token_info = response.json()
            
            token_data = {
                'token_type': 'access_token',
                'access_token': token_info['access_token'],
                'expiry': (datetime.now() + timedelta(seconds=token_info['expires_in'])).isoformat()
            }
            self._write_token_to_dynamodb(token_data)
            
            print("Access token updated.")
            return token_data['access_token']
        except requests.RequestException as e:
            print(f"Failed to refresh access token: {str(e)}")
            return None