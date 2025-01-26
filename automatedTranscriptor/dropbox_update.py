import json
import requests
import boto3
from botocore.exceptions import ClientError
from token_manager import DropboxTokenManager

class DropboxUpdateNotificationAPI:
    def __init__(self):
        self.error = False
        self.errmsg = ''
        self.responses = None
        self.token_manager = DropboxTokenManager()
        self.access_token = self.token_manager.get_access_token()
        self.folders = ['/automated_transcriptor']
        self.dynamodb = boto3.resource('dynamodb')
        self.table_name = 'DropboxCursors'
        self.table = self.ensure_table_exists()

    def ensure_table_exists(self):
        try:
            table = self.dynamodb.Table(self.table_name)
            table.load()
            return table
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                return self.create_table()
            else:
                raise

    def create_table(self):
        table = self.dynamodb.create_table(
            TableName=self.table_name,
            KeySchema=[
                {
                    'AttributeName': 'folder_path',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'folder_path',
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

    def request_dropbox_api_v2(self, url, argv=None, post=None, upload=None):
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        print(f"Request headers: {headers}")

        if argv is not None:
            headers['Dropbox-API-Arg'] = json.dumps(argv)

        if upload is not None:
            headers['Content-Type'] = 'application/octet-stream'
            data = upload
        elif post is not None:
            headers['Content-Type'] = 'application/json'
            data = json.dumps(post)
        else:
            data = None

        print(f"Request data: {data}")

        try:
            response = requests.post(url, headers=headers, data=data, timeout=5)
            print(f"Response status code: {response.status_code}")
            print(f"Response content: {response.text}")
            response.raise_for_status()
            self.responses = response.json() if post or upload else response.text
            return True
        except requests.exceptions.RequestException as e:
            self.error = True
            self.errmsg = str(e)
            print(f"Request exception: {self.errmsg}")
            return False

    def get_new_files(self):
        new_files = []
        for folder in self.folders:
            print(f"Processing folder: {folder}")
            cursor = self.get_cursor(folder)
            print(f"Cursor for {folder}: {cursor}")

            if cursor:
                url = 'https://api.dropboxapi.com/2/files/list_folder/continue'
                post = {'cursor': cursor}
            else:
                url = 'https://api.dropboxapi.com/2/files/list_folder'
                post = {
                    'path': folder,
                    'recursive': True,
                    'include_media_info': False,
                    'include_deleted': False,
                    'include_has_explicit_shared_members': False
                }

            if not self.request_dropbox_api_v2(url, post=post):
                print(f"API request failed for {folder}")
                print(f"Error: {self.errmsg}")
                continue

            print(f"API response: {self.responses}")

            if self.responses is not None:
                if isinstance(self.responses, dict) and 'entries' in self.responses:
                    for entry in self.responses['entries']:
                        if entry['.tag'] == 'file':
                            new_files.append(entry['path_display'])
                            print(f"New file detected: {entry['path_display']}")

                if isinstance(self.responses, dict) and self.responses.get('cursor'):
                    self.save_cursor(folder, self.responses['cursor'])
                    print(f"New cursor saved for {folder}: {self.responses['cursor']}")
            else:
                print(f"No response received for {folder}")

        print(f"Total new files detected: {len(new_files)}")
        return new_files

    def get_cursor(self, folder):
        try:
            response = self.table.get_item(Key={'folder_path': folder})
            return response.get('Item', {}).get('cursor')
        except ClientError as e:
            print(f"Error getting cursor for {folder}: {str(e)}")
            return None

    def save_cursor(self, folder, cursor):
        try:
            self.table.put_item(Item={'folder_path': folder, 'cursor': cursor})
        except ClientError as e:
            print(f"Error saving cursor for {folder}: {str(e)}")