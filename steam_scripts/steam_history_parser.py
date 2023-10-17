from math import ceil
import requests

from secret_data.cookies import steam_cookies as cookies
from secret_data.cookies import headers

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

def write_items(path: str = 'C:/DanislavScripts/marketbot/steam_history.txt', items: dict = {}) -> None:
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