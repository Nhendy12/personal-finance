import re

def chase_subject_check(subject):
    return bool(re.search(r"Your \$\d+\.\d{2} transaction", subject))

def chase_get_trancstion_details(subject, body):
    match = re.search(r"\$(\d+\.\d{2}) transaction with (.+)", subject)
    if match:
        amount = match.group(1)
        description = match.group(2)
        return amount, description
    return None, None