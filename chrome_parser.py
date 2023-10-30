from bs4 import BeautifulSoup
from dataclasses import dataclass
import os
from path import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import re
from time import sleep

from settings import PROFILE_NAME
from settings import SERVICES



@dataclass
class Parser:
    BROWSER_PROCESS_NAME = 'chrome.exe'

    table: bool = False
    profile_name: str = PROFILE_NAME

    ARGUMENTS = [
        '--allow-profiles-outside-user-dir',
        '--enable-profile-shortcut-manager',
        f'user-data-dir={os.path.expanduser("~")}\\AppData\\Local\\Google\\Chrome\\User Data',
        f'--profile-directory={PROFILE_NAME}',
        '--remote-debugging-port=9222',
        '--log-level=3',
        '--disable-dev-shm-usage',
        'disable-infobars',
        '--extensions-install-verification',
        '--no-sandbox',
        '--disable-blink-features=AutomationControlled',
        '-lang=en-UK'
    ]

    def write_table_cookies(self, cookies, path):
        string = 'cookies = {\n'
        for i in cookies:
            if '_ga' in i or 'PHP' in i:
                name = i.get("name")
                value = i.get("value")
                string += f'    "{name}": "{value}",\n'
        string += '}'
        with open(path, 'w') as f:
            f.write(string)
        f.close()

    def write_cookies(self, cookies, path):
        string = 'cookies = {\n'
        for i in cookies:
            name = i.get("name")
            value = i.get("value")
            string += f'    "{name}": "{value}",\n'
        string += '}'
        with open(path, 'w') as f:
            f.write(string)
        f.close()

    def kill_chrome(self):
        os.system('taskkill /f /im ' + self.BROWSER_PROCESS_NAME)

    # Готовим браузер хром (в данном случае) со всеми настройками
    def set_up_browser(self):
        options = webdriver.ChromeOptions()
        for option in self.ARGUMENTS:
            options.add_argument(option)
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    # Полностью готовит браузер, достает куки, записывает в path
    def save_cookie(self, link, path):
        self.kill_chrome()
        self.set_up_browser()
        self.driver.get(link)
        sleep(3)
        cookies = self.driver.get_cookies()
        if self.table is False:
            self.write_cookies(cookies=cookies, path=path)
        else:
            self.write_table_cookies(cookies=cookies, path=path)

# Для теста
if __name__ == '__main__':
    # parser = Parser().save_cookie(
    #     link=SERVICES.get('table').get('link'),
    #     path=SERVICES.get('table').get('path')
    # )
    print(f'user-data-dir={os.path.expanduser("~")}\\AppData\\Local\\Google\\Chrome\\User Data')