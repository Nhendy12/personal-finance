import re
from bs4 import BeautifulSoup

def boa_subject_check(subject):

    return bool(re.search(r"Credit card transaction exceeds alert limit you set", subject))

def boa_get_trancstion_details(subject, body):
    merchant = None
    amount = None

    soup = BeautifulSoup(body, "html.parser")
    for label in soup.find_all("td", class_="tdMobZ2tbllabel2"):
        key = label.get_text(strip=True).rstrip(":")
        value_td = label.find_next_sibling("td")
        if value_td:
            if key == "Where":
                merchant = value_td.get_text(strip=True)
            elif key == "Amount":
                amount = value_td.get_text(strip=True).lstrip("$")

    return amount, merchant