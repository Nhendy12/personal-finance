import re

def venmo_subject_check(subject):
    return bool(re.search(r"You paid", subject))

def venmo_get_trancstion_details(subject, body):
    match = re.search(r"You paid (.+?) \$(\d+\.\d{2})", subject)

    if match:
        recipient = match.group(1)
        amount = match.group(2)
        return amount, "Venmo to " + recipient

    return None, None  