from path import Path

# Имя браузера, пока не используется
BROWSER_NAME = 'Chrome'
# Имя профиля браузера, которое будет запускать селениум,
# по стандарту Default
PROFILE_NAME = 'Profile 24'

# Настройки для парсинга стима и таблицы
SERVICES = {
    'steam': {
        'link':'https://steamcommunity.com/market/',
        'path': 'secret_data/steam_cookies.py'
    },
    'table': {
        'link':'https://skins-table.xyz/',
        'path': 'table_cookies.py'
    }
}

RATIO = 0.82
DEFAULT_CUR_MARKET = 'RUB' # курс валюты на market_csgo

# Пока не используется, нужен будет для фильтра имен,
# полученных с таблицы
trash_part_names = ['capsule', 'patch', 'pin', 'sticker']
working_dir = Path(__file__).parent # рабочая папка, нужна для сохранения остальных файлов
                                    # в данный момент это - c:\DanislavScripts\marketbot

steam_history_path = Path(__file__).parent / 'steam_history.txt'
steam_auto_buy_path = Path(__file__).parent / "steam_items_name_to_buy.txt"