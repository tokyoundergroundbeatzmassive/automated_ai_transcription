import requests
import webbrowser

APP_KEY = 'dropbox_app_key'
APP_SECRET = 'dropbox_app_secret'
REDIRECT_URI = 'http://localhost'

class DropboxTokenManager:
    def __init__(self, app_key, app_secret, redirect_uri):
        self.app_key = app_key
        self.app_secret = app_secret
        self.redirect_uri = redirect_uri
        self.refresh_token = None
        self.access_token = None

    def get_authorization_code(self):
        auth_url = f"https://www.dropbox.com/oauth2/authorize?client_id={self.app_key}&redirect_uri={self.redirect_uri}&response_type=code&token_access_type=offline"
        print(f"Please access the following URL to authenticate:\n{auth_url}")
        webbrowser.open(auth_url)
        return input("Enter the authorization code from the redirected URL: ")

    def get_refresh_token(self, auth_code):
        token_url = "https://api.dropboxapi.com/oauth2/token"
        data = {
            "code": auth_code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri
        }
        auth = (self.app_key, self.app_secret)
        
        response = requests.post(token_url, data=data, auth=auth)
        
        if response.status_code == 200:
            token_info = response.json()
            self.refresh_token = token_info.get('refresh_token')
            self.access_token = token_info.get('access_token')
            print("Token information:")
            print(f"Refresh token: {self.refresh_token}")
            print(f"Access token: {self.access_token}")
            return self.refresh_token
        else:
            print(f"Failed to obtain tokens: {response.text}")
            return None

    def refresh_access_token(self):
        if not self.refresh_token:
            print("No refresh token available. Please authenticate first.")
            return None

        token_url = "https://api.dropboxapi.com/oauth2/token"
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        }
        auth = (self.app_key, self.app_secret)
        
        response = requests.post(token_url, data=data, auth=auth)
        
        if response.status_code == 200:
            token_info = response.json()
            self.access_token = token_info.get('access_token')
            print(f"New access token: {self.access_token}")
            return self.access_token
        else:
            print(f"Failed to refresh access token: {response.text}")
            return None


if __name__ == "__main__":
    manager = DropboxTokenManager(APP_KEY, APP_SECRET, REDIRECT_URI)

    auth_code = manager.get_authorization_code()
    refresh_token = manager.get_refresh_token(auth_code)

    if refresh_token:
        print("Please store the refresh token securely.")

        new_access_token = manager.refresh_access_token()
        if new_access_token:
            print("Access token successfully refreshed.")