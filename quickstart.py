from datetime import datetime, timedelta, timezone

import sys
import traceback
import boto3
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from auth import authenticate_gmail, is_running_in_lambda

def main(name=None):
  from email_utils import get_email_contents

  try:
    if not name:
      name = get_args_name()

    creds = authenticate_gmail(name)

    # Set Pacific Timezone
    PT = timezone(timedelta(hours=-7))

    # Get yesterday in Pacific Time
    now_pt = datetime.now(PT)
    yesterday = now_pt - timedelta(days=1)

    start_of_yesterday = (yesterday.replace(hour=0, minute=0, second=0, microsecond=0))
    end_of_yesterday = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)

    start_of_yesterday_utc = start_of_yesterday.astimezone(timezone.utc)
    end_of_yesterday_utc = end_of_yesterday.astimezone(timezone.utc)
    
    # Convert to UNIX timestamps (Gmail API uses seconds)
    start_of_yesterday_ts = int(start_of_yesterday_utc.timestamp())
    end_of_yesterday_ts = int(end_of_yesterday_utc.timestamp())

    query = f"after:{start_of_yesterday_ts} before:{end_of_yesterday_ts}"
    print(f"Pacific Start: {start_of_yesterday} -> UTC: {start_of_yesterday_utc} ({start_of_yesterday_ts})")
    print(f"Pacific End: {end_of_yesterday} -> UTC: {end_of_yesterday_utc} ({end_of_yesterday_ts})")
    print(f"Query: {query}")

    service = build("gmail", "v1", credentials=creds)
    messages = []
    next_page_token = None

    while True:
        response = service.users().messages().list(userId="me", q=query, maxResults=100, pageToken=next_page_token).execute()
        messages.extend(response.get('messages', []))
        next_page_token = response.get('nextPageToken')
    
        if not next_page_token:
            break
        
    # print(f"Total emails found: {len(messages)}")
    print("-------------")
    for msg in messages:
        get_email_contents(service, msg["id"], name)
    print("-------------")
    return f"Processed transactions for: {name}"

  except Exception as error:
    if is_running_in_lambda():
        send_email(error, name)
    else:
      print(f"An error occurred: {type(error).__name__}: {error}")
      traceback.print_exc()

def get_args_name():
        if len(sys.argv) <= 1:
          raise Exception("Name must be included")
   
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('name', type=str, help='A name to process')
        args = parser.parse_args()
        return args.name

def send_email(error, name=None):
  ses_client = boto3.client("ses", region_name="us-west-1")

  sender_email = "nickh1225@gmail.com"
  recipient_email = "nickh1225@gmail.com"
  error_type = type(error).__name__
  subject = f"Personal finance Lambda failed for {name or 'unknown user'}: {error_type}"
  stack = "".join(traceback.format_exception(type(error), error, error.__traceback__))
  body_text = (
      f"User: {name or 'unknown'}\n"
      f"Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
      f"Error: {error_type}: {error}\n"
      f"\n"
      f"Traceback:\n{stack}"
  )

  try:
      response = ses_client.send_email(
          Source=sender_email,
          Destination={"ToAddresses": [recipient_email]},
          Message={
              "Subject": {"Data": subject},
              "Body": {"Text": {"Data": body_text}},
          },
      )
      print("Email sent successfully! Message:", body_text)
  except Exception as e:
      print("Error sending email:", str(e))

if __name__ == "__main__":
  main()