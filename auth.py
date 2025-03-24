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

def run_oauth_flow():
    if is_running_in_lambda():    
        creds_data = get_secret("OAUTH-CLIENT-ID")
        creds = Credentials.from_authorized_user_info(creds_data, SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials/oauth-client-id.json', SCOPES)
        creds = flow.run_local_server(port=8080)
    return creds

def save_credentials(creds):
    creds_json = {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret
        }
    if is_running_in_lambda():
        client = boto3.client("secretsmanager", region_name="us-west-1")
        client.update_secret(SecretId="GMAIL-OAUTH-TOKEN", SecretString=json.dumps(creds_json))
    else:
        with open("credentials/token.json", "w") as token:
            json.dump(creds_json, token)

def load_credentials():
    # Load credentials from local file (if available) or AWS Secrets Manager.
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    creds = None
    running_on_lambda = is_running_in_lambda()
    if running_on_lambda:
        print("Fetching credentials from AWS Secrets Manager")
        token_data = get_secret("GMAIL-OAUTH-TOKEN")

        if "refresh_token" not in token_data:
            print("Warning: Refresh token is missing. OAuth flow may be required.")
        
        creds = Credentials.from_authorized_user_info(token_data, SCOPES)
    elif os.path.exists("credentials/token.json"):
        print("Using local token.json")
        creds = Credentials.from_authorized_user_file("credentials/token.json", SCOPES)

    return creds

def authenticate_gmail():
    # Authenticate with Gmail API, handling token refresh if needed
    creds = load_credentials()
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
            creds = run_oauth_flow()

        save_credentials(creds)

    return creds