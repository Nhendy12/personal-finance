from datetime import datetime, timedelta, timezone

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from auth import authenticate_gmail


def main():
  from email_utils import get_email_contents

  creds = authenticate_gmail()

  try:
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