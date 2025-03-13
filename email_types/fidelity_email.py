import re

def fidelity_subject_check(subject):
    return bool(re.search(r"A charge was authorized", subject))


def fidelity_get_trancstion_details(subject, body):
    match = re.search(r"Your card was charged \$(\d+\.\d{2}) at (.+?)(?=\.)", body)
    
    if match:
        amount = match.group(1)
        merchant = match.group(2)
        return amount, merchant

    return None, None