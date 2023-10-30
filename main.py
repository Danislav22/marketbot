import datetime as dt

from market import ping, put_on_sale, change_prices, auto_buy, get_filters_skins_table, make_request
from chrome_parser import Parser
from steam_scripts.steam_history_parser import parse_steam_history, write_items
from secret_data.API_KEY import API_KEY
from secret_data.API_KEY import API_KEYS_FARM
from settings import RATIO, SERVICES, working_dir

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
        "[y] Перекинуть баланс между аккаунтами\n"
        "[a] Обновить куки стима\n"
        "[b] Обновить куки таблицы (для аккаунты, где есть подписка на таблицу)\n"
        "[c] Спарсить историю покупок в стиме (20000 последних действий)\n"
        "[d] Включить автопокупку стима\n"
    )

    if '1' in type_action:
        put_on_sale()

    if '2' in type_action:
        delta = dt.timedelta(hours=1)
        last_updated = dt.datetime.now()
        while True:
            if last_updated+delta <= dt.datetime.now():
                global RATIO
                RATIO -= 0.02
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
            save_path=working_dir + '\\filters.txt',
            scrolls=1,
            save_only_name=False,
        )
    
    output_message = '{key}: {value}'
    if 'y' in type_action:
        accounts = {
            'main': API_KEY,
            **API_KEYS_FARM
        }
        # Вывод сообщения на печать
        print('Выберите аккаунт ОТКУДА отправлять средства')
        for key,value in accounts.items():
            print(output_message.format(key=key, value=value))

        acc_from = input()
        while acc_from not in accounts:
            acc_from = input('Введите имя аккаунта из списка!\n')
        key_from = accounts.pop(acc_from)

        # Вывод сообщения на печать
        print('Выберите аккаунт КУДА отправлять средства')
        for key,value in accounts.items():
            print(output_message.format(key=key, value=value))
        acc_to = input()
        while acc_to not in accounts:
            acc_to = input('Введите имя аккаунта из списка!\n')

        key_to = accounts.pop(acc_to)
        amount = input('Введите сумму перевода в копейках:\n')
        pass_from = input('Введите платежный пароль аккаунта С КОТОРОГО отправляете:\n')
        make_request(
            request=f'money-send/{amount}/{key_to}',
            params={
                'pay_pass': pass_from,
                'key': key_from,
            }
        )

    if 'a' in type_action:
        Parser().save_cookie(
            link=SERVICES.get('steam').get('link'),
            path=SERVICES.get('steam').get('path')
        )

    if 'b' in type_action:
        Parser(table=True).save_cookie(
            link=SERVICES.get('table').get('link'),
            path=SERVICES.get('table').get('path')
        )
    
    if 'c' in type_action:
        write_items(items=parse_steam_history(count=20000))


if __name__ == "__main__":
    main()