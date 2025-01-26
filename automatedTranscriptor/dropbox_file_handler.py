import os
import json
import requests

class DropboxFileHandler:
    def __init__(self, access_token):
        self.access_token = access_token

    def download_file_to_tmp(self, file_path):
        try:
            url = "https://content.dropboxapi.com/2/files/download"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Dropbox-API-Arg": json.dumps({"path": file_path})
            }
            response = requests.post(url, headers=headers)
            response.raise_for_status()

            file_name = os.path.basename(file_path)

            tmp_file_path = f"/tmp/{file_name}"
            with open(tmp_file_path, "wb") as f:
                f.write(response.content)
            
            print(f"File downloaded: {tmp_file_path}")
            return tmp_file_path
        except Exception as e:
            print(f"Error downloading file {file_path}: {str(e)}")
            return None

    def get_file_metadata(self, file_path):
        try:
            url = "https://api.dropboxapi.com/2/files/get_metadata"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            data = {
                "path": file_path,
                "include_media_info": True
            }
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting metadata for file {file_path}: {str(e)}")
            return None