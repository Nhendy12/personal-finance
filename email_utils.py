import base64
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from email.utils import parsedate_to_datetime
from datetime import datetime
from calendar import month_name

from email_types.banks import BANK_EMAILS
from email_types.chase_email import chase_subject_check, chase_get_trancstion_details
from email_types.citi_email import citi_subject_check, citi_get_trancstion_details
from email_types.discover_email import discover_subject_check, discover_get_trancstion_details
from email_types.fidelity_email import fidelity_subject_check, fidelity_get_trancstion_details
from email_types.venmo_email import venmo_subject_check, venmo_get_trancstion_details

def get_email_contents(service, message_id):
    # print(f"Message ID: {message_id}")
    message = service.users().messages().get(userId="me", id=message_id, format="full").execute()
    
    # Extract headers
    headers = message["payload"]["headers"]
    subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
    sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
    date_header = next((h["value"] for h in headers if h["name"] == "Date"), None)

    result, bank_name = is_transaction_email(sender)
    if not result: return
    print("??????")
    if date_header:
        parsed_date = parsedate_to_datetime(date_header).strftime('%m-%d-%Y')
        # print(f"Email Date: {parsed_date.strftime('%m-%d-%Y')} (UTC: {parsed_date.astimezone().isoformat()})")
    else:
        parsed_date = ""

    body = ""
    if "parts" in message["payload"]:
        for part in message["payload"]["parts"]:
            if part["mimeType"] == "text/plain":
                body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
                break
    else:
        body = base64.urlsafe_b64decode(message["payload"]["body"]["data"]).decode("utf-8")

    should_continue, amount, description = get_details_from_transaction_email(bank_name, subject, body)
    print(f"should_continue: {should_continue}")

    if not should_continue: return
    print(f"amount: {amount}")
    print(f"description: {description}")
    print(f"parsed_date: {parsed_date}")

    # insert line item into google sheets
    insert_transaction(get_sheet_name(), parsed_date, amount, description)
    print("??????")


def is_transaction_email(sender):
    for bank_name, bank_email in BANK_EMAILS.items():
        if bank_email in sender:
            return True, bank_name
    return False, None


BANK_SUBJECT_CHECKS = {
    "Chase": chase_subject_check,  
    "Citi": citi_subject_check,  
    "Discover": discover_subject_check,
    "Fidelity": fidelity_subject_check,
    "Venmo": venmo_subject_check,
}

BANK_GET_TRANSACTION_DETAILS = {
    "Chase": chase_get_trancstion_details,  
    "Citi": citi_get_trancstion_details,  
    "Discover": discover_get_trancstion_details,
    "Fidelity": fidelity_get_trancstion_details,
    "Venmo": venmo_get_trancstion_details,
}

def default_bank_function(subject):
    """Fallback function for unsupported banks."""
    return False

# bank_name determiens which files in email_types to use
# checks if we should use this email
# if we should then it returns the amount and description from the email
def get_details_from_transaction_email(bank_name, subject, body):
    check_function = BANK_SUBJECT_CHECKS.get(bank_name, default_bank_function)
    get_amount_and_description_function = BANK_GET_TRANSACTION_DETAILS.get(bank_name, default_bank_function)

    if check_function(subject):
        print(f"Transaction email from {bank_name} matched.")
        # Further processing here
        amount, description = get_amount_and_description_function(subject, body)
        
        return True, amount, description
    else:
        print(f"Transaction email from {bank_name} did not match.")
        return False, None, None
    
def get_sheet_name():
    current_date = datetime.now()
    day_of_month = current_date.day
    month = current_date.month
    year = current_date.year
    
    if day_of_month == 1:
        if month == 1:
            previous_month = month_name[12]
            previous_year = year - 1
        else:
            previous_month = month_name[month - 1]
            previous_year = year
    else:
        previous_month = month_name[month]
        previous_year = year
    
    return f"{previous_month} {previous_year} Budget"
    
# Google Sheets API Authentication
def authenticate_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    #   creds_data = get_secret("GOOGLE-SERVICE-ACCOUNT-CREDENTIALS")
    creds = ServiceAccountCredentials.from_json_keyfile_name("./credentials/service-account-credentials.json", scope)
    client = gspread.authorize(creds)
    return client

def insert_transaction(sheet_name, date, amount, description):
    client = authenticate_google_sheets()
    sheet = client.open(sheet_name).worksheet('Transactions')
    
    amount = float(amount.lstrip("'"))
    rounded_amount = round(amount, 2)

    # Insert transaction details as a new row in first empty row found from Column C
    next_row = len(sheet.col_values(3)) + 1 
    print(f"next_row {next_row}")

    sheet.update(f"B{next_row}:D{next_row}", [[date, rounded_amount, description]])

    print(f"Inserted at row {next_row}")