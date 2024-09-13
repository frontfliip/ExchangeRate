import requests
import datetime
from datetime import datetime
from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)
auth = HTTPBasicAuth()

users = {
    "admin": generate_password_hash("admin", method='pbkdf2:sha256')
}

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_file('booming-crowbar-370309-19f67679ff2f.json', scopes=SCOPES)
client = gspread.authorize(creds)

def convert_to_unix(date_string):
    dt = datetime.strptime(date_string, '%Y-%m-%d')
    unix_timestamp = int(dt.timestamp())
    return unix_timestamp


def convert_to_nbu_format(date_string):
    dt = datetime.strptime(date_string, '%Y-%m-%d')
    return dt.strftime('%Y%m%d')


def fetch_exchange_rate(base_url, update_from, update_to, currency):
    update_from_nbu = convert_to_nbu_format(update_from)
    update_to_nbu = convert_to_nbu_format(update_to)
    req_url = f"{base_url}?start={update_from_nbu}&end={update_to_nbu}&valcode={currency}&sort=exchangedate&order=desc&json"

    response = requests.get(req_url)

    period_prices = {}

    if response.status_code == 200:
        exchange_rates = response.json()
        for day_info in exchange_rates:
            curr_rate = day_info['rate_per_unit']
            curr_date = datetime.strptime(day_info['exchangedate'], '%d.%m.%Y').strftime('%Y-%m-%d')
            period_prices[curr_date] = curr_rate
    return period_prices


@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username
    return None


def write_df_to_sheet(GSHEET_NAME, TAB_NAME, prices):
    gc = gspread.service_account(filename='booming-crowbar-370309-19f67679ff2f.json')
    sh = gc.open(GSHEET_NAME)
    worksheet = sh.worksheet(TAB_NAME)

    worksheet.clear()
    worksheet.format('B2:B', {'numberFormat': {'type': 'NUMBER', 'pattern': '0.0000'}})

    rows = [['Date', 'Rate']]

    for date, rate in prices.items():
        rows.append([date, rate])

    worksheet.update(rows)

@app.route('/write_exchange_rate', methods=['GET'])
@auth.login_required
def write_exchange_rate():
    update_from = request.args.get('from', datetime.today().strftime('%Y-%m-%d'))
    update_to = request.args.get('to', datetime.today().strftime('%Y-%m-%d'))
    currency = request.args.get('currency', 'usd')

    base_url = 'https://bank.gov.ua/NBU_Exchange/exchange_site'
    prices = fetch_exchange_rate(base_url, update_from, update_to, currency)

    write_df_to_sheet('exchange_rate', 'exchange_rate', prices)

    return jsonify({"message": "Exchange rates written to the Google Sheet"}), 200

@app.route('/exchange_rate', methods=['GET'])
@auth.login_required
def get_exchange_rate():

    update_from = request.args.get('from', datetime.today().strftime('%Y-%m-%d'))
    update_to = request.args.get('to', datetime.today().strftime('%Y-%m-%d'))
    currency = request.args.get('currency', 'usd')

    base_url = 'https://bank.gov.ua/NBU_Exchange/exchange_site'
    prices = fetch_exchange_rate(base_url, update_from, update_to, currency)
    return jsonify(prices)


if __name__ == '__main__':
    app.run(debug=True)
