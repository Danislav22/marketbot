import requests

data = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()

CURRENCIES = {
    'RUB': 1,
    'YUAN': data['Valute']['CNY']['Value'],
    'KZT': data['Valute']['KZT']['Value'],
    'USD': data['Valute']['USD']['Value'],
}