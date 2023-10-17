from bs4 import BeautifulSoup
from dataclasses import dataclass
import datetime as dt
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from sys import exit
from time import sleep
import path

from data import filters, filter_pattern
from secret_data.API_KEY import API_KEY
from currencies import CURRENCIES
from secret_data.cookies import table_cookie

# Ошибка Not money
# Ответ сервера: {'success': False, 'error': 'Not money'}
# {'success': False, 'error': 'Not money'}
# Название: Revolution Case
# Цена: 89.0
# ID: 4537666177


RATIO = 0.85
phase_list = [
    'phase1',
    'phase2',
    'phase3',
    'phase4',
    'sapphire',
    'ruby',
    'emerald',
    'blackpearl'
]
skins_table_bad_names_lowercase = ['capsule', 'patch', 'pin', 'sticker']


@dataclass
class SkinsTable:
    SLEEP_TIME_SEC = 5
    DRIVER_PATH = 'C:/DanislavScripts/chromedriver.exe'
    SAVE_PATH = r'C:\DanislavScripts\marketbot\steam_history.txt\filters.txt'
    CHECKED_COOKIES_LAST_TIME = None

    filter_name: str = 'steam_auto_market_avg'
    scrolls: int = 1
    save_only_name: bool = True

    # Просто парсим все предметы
    def parse(self):
        driver = webdriver.Chrome(SkinsTable.DRIVER_PATH)
        try:
            driver.get('https://skins-table.xyz/')
            cookies = filter_pattern | filters[self.filter_name] | table_cookie
            for cookie in cookies:
                driver.add_cookie({'name': cookie, 'value': cookies[cookie]})
            driver.get('https://skins-table.xyz/table/')
            driver.find_element(By.XPATH, '//*[@onclick="setsort(4);"]').click()  #Отсортировать вещи по процентам
            sleep(SkinsTable.SLEEP_TIME_SEC)
            #Листаем страницу в самый низ scrolls раз для прогрузки всех вещей
            for i in range(self.scrolls):
                driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);"
                )
                sleep(SkinsTable.SLEEP_TIME_SEC)
        except Exception as ex:
            print(ex)
        finally:
            driver.close()
            driver.quit()

    # Функция проверки куки на работоспособность
    def check_cookies(self):
        ...
        SkinsTable.CHECKED_COOKIES_LAST_TIME = dt.datetime.now()


def get_filters_skins_table(
        filter_name: str = 'steam_auto_market_avg',
        scrolls: int = 1,
        save_path: str = path.Path(__file__).parent + '\item_names_to_import.txt',
        driver_path: str = 'C:/DanislavScripts/chromedriver.exe',
        time_sleep: int = 5,
        save_only_name: bool = True,
    ) -> None:
    driver = webdriver.Chrome()
    try:
        driver.get('https://skins-table.xyz/')
        cookies = filter_pattern | filters[filter_name] | table_cookie
        for cookie in cookies:
            driver.add_cookie({'name': cookie, 'value': cookies[cookie]})
        driver.get('https://skins-table.xyz/table/')
        driver.find_element(By.XPATH, '//*[@onclick="setsort(4);"]').click()  #Отсортировать вещи по процентам
        sleep(time_sleep)
        #Листаем страницу в самый низ scrolls раз для прогрузки всех вещей
        for i in range(scrolls):
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            sleep(5)
        
        data=BeautifulSoup(driver.page_source, "lxml").tbody
        #Словарь для формирования пары значений ИМЯ:Цена со первого сервиса скорректированная
        items = {}

        if not save_only_name:
            k = int(input(
                'Какой процент перевода с первого сервиса на стим '
                'в % (2 - цена будет на 2 процента ниже): \n')
            )
        else:
            k = 0

        #Сохранение имени и цены с страницы таблицы
        for item in data:
            name = item.find('td', class_='clipboard').text.strip()
            prices = item.find_all('span', class_='price-value')
            first_service = float(prices[0].text.strip())
            second_service = float(prices[1].text.strip())
            items[name] = round(second_service*0.87*(1-k/100)*CURRENCIES['USD'], 2)
        
        #Записываем имена или имена/цену покупки в txt файл
        if save_only_name:
            try:
                with open(save_path, 'w', encoding='UTF-8') as f:
                    for name in items:
                        f.write(
                            (name + f'/{items[name]}' + '\n')
                            if not save_only_name
                            else name + '\n'
                        )
            except IOError:
                print('Failure')
        else:
            try:
                with open(save_path, 'w', encoding='UTF-8') as f:
                    for name in items:
                        f.write(
                            (name + f'///{items[name]}/' + '\n')
                            if not save_only_name
                            else name + '\n'
                        )
            except IOError:
                print('Failure')
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


class Items():
    items = []
    len_items_on_sell = 0
    def __init__(self, name, id, price=None, min_price=0):
        self.name = name
        self.id = id
        self.price = int(price*float(100))
        self.min_price = int(min_price*float(100))
        Items.items.append(self)


def ping() -> bool:
    #{'success': True, 'ping': 'pong', 'online': True, 'p2p': True, 'steamApiKey': True}
    return True #Узнать ошибки и начать их обрабатывать, на возврате False вырубать скрипт, проблема в чем-то


DEFAULT_CUR_MARKET = 'RUB'

def make_request(
        request: str,
        item_name: str|list = None,
        cur: str = DEFAULT_CUR_MARKET,
        price: str|int = None,
        item_id: str = None,
        params: dict = {},
    ) -> dict:
    if not params:
        params = (
            {
                'key': f'{API_KEY}',
                'list_hash_name[]': tuple(item_name)
            }
            if type(item_name) is list else
            {
                'hash_name': f'{item_name}',
                'key': f'{API_KEY}',
                'item_id':f'{item_id}',
                'price':f'{price}',
                'cur':f'{cur}',
            }
        )
    response = requests.get(f'https://market.csgo.com/api/v2/{request}', params)
    count = 0
    while not (
            response.headers["content-type"].strip().startswith("application/json") and
            response.status_code == 200
        ):
        count += 1
        if count == 3:
            if not ping():
                exit()
        response = requests.get(f'https://market.csgo.com/api/v2/{request}', params)
    if 'error' in response.json():
        print(f'Ошибка {response.json()["error"]}\nОтвет сервера: {response.json()}')
    print(response.json())
    return response.json()


def items_on_sell():
    return make_request('items').get('items')

status = { #Пока не используется но надо добавить действия по статусу предмета
    '1': 'Item is set for sale.',
    '2': 'You sold the item and must give it to the bot.',
    '3': 'Waiting for the transfer of the item you bought from the seller to the bot.',
    '4': 'You can pick up the purchased item.'
}

buy_history_path = 'C:\DanislavScripts\MarketBot\steam_history.txt'

def refresh_items(cur: int|float = CURRENCIES['RUB']) -> None:
    Items.items = []
    buy_history_data = open(buy_history_path, 'r', encoding='utf-8').readlines()
    buy_history_dict = {}

    items = items_on_sell()

    if items:
        for item in buy_history_data:
            data = item.split("/")
            name = data[0]
            price = data[1]
            buy_history_dict[name] = int(float(price)*cur)
        for i in items:
            if i['status'] == '1':
                if buy_history_dict.get(i['market_hash_name']):
                    Items(i['market_hash_name'],
                        i['item_id'], i['price'],
                        buy_history_dict[i['market_hash_name']]*RATIO)
                else:
                    print(('Предмет {} не имеет цену покупки и будет всегда '
                           'продаваться на 1 копейку').format(i['market_hash_name']))
                    Items(i['market_hash_name'], i['item_id'], i['price'])


def get_market_items(names: list[str] = []) -> dict:
    result = {}
    list_of_items = [names[x:x+50] for x in range (0, len(names), 50)]
    for i in list_of_items:
        result.update(
            make_request(
                request='search-list-items-by-hash-name-all',
                item_name=i).get('data')
        )
    
    return result


def change_prices() -> None:
    refresh_items()
    list_of_actual_items = get_market_items(
        [self.name for self in Items.items]
        )
    print([self.name for self in Items.items])
    for skin in Items.items:
        sleep(0.6)
        market_item = list_of_actual_items[skin.name]
        if len(market_item) < 2:
            new_price = skin.min_price
            make_request('set-price', item_name=skin.name, item_id=skin.id, price=new_price)
            print(f'{skin.name} Продается по минимально допустимой цене {new_price/100}')
            skin.price = new_price
            continue
        second_price = int(market_item[1]['price'])
        first_id = str(market_item[0]['id'])
        first_price = int(market_item[0]['price'])

        if ((first_id == skin.id and skin.price == second_price-1) or
        (skin.price == skin.min_price and first_id != skin.id)):
            ...
        elif skin.price < skin.min_price:
            new_price = skin.min_price
            make_request('set-price', item_name=skin.name, item_id=skin.id, price=new_price)
            print(f'{skin.name} Продается по минимально допустимой цене {new_price/100}')
            skin.price = new_price
        elif first_id == skin.id:
            new_price = second_price-1
            make_request('set-price',item_name=skin.name, item_id=skin.id, price=new_price)
            print(f'Поменял цену {skin.name} с {skin.price/100} на {new_price/100}')
            skin.price = new_price
        elif first_id != skin.id and first_price <= skin.min_price and skin.price != skin.min_price:
            new_price = skin.min_price
            make_request('set-price',item_name=skin.name, item_id=skin.id, price=new_price)
            print(f'{skin.name} стоит по минимальной цене {new_price/100}')
            skin.price = skin.min_price
        elif first_id != skin.id and first_price > skin.min_price and skin.price != skin.min_price:
            new_price = first_price-1
            make_request('set-price', item_name=skin.name, item_id=skin.id, price=new_price)
            print(f'Поменял цену {skin.name} с {skin.price/100} на {new_price/100}')
            skin.price = new_price


def put_on_sale() -> None:
    refresh_items()
    items_on_sell = [self.name for self in Items.items]
    request = make_request('my-inventory')['items']
    for item in request:
        if item not in items_on_sell:
            make_request('add-to-sale',
                        params={
                            'key': API_KEY,
                            'id': item['id'],
                            'cur': 'RUB',
                            'price': 314150000
                            })
            sleep(0.2)
        print(f'Успешно добавлен предмет {item["market_hash_name"]} на продажу')


def auto_buy():
    path_filters = path.Path(__file__).parent + r'\filters.txt'
    try:
        filters = open(path_filters, 'r', encoding='utf-8')
    except:
        print(f"Такого файла по пути {path} не существует")

    filters_data = filters.readlines()

    list_of_names = []

    for line in filters_data:
        data = line.split("/")
        name = data[0]

        if name not in list_of_names:
            list_of_names.append(name)
    for i in range(1500000):
        sleep(3)
        actual_data_for_items_list = get_market_items(list_of_names)
        for line in filters_data:
            data = line.split("/")
            name = data[0]


            try:
                min_float = float(data[1])
            except:
                min_float = 0

            try:
                max_float = float(data[2])
            except:
                max_float = 1
            
            try:
                max_price = float(data[3])*100
            except:
                max_price = 999999999

            
            try:
                phase_filter = data[4].strip()
                if phase_filter not in phase_list:
                    phase_filter = None
            except:
                phase_filter = None
            
            
            
            if len(actual_data_for_items_list)==0:
                print('Нету предметов по заданным именам')
                break
            
            item_exists = 1
            try:
                actual_item_data = actual_data_for_items_list[name]
            except KeyError:
                item_exists = 0

            if item_exists == 1:
                for item in actual_item_data:
                    item_id = item['id']
                    item_price = int(item['price'])
                    item_phase = item['extra'].get('phase')
                    

                    float_of_item_on_market = item['extra'].get('float')
                    if float_of_item_on_market != None and phase_filter != None:
                        float_of_item_on_market = float(item['extra'].get('float'))

                        if (item_price <= max_price and
                            min_float <= float_of_item_on_market <= max_float and
                            item_phase == phase_filter):
                            print(f'Название: {name}|| {item_phase}\n'
                                f'Цена: {item_price/100} Флоат: {float_of_item_on_market}\n'
                                f'ID: {item_id}\n')
                            
                    if float_of_item_on_market != None and phase_filter == None:
                        float_of_item_on_market = float(item['extra'].get('float'))

                        if (item_price <= max_price and
                            min_float <= float_of_item_on_market <= max_float):
                            print(f'Название: {name}\n'
                                f'Цена: {item_price/100} Флоат: {float_of_item_on_market}\n'
                                f'ID: {item_id}\n')
                    
                    if float_of_item_on_market == None and phase_filter != None:

                        if (item_price <= max_price and
                            item_phase == phase_filter):
                            print(
                                f'Название: {name}|| {item_phase}\n'
                                f'Цена: {item_price/100}\n'
                                f'ID: {item_id}\n'
                            )

                    if float_of_item_on_market is None and phase_filter is None:
                        if max_float == 1 and min_float == 0 and item_price <= max_price:
                            print(f'Название: {name}\n'
                                f'Цена: {item_price/100}\n'
                                f'ID: {item_id}\n')
                            make_request('buy', params={'key':API_KEY, 'id': item_id, 'price':item_price})


def main():
    ping()
    type_action = input(
        "Выберите действие:\n"
        "[1] Выставить предметы на продажу\n"
        "[2] Обновление цен\n"
        "[3] Найти вещи по фильтрам\n"
        "[4] Получить список предметов для покупки с маркета на buff (CASES)\n"
        "[5] Получить список предметов для покупки с маркета на buff (SKINS)\n"
        "[6] Получить список предметов для выставления АВТОПОКУПКИ на самом BUFF\n"
        "[7] Получить список предметов для ПОКУПКИ на самом BUFF\n"
        "[8] Покупка кейсов с маркета на стим (Market -> Steam Auto)\n"
        "[9] Спарсить вещи из Skinstable для покупки в стиме\n"
        "[z] Сохранить кейсы под процент в стим\n"
    )

    if '1' in type_action:
        put_on_sale()

    if '2' in type_action:
        delta = dt.timedelta(hours=1)
        last_updated = dt.datetime.now()
        while True:
            if last_updated+delta <= dt.datetime.now():
                global RATIO
                RATIO -= 0.01
                last_updated = dt.datetime.now()
            change_prices()
            print('Круг смены цен закончен')

    if '3' in type_action:
        auto_buy()

    if '9' in type_action:
        scrolls = int(input('Сколько нужно прокрутов страницы?\n'))
        save_path = input(
            'Введите желаемый путь сохранения имён предметов\n'
        ).replace('"', '')
        if save_path:
            get_filters_skins_table(save_path=save_path, scrolls=scrolls)
        else:
            get_filters_skins_table(scrolls=scrolls)

    if 'z' in type_action:
        get_filters_skins_table(
            filter_name='market_to_steam_auto_percent',
            save_path=path.Path(__file__).parent + r'\filters.txt',
            scrolls=1,
            save_only_name=False,
        )


if __name__ == "__main__":
    main()
    #print(path.Path(__file__).parent + r'\filters.txt')