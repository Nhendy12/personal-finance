import os.path

from datetime import datetime, timedelta

import json
import boto3
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from email_utils import get_email_contents

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def is_running_in_lambda():
  return bool(os.getenv("AWS_EXECUTION_ENV"))


def get_secret(secret_name):
  client = boto3.client("secretsmanager", region_name="us-west-1")
  response = client.get_secret_value(SecretId=secret_name)
  return json.loads(response["SecretString"])

def save_credentials(creds):
  if is_running_in_lambda() == True:
      boto3.client("secretsmanager").update_secret(
          SecretId="GmailOAuthToken", SecretString=creds.to_json()
      )
  else:
      with open("credentials/token.json", "w") as token:
          token.write(creds.to_json())

def load_credentials():
  """Load credentials from local file (if available) or AWS Secrets Manager."""
  creds = None
  running_on_lambda = is_running_in_lambda()
  if running_on_lambda:
      print("Fetching credentials from AWS Secrets Manager")
      token_data = get_secret("GmailOAuthToken")
      creds = Credentials.from_authorized_user_info(token_data, SCOPES)
  elif os.path.exists("credentials/token.json"):
      print("Using local token.json")
      creds = Credentials.from_authorized_user_file("credentials/token.json", SCOPES)

  return creds

def authenticate_gmail():
  """Authenticate with Gmail API, handling token refresh if needed."""
  creds = load_credentials()
  if not creds or not creds.valid:
      if creds and creds.expired and creds.refresh_token:
          try:
            print("Refreshing expired token")
            creds.refresh(Request())
          except Exception as e:
            print(f"Token refresh failed: {e}")
            creds = None
      else:
          print("Token is invalid or expired. Running OAuth flow.")
          flow = InstalledAppFlow.from_client_secrets_file(
              'credentials.json', SCOPES)
          creds = flow.run_local_server(port=0)

      save_credentials(creds)

  return creds

def main():
  creds = authenticate_gmail()

  try:
    yesterday = datetime.utcnow() - timedelta(days=1)

    print(f"datetime.utcnow(): {datetime.utcnow()}")
    print(f"yesterday: {yesterday}")

    start_of_yesterday = (yesterday.replace(hour=0, minute=0, second=0, microsecond=0))
    end_of_yesterday = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)

    print(f"start_of_yesterday: {start_of_yesterday}")
    print(f"end_of_yesterday: {end_of_yesterday}")

    # Convert to UNIX timestamps (Gmail API uses seconds)
    start_of_yesterday_ts = int(start_of_yesterday.timestamp())
    end_of_yesterday_ts = int(end_of_yesterday.timestamp())

    print(f"start_of_yesterday_ts: {start_of_yesterday_ts}")
    print(f"end_of_yesterday_ts: {end_of_yesterday_ts}")

    query = f"after:{start_of_yesterday_ts} before:{end_of_yesterday_ts}"
    print(f"query: {query}")

    service = build("gmail", "v1", credentials=creds)
    messages = []
    next_page_token = None

    while True:
        response = service.users().messages().list(userId="me", q=query, maxResults=100, pageToken=next_page_token).execute()
        messages.extend(response.get('messages', []))
        next_page_token = response.get('nextPageToken')
    
        if not next_page_token:
            break
        
    print(f"Total emails found: {len(messages)}")
    print("-------------")
    for msg in messages:
        get_email_contents(service, msg["id"])
    print("-------------")

  except HttpError as error:
    # TODO(developer) - Handle errors from gmail API.
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()