from math import ceil
import requests
import sys
from path import Path

sys.path.append(Path(__file__).parent.parent)

from secret_data.steam_cookies import cookies
from secret_data.headers import headers
from settings import steam_history_path

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

def write_items(path: str = steam_history_path, items: dict = {}) -> None:
    try:
        with open(path, 'w', encoding='UTF-8') as f:
            for name in items:
                f.write(name + f'/{items[name]/100}' + '\n')
    except IOError:
        print('Failure')
    print('Успешно выполнена запись предметов')

if __name__ == '__main__':
    write_items(items=parse_steam_history(count=20000))