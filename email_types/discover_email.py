import re

def discover_subject_check(subject):
    return bool(re.search(r"Transaction Alert", subject))

def discover_get_trancstion_details(subject, body):
    merchant_match = re.search(r"Merchant:\s*(.+)", body)
    amount_match = re.search(r"Amount:\s*\$(\d+\.\d{2})", body)

    merchant = merchant_match.group(1) if merchant_match else None
    amount = amount_match.group(1) if amount_match else None

    return amount, merchant