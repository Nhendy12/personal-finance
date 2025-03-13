import re

def citi_subject_check(subject):
    return bool(re.search(r"A \$\d+\.\d{2} transaction", subject))

def citi_get_trancstion_details(subject, body):
    match = re.search(r"A \$(\d+\.\d{2}) transaction was made on your (.+)", subject)
    if match:
        amount = match.group(1)
        description = match.group(2)
        return amount, description
    return None, None