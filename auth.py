import os.path

import json
import boto3
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def is_running_in_lambda():
    return bool(os.getenv("AWS_EXECUTION_ENV"))

def get_secret(secret_name):
    client = boto3.client("secretsmanager", region_name="us-west-1")
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])

def update_secret(secret_name, new_data):
    client = boto3.client("secretsmanager", region_name="us-west-1")
    client.update_secret(SecretId=secret_name, SecretString=json.dumps(new_data))

def run_oauth_flow(user_prefix):
    if is_running_in_lambda():    
        print("Should not run Oauth flow inside Lambda, should run locally first instead")
        creds = None
    else:
        cred_path = f"{user_prefix}-credentials/oauth-client-id.json"
        flow = InstalledAppFlow.from_client_secrets_file(cred_path, SCOPES)
        creds = flow.run_local_server(port=8080)
    return creds

def save_credentials(creds, user_prefix):
    creds_json = {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret
        }
    if is_running_in_lambda():
        secret_name = f"{user_prefix}-GMAIL-OAUTH-TOKEN"
        update_secret(secret_name, creds_json)
    else:
        os.makedirs(f"{user_prefix}-credentials", exist_ok=True)
        with open(f"{user_prefix}-credentials/token.json", "w") as token_file:
            json.dump(creds_json, token_file)

def load_credentials(user_prefix):
    # Load credentials from local file (if available) or AWS Secrets Manager.
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    creds = None
    running_on_lambda = is_running_in_lambda()
    if running_on_lambda:
        print("Fetching credentials from AWS Secrets Manager")
        secret_name = f"{user_prefix}-GMAIL-OAUTH-TOKEN"
        token_data = get_secret(secret_name)

        if "refresh_token" not in token_data:
            print("Warning: Refresh token is missing. OAuth flow may be required.")
        
        creds = Credentials.from_authorized_user_info(token_data, SCOPES)
    else:
        token_path = f"{user_prefix}-credentials/token.json"
        if os.path.exists(token_path):
            print(f"Using local token: {token_path}")
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    return creds

def authenticate_gmail(user_prefix):
    # Authenticate with Gmail API, handling token refresh if needed
    creds = load_credentials(user_prefix)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                print("Refreshing expired token")
                creds.refresh(Request())
            except Exception as e:
                print(f"Token refresh failed: {e}")
                creds = None

        # If creds are still invalid, trigger OAuth flow
        if not creds or not creds.valid:
            print("Running OAuth flow.")
            creds = run_oauth_flow(user_prefix)

        save_credentials(creds, user_prefix)

    return creds