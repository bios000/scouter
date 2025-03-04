from DrissionPage import ChromiumPage, ChromiumOptions
import requests
import time
import cv2
import numpy as np
import pyautogui
from utils.image import image_search


class CloudflareBypass():

    # Welcome to submit a pull request or open an issue to support more language versions.
    language_dict = {
        'en-us': {'title': 'Just a moment'},
        'zh-cn': {'title': '请稍候'},
    }

    image_path_dict = {
        'zh-cn': 'img/zh-cn.jpg'
    }
    
    def __init__(self, browser_path, url):
        self.browser_path = browser_path
        self.url = url
        self.is_clicked = False
        self.image_dict = {}

        for key, value in self.image_path_dict.items():
            self.image_dict[key] = cv2.imread(value)

        # 配置 Chrome 选项
        options = ChromiumOptions().auto_port()
        options.set_paths(self.browser_path)

        args = [
            # "--headless",
            "-no-first-run",
            "-force-color-profile=srgb",
            "-metrics-recording-only",
            "-password-store=basic",
            "-use-mock-keychain",
            "-export-tagged-pdf",
            "-no-default-browser-check",
            "-disable-background-mode",
            "-enable-features=NetworkService,NetworkServiceInProcess,LoadCryptoTokenExtension,PermuteTLSExtensions",
            "-disable-features=FlashDeprecationWarning,EnablePasswordsAccountStorage",
            "-deny-permission-prompts",
            "-disable-gpu",
        ]

        for arg in args:
            options.set_argument(arg)

        self.driver = ChromiumPage(addr_or_opts=options)


    def _is_bypassed(self):
        for dict in self.language_dict.values():
            if dict['title'] in self.driver.title:
                return False
        return True


    def _click_button(self, x, y):
        print('click bypass cloudflare button')
        
        click_x = x + self.driver.rect.page_location[0] + 10
        click_y = y + self.driver.rect.page_location[1] + 10
        print(f'click_x: {click_x}, click_y: {click_y}')

        pyautogui.moveTo(click_x, click_y, duration=0.5, tween=pyautogui.easeInElastic)
        pyautogui.click()

        self.is_clicked = True


    def _cookie_format_convert(self, driver_cookie):
        requests_cookie = ''
        for dict in driver_cookie:
            requests_cookie += f'{dict["name"]}={dict["value"]}; '
        return requests_cookie


    def bypass(self):
        self.driver.get(self.url)

        while not self._is_bypassed():
            image = self.driver.get_screenshot(as_bytes='jpg')
            image = cv2.imdecode(np.frombuffer(image, np.uint8), cv2.IMREAD_COLOR)
            for target in self.image_dict.values():
                coords = image_search(image, target)
                if not self.is_clicked and len(coords) == 1:
                    self._click_button(coords[0][0], coords[0][1])

        user_agent = self.driver.user_agent
        cookie = self.driver.cookies()
        cookie = self._cookie_format_convert(cookie)

        self.driver.quit()

        return user_agent, cookie
