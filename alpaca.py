import requests
import json
import alpaca_trade_api as tradeapi

key = 'FAKE_KEY'
secret = 'FAKE_SECRET'
base_url = 'https://paper-api.alpaca.markets'

api = tradeapi.REST(key, secret, base_url, api_version='v2')
account = api.get_account()
print(account.status)

tenquant_key = 'FAKE_KEY'
tenquant_base_url = 'https://api.tenquant.io'

tickers_list = []


with open('tickers.txt', 'r+') as tickers_file:
  tickers_list = tickers_file.read().splitlines()

stocks_data = {}

for ticker in tickers_list:
  # build url
  request_url = (tenquant_base_url + '/earningsreport?ticker={TICKER}&key={KEY}').replace('{TICKER}', ticker).replace('{KEY}', tenquant_key)

  # get json response
  ticker_json = requests.get(request_url).content

  # make sure everything works and make a Pytohn dict from the json
  try:
    ticker_data = dict(json.loads(ticker_json))
  except:
    continue
  if 'error' in ticker_data.keys():
    continue

  # extract key data points
  net_income = ticker_data['netincomeloss']
  operating_income = ticker_data['operatingincomeloss']

  non_operating_income = float(net_income) - float(operating_income)
  non_operating_income_percent = non_operating_income / float(net_income)

  stocks_data[ticker] = non_operating_income_percent

sorted_stocks_data = sorted(stocks_data.items(), key=lambda x: x[1])

understated_ten_percent = sorted_stocks_data[:int(len(sorted_stocks_data)/10) + 1]

overstated_ten_percent = sorted_stocks_data[-int(len(sorted_stocks_data)/10) - 1:]

print('Understated 10%: ')
print(understated_ten_percent)
print('Overstated 10%: ')
print(overstated_ten_percent)

# long understated earnings
for long_stock, diff in understated_ten_percent:
    qty = 1
    side = 'buy'
    try:
        api.submit_order(long_stock, qty, side, "market", "day")
        print("Market order of | " + str(qty) + " " + long_stock + " " + side + " | completed.")
    except:
        print("Order of | " + str(qty) + " " + long_stock + " " + side + " | did not go through.")

# short overstated earnings
for short_stock, diff in overstated_ten_percent:
    qty = 1
    side = 'sell'
    try:
        api.submit_order(short_stock, qty, side, "market", "day")
        print("Market order of | " + str(qty) + " " + short_stock + " " + side + " | completed.")
    except:
        print("Order of | " + str(qty) + " " + short_stock + " " + side + " | did not go through.")
