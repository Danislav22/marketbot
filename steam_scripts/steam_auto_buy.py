import re, time, logging, json, requests, urllib.parse, http.client
from collections import defaultdict
from datetime import datetime
from path import Path
import sys

sys.path.append(Path(__file__).parent.parent)
from secret_data.steam_cookies import cookies as COOKIES
from secret_data.headers import headers as HEADERS
from settings import steam_auto_buy_path


CURRENCY = {
    "Russia": {
        "country": "RU",
        "currency": 5
    },
    "Kazahstan": {
        "country": "KZ",
        "currency": 37
    },
}

COUNTRY = 'Russia'

log = logging.getLogger(__name__)

MARKET_URL = u"http://steamcommunity.com/market/"
MARKET_SEARCH_URL = MARKET_URL + "search/render/{args}"
STEAM_GROUP_LIST_URL = u"http://steamcommunity.com/groups/{id}/memberslistxml/?xml=1"

LIST_ITEMS_QUERY = u"http://steamcommunity.com/market/search/render/?query={query}&start={start}&count={count}&search_descriptions=0&sort_column={sort}&sort_dir={order}&appid={appid}"
ITEM_PRICE_QUERY = u"http://steamcommunity.com/market/priceoverview/?country=US&currency=1&appid={appid}&market_hash_name={name}"
ITEM_PAGE_QUERY = u"http://steamcommunity.com/market/listings/{appid}/{name}"
INVENTORY_QUERY = u"http://steamcommunity.com/profiles/{id}/inventory/json/{app}/{ctx}"
INVENTORY_STE_QUERY = u"https://steamcommunity.com/inventory/{id}/{app}/{ctx}?&count={count}&start_assetid="
BULK_ITEM_PRICE_QUERY = u"/market/itemordershistogram?country={country}&language=english&currency={currency}&item_nameid={nameid}&two_factor=0"
MARKET_LISTED_QUERY = u"https://steamcommunity.com/market/mylistings/render/?query=&norender=1&start={start}&count={count}"
CANCEL_BUYORDER_QUERY = u"https://steamcommunity.com/market/cancelbuyorder/"
SET_BUYORDER_QUERY = u"https://steamcommunity.com/market/createbuyorder/"

steam_id_re = re.compile('steamcommunity.com/openid/id/(.*?)$')
class_id_re = re.compile('"classid":"(\\d+)"')
name_id_re = re.compile('Market_LoadOrderSpread\( (\\d+) \)\;')
# ошибка с куками это вроде 429 код
#requests.exceptions.ConnectTimeout: HTTPSConnectionPool(host='steamcommunity.com', port=443): Max retries exceeded with url: /market/listings/730/StatTrak%E2%84%A2%20SSG%2008%20%7C%20Ghost%20Crusader%20%28Well-Worn%29 (Caused by ConnectTimeoutError(<urllib3.connection.HTTPSConnection object at 0x00000162A154BB90>, 'Connection to steamcommunity.com timed out. (connect timeout=None)'))
def get_item_meta(item_name: str):
    item_name = urllib.parse.quote(item_name, safe="™")
    for i in range(10):
        r = requests.get(ITEM_PAGE_QUERY.format(appid=730, name=item_name), headers=HEADERS, cookies=COOKIES)
        print(r.status_code)
        text = r.content.decode('utf-8')
        name_id = name_id_re.findall(text)
        class_id = class_id_re.findall(text)
        if class_id:
            print('получил класс айди')
            break
    class_id = int(class_id[0])
    name_id = int(name_id[0]) if len(name_id) else None
    print (f"get_item| {name_id} {class_id}")
    return name_id, class_id


def get_bulkitem_price_old(item_name, country = COUNTRY):
    r = requests.get(BULK_ITEM_PRICE_QUERY.format(
        nameid=get_item_meta(item_name)[0],
        country=CURRENCY[country]['country'],
        currency=CURRENCY[country]['currency'], headers=HEADERS, cookies=COOKIES)
            )
    print(r.status_code)
    r = r.json()
    buy_order_graph = r["buy_order_graph"][0]
    price = buy_order_graph[0]
    quantity = buy_order_graph[1]
    print(f'get_bulitem | {price} {quantity}')
    return price, quantity


def get_bulkitem_price(item_name, country = COUNTRY):
    conn = http.client.HTTPSConnection("steamcommunity.com")
    conn.request("GET", BULK_ITEM_PRICE_QUERY.format(
        nameid=get_item_meta(item_name)[0],
        country=CURRENCY[country]['country'],
        currency=CURRENCY[country]['currency']), headers=HEADERS)
    res = conn.getresponse()
    data = res.read()
    data = json.loads(data)
    buy_order_graph = data["buy_order_graph"][0]
    price = buy_order_graph[0]
    quantity = buy_order_graph[1]
    print(f'get_bulitem | {price} {quantity}')
    return price, quantity


def show_buyorders_info(start=0, count=0):
    r = requests.get(MARKET_LISTED_QUERY.format(start=start, count=count),
                     headers=HEADERS, cookies=COOKIES)
    print(r.status_code)

    buy_orders = r.json().get('buy_orders', [])
    result = {
        order['hash_name']: {
            'order_id': order['buy_orderid'],
            'price': float(order['price']) / 100,
            'quantity': order['quantity']
            } for order in buy_orders
        }
    print(result)
    return result


def delete_buyorder(order_id=None):
    data = {
        'sessionid': COOKIES['sessionid'],
        'buy_orderid': int(order_id),
    }
    r = requests.post(CANCEL_BUYORDER_QUERY,
                      data=data, headers=HEADERS, cookies=COOKIES)
    print(r.status_code)
    print(f"delete_buyorder | {r.content} {r.status_code}")
    return r.content, r.status_code
    # {'success': 1}

 
def set_buyorder(item_name: str,
                 price: int | float,
                 quantity=1,
                 country = COUNTRY,
                 limit_price=None):
    data = {
        "sessionid": COOKIES['sessionid'],
        "currency": CURRENCY[country]['currency'],
        "appid": 730,
        "market_hash_name": item_name,
        "price_total": int(price * quantity * 100),
        "quantity": quantity,
        "billing_state": '',
        "save_my_address": 0
    }
    r = requests.post(SET_BUYORDER_QUERY, cookies=COOKIES, headers=HEADERS, data=data)
    print(r.status_code)
    print(f"set_buyorder | {r.content} {r.json()}")
    return r.content, r.json()


def check_inventory(id=None, app=730, ctx=2, count=5000):
    if not id:
        id = COOKIES['steamLoginSecure'].split('%')[0]
    r = requests.get(INVENTORY_STE_QUERY.format(
        id=id,
        app=app,
        ctx=ctx,
        count=count),
        cookies=COOKIES,
        headers=HEADERS
        )
    print(r.status_code)
    list = [item['market_hash_name'] for item in r.json()['descriptions']]
    result = defaultdict(int)
    for i in list:
        result[i] += 1
    print(f"check_inventory | {result}")
    return result

def main():
     # Удаляем все автобаи
    print('Удаляю все ордера...')
    count = 0
    for item_name, item_info in show_buyorders_info().items():
        count += 1
        order_id = item_info['order_id']
        delete_buyorder(order_id)
        print(f'Удалил ордер на предмет: {item_name}')
        time.sleep(3)
    print(f'Удалил {count} ордеров')

    data = {}
    with open('items.txt', 'r', encoding='utf-8') as file:  # Парсим все элементы из файла и добавляем в словарь data
        for line in file:
            parts = line.strip().split('/')

            name = parts[0]
            data[name] = {
                'count': int(parts[1]) if parts[1] else 1,
                'price_limit': float(parts[2]) if parts[2] else float('inf'),
            }
    inventory_dict = check_inventory()
    keys_to_remove = []
    for key, value in data.items():
        if key in inventory_dict:
            value['count'] = value['count'] - inventory_dict[key]
            if value['count'] <= 0:  # Записываем все ключи, которые в дальнейшем собираемся удалить
                keys_to_remove.append(key)
    for key in keys_to_remove:  # Удаляем все значения из data по ключу
        del data[key]
    print('Начинаю выставлять ордера')
    while True:
        buyorders_dict = show_buyorders_info()
        for key, value in data.items():
            bulkitem_info = get_bulkitem_price(key)
            if key in buyorders_dict:  # Если на предмет уже выставлен автобай
                if bulkitem_info[0] == buyorders_dict[key]['price']:  # Проверка на то, что предмет уже имеет самую высокую позицию
                    print(f'На предмет: {key} стоит самый высокий ордер по цене - {bulkitem_info[0]}')
                    continue
                if value['price_limit'] > bulkitem_info[0]:
                    delete_buyorder(buyorders_dict[key]['order_id'])
                    time.sleep(3)
                    set_buyorder(key, bulkitem_info[0]+1)
                    print(f'Обновил ордер на предмет: {key} по цене {bulkitem_info[0] + 1} | ПРОШЛАЯ ЦЕНА {bulkitem_info[0]}')
            else:
                if value['price_limit'] > bulkitem_info[0]:
                    set_buyorder(key, bulkitem_info[0]+1)
                    print(f'Выставил ордер на предмет: {key} по цене {bulkitem_info[0] + 1} | ПРОШЛАЯ ЦЕНА {bulkitem_info[0]}')
            time.sleep(3)
        print("Начинаю новый цикл...")
        time.sleep(60)


def main():
    data = {}
    with open(steam_auto_buy_path, 'r', encoding='utf-8') as file:  # Парсим все элементы из файла и добавляем в словарь data
        for line in file:
            parts = line.strip().split('/')
            if len(parts) == 1:
                data[parts[0]] = {
                'count': 1,
                'price_limit': float('inf'),
            }
            elif len(parts) == 3:
                name = parts[0]
                data[name] = {
                    'count': int(parts[1]) if parts[1] else 1,
                    'price_limit': float(parts[2]) if parts[2] else float('inf'),
                }
            
    inventory_dict = check_inventory()
    keys_to_remove = []
    for key, value in data.items():
        if key in inventory_dict:
            value['count'] = value['count'] - inventory_dict[key]
            if value['count'] <= 0:  # Записываем все ключи, которые в дальнейшем собираемся удалить
                keys_to_remove.append(key)
    for key in keys_to_remove:  # Удаляем все значения из data по ключу
        del data[key]
    print('Начинаю выставлять ордера')
    while True:
        buyorders_dict = show_buyorders_info()
        for key, value in data.items():
            bulkitem_info = get_bulkitem_price(key)
            new_buyorder = (bulkitem_info[0] * 100 + 1) / 100 
            if key in buyorders_dict:               # Если на предмет уже выставлен автобай

                if bulkitem_info[0] <= buyorders_dict[key]['price']:  # Проверка на то, что предмет уже имеет самую высокую позицию
                    print(f'На предмет: {key} стоит самый высокий ордер по цене - {bulkitem_info[0]} | {buyorders_dict[key]["price"]}')
                    time.sleep(5)
                    continue
                if value['price_limit'] > bulkitem_info[0]:
                    delete_buyorder(buyorders_dict[key]['order_id'])
                    time.sleep(3)
                    set_buyorder(key, new_buyorder)
                    print(f'Обновил ордер на предмет: {key} по цене {new_buyorder} | ПРОШЛАЯ ЦЕНА {bulkitem_info[0]}')
            else:
                if value['price_limit'] > bulkitem_info[0]:
                    set_buyorder(key, new_buyorder)
                    print(f'Выставил ордер на предмет: {key} по цене {new_buyorder} | ПРОШЛАЯ ЦЕНА {bulkitem_info[0]}')
            time.sleep(5)
        time.sleep(1800)

if __name__ == '__main__':
    main()