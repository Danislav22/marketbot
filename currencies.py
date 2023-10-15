import requests

CURRENCIES = {
    'RUB': 1,
    'YUAN': requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()['Valute']['CNY']['Value'],
    'KZT': 0.2,
}