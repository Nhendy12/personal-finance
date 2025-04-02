# personal finance automation

This project automates extracting daily transacations email data from my personal Gmail and storing it my [Google Sheets monthly budget tracker](https://docs.google.com/spreadsheets/d/1UiPi9wQHIbUpB2RSI0ybCbwW2PcYtrONFho83VuiTu4/edit#gid=0). Can manually run locally or set up in AWS lamda. I have lamdba run every day at 8:00AM PST to fetch previous day transactions. 


## 🛠️ Setup & Deployment
To clone and run this application, you'll need [Git](https://git-scm.com), [Ruby on Rails](https://www.tutorialspoint.com/ruby-on-rails/rails-installation.htm), and [Node.js](https://nodejs.org/en/download/) (which comes with [npm](http://npmjs.com)) installed on your computer.
```
# Clone this repository
$ git clone https://github.com/Nhendy12/pokedex.git

# Go into the repository
$ cd pokedex
```

🛠️ Setup & Deployment

1️⃣ Google Cloud Setup

Enable Gmail & Google Sheets API:

Go to Google Cloud Console.

Enable Gmail API and Google Sheets API.

Create OAuth Credentials:

Navigate to APIs & Services > Credentials.

Click Create Credentials > OAuth Client ID.

Select Web Application and add redirect URIs (e.g., http://localhost:8080/).

Download credentials.json.