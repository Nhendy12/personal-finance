# Personal Finance Automation

Python script to parse emails and insert into data into google sheets

## Table of Contents 📖

* [General Info](#general-info-)
* [Built With](#built-with-)
* [Features](#features-)
* [Getting Started](#getting-started-)
* [Deployment](#deployment-)

## General Info 📝

This project automates extracting daily transacations email data from my personal Gmail and storing it my [Google Sheets monthly budget tracker](https://docs.google.com/spreadsheets/d/1UiPi9wQHIbUpB2RSI0ybCbwW2PcYtrONFho83VuiTu4/edit#gid=0). Can manually run locally or set up in AWS lamda. I have lamdba run every day at 8:00AM PST to fetch previous day transactions. I have email notifications turned for each of my credit cards and venmo to send me alerts whenever I make a purchase.


## Built With ⚡️

Project is created with:
* [requirements.txt](requirements.txt)

## Features 🎯

* Extracts email data from personal Gmail.
* Define which bank transcation emails you want (see [banks.py](email_types/banks.py))
* Parses email content and processes relevant transactions with dates, amounts, and descriptions.
* Stores data in Google Sheets via Google Sheets API.
* Uses OAuth 2.0 for authentication, storing and refreshing tokens automatically.
* Runs on AWS Lambda, triggered by an AWS EventBridge schedule.
* Securely manages secrets via AWS Secrets Manager.

## Getting Started 🛠️ 

1️⃣ Set Up a Google Cloud Project:
* https://developers.google.com/workspace/gmail/api/quickstart/python

2️⃣ You'll need to enable the Google API's (sheets and gmail) and get API credentials:
* https://developers.google.com/workspace/gmail/api/quickstart/python 
```
# Run locally
$ pip install -r requirements.txt
$ py.exe .\quickstart.py
```

3️⃣ You'll need to create a service account to interact with google sheets.
* https://support.google.com/a/answer/7378726?hl=en


## Deployment 🚂

1️⃣ Create AWS project and set up Lambda function

2️⃣ Set up Github actions to deploy project to AWS Lambda

3️⃣ Store your crendentials in AWS Secrets
* token.json -> GMAIL-OAUTH-TOKEN
* service-account-credentials.json -> GOOGLE-SERVICE-ACCOUNT-CREDENTIALS

4️⃣ Set up Amazon EventBridge to trigger Lambda function to run once a day at a certain time

