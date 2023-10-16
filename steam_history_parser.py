from math import ceil
import requests

cookies = {
    'ActListPageSize': '10',
    'enableSIH': 'true',
    'sessionid': '68f9cbad732ff117884212b8',
    '_ga': 'GA1.2.1296801590.1680687301',
    'browserid': '2908803524379670284',
    'timezoneOffset': '25200,0',
    'strInventoryLastContext': '730_2',
    'extproviders_730': 'steam',
    'recentlyVisitedAppHubs': '730%2C47870',
    'app_impressions': '730@2_9_100000_|47870@2_9_100006_100202',
    'Steam_Language': 'english',
    'totalproviders_730': 'buff163',
    'webTradeEligibility': '%7B%22allowed%22%3A1%2C%22allowed_at_time%22%3A0%2C%22steamguard_required_days%22%3A15%2C%22new_device_cooldown_days%22%3A0%2C%22time_checked%22%3A1695962090%7D',
    'steamCurrencyId': '5',
    'steamCountry': 'RU%7Ca5594ea03f0b6083c689120a08771586',
    'steamLoginSecure': '76561198220991936%7C%7CeyAidHlwIjogIkpXVCIsICJhbGciOiAiRWREU0EiIH0.eyAiaXNzIjogInI6MEQyNF8yMjU2NEQ4Rl9GQzkwRiIsICJzdWIiOiAiNzY1NjExOTgyMjA5OTE5MzYiLCAiYXVkIjogWyAid2ViIiBdLCAiZXhwIjogMTY5NzQ2ODg1MCwgIm5iZiI6IDE2ODg3NDEyMDgsICJpYXQiOiAxNjk3MzgxMjA4LCAianRpIjogIjBENkJfMjM0RjcyRDZfNUYyNDkiLCAib2F0IjogMTY4MDY4NzMxNSwgInJ0X2V4cCI6IDE2OTg4OTAzNTMsICJwZXIiOiAwLCAiaXBfc3ViamVjdCI6ICIzNy4yMy4yMjUuMzUiLCAiaXBfY29uZmlybWVyIjogIjM3LjIzLjIyNS4zNSIgfQ.MkZVZQ_XEGxVmpExMP7Ay1LaHyIxHqmimpL8TxTdOTxXx5QIIBP5_1PgNa8QVyGZ_W2QiAZhA7RKn9UqJJXlBw',
}

headers = {
    'Accept': '*/*',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    # 'Cookie': 'sessionid=68f9cbad732ff117884212b8; _ga=GA1.2.1296801590.1680687301; browserid=2908803524379670284; timezoneOffset=25200,0; strInventoryLastContext=730_2; extproviders_730=steam; recentlyVisitedAppHubs=730%2C47870; app_impressions=730@2_9_100000_|47870@2_9_100006_100202; Steam_Language=english; totalproviders_730=buff163; webTradeEligibility=%7B%22allowed%22%3A1%2C%22allowed_at_time%22%3A0%2C%22steamguard_required_days%22%3A15%2C%22new_device_cooldown_days%22%3A0%2C%22time_checked%22%3A1695962090%7D; steamCurrencyId=5; steamCountry=RU%7Ca5594ea03f0b6083c689120a08771586; steamLoginSecure=76561198220991936%7C%7CeyAidHlwIjogIkpXVCIsICJhbGciOiAiRWREU0EiIH0.eyAiaXNzIjogInI6MEQyNF8yMjU2NEQ4Rl9GQzkwRiIsICJzdWIiOiAiNzY1NjExOTgyMjA5OTE5MzYiLCAiYXVkIjogWyAid2ViIiBdLCAiZXhwIjogMTY5Njc0NDk2MiwgIm5iZiI6IDE2ODgwMTczOTAsICJpYXQiOiAxNjk2NjU3MzkwLCAianRpIjogIjBENTRfMjM0NjNEMzJfNjZBQjciLCAib2F0IjogMTY4MDY4NzMxNSwgInJ0X2V4cCI6IDE2OTg4OTAzNTMsICJwZXIiOiAwLCAiaXBfc3ViamVjdCI6ICIzNy4yMy4yMjUuMzUiLCAiaXBfY29uZmlybWVyIjogIjM3LjIzLjIyNS4zNSIgfQ.oqz3-ZldJelK8mZnFQqGmgcQUsnnjaq9zHJyigRqYGiKGNyM0MBUmbrDIkJfHKk5AR0WswlJbuI4bPyXP4vsBg',
    'Referer': 'https://steamcommunity.com/id/profiles1205243233912/inventory/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}
params: dict = {
    'norender':1,
    'query': '',
    'start': 0,
    'count': 500,
}

roles: dict = {
    'Покупатель': 4, #'event_type' в events 3 - я продал кому-то, 4 - я купил у кого-то
    'Продавец': 3,
}

STEAM_ID = '76561198220991936' #Пока не используется, на всякий
# def test_login() -> bool:
#     response = requests.get('https://steamcommunity.com/market/myhistory/', params=params, cookies=cookies, headers=headers)
#     if response.status_code != 200:
#         print('Сервера стим недоступны, попробуйте снова')
#         return False
    
#     soup = BeautifulSoup(response.json()['results_html'], "lxml")
#     message: str = soup.find(class_='market_listing_table_message')
#     if message == None:
#         return True
#     print(message.a.text.strip())
#     if message == 'Login':
#         print('Куки устарели')
#         return False
#     return True
game_ids = {
    'csgo': '730',
    'dota2': '530',
}


def parse_steam_history(
        my_role: str='Покупатель',
        count: int=500,
        game_id=game_ids['csgo']
    ) -> dict:
    if my_role not in roles:
        return (
            'Нет такой роли '
            f'Доступные роли {roles.keys()}'
            )
    if type(count)!=int:
        return (
            'Неправильный тип данных переменной count. '
            f'Нужен int, стоит {type(count)}'
            )
    
    result = {}

    for i in range(ceil(count/params['count'])):
        response = requests.get('https://steamcommunity.com/market/myhistory/', params=params, cookies=cookies, headers=headers)

        events = response.json().get('events')
        purchases = response.json().get('purchases')
        if game_id not in response.json().get('assets'):
            params['start'] += params['count']
            continue
        assets = response.json().get('assets')[game_id]['2'] #'730' - это айди игры кс го

        event_type = roles.get(my_role)
        
        for event in events:
            if event['event_type'] == event_type:
                purchase = purchases.get(event['listingid'] + '_' + event['purchaseid'])
                if purchase['asset']['appid'] != int(game_id):
                    continue
                id = purchase['asset']['id']
                paid = purchase['paid_amount'] + purchase['paid_fee']
                name = assets[id]['market_hash_name']
                result[name] = paid
        params['start'] += params['count']

    return result

def write_items(path: str = 'C:/DanislavScripts/MarketBot/steam_history.txt', items: dict = {}) -> None:
    if type(path)!=str:
        print(
            'Неправильный тип переменной path. '
            f'Стоит {type(path)}, а должен str'
            )
        return ''
    try:
        with open(path, 'w', encoding='UTF-8') as f:
            for name in items:
                f.write(name + f'/{items[name]/100}' + '\n')
    except IOError:
        print('Failure')
    print('Успешно выполнена запись предметов')

write_items(items=parse_steam_history(count=20000))