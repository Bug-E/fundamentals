import csv
import requests
import json

checked_ids = set()
URL = 'https://www.screener.in/api/company/{company_id}/chart/?q=Price-DMA50-DMA200-Volume&days=365'

print('stock-id,date,price')


def fetch_price(stock_id):

    url = URL.format(company_id = stock_id)

    json_data = requests.get(url).json()
    datasets = json_data['datasets']

    for d in datasets:
        metric = d['metric']
        if metric != 'Price':
            continue
        values = d['values']
        for v in values:
            date, price = v[0], float(v[1])
            print(stock_id + ',' + date + ',' + price)


with open('../stocks.csv') as stock_csv:
    reader = csv.DictReader(stock_csv)
    for row in reader:
        stock_id = row['data-company-id']
        if not stock_id:
            continue
        if stock_id in checked_ids:
            continue
        fetch_price(stock_id)
        checked_ids.add(stock_id)
