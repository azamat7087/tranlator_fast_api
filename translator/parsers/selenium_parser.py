import time

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


class SeleniumParser:

    def __init__(self, domain: str, from_lang: str, to_lang: str, text: str):
        options = Options()
        # options.add_argument("--headless")
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        self.from_lang = from_lang
        self.to_lang = to_lang
        self.text = text
        self.domain = self.set_domain(domain)

    def set_domain(self, domain):
        return f"{domain}{self.from_lang}/{self.to_lang}/{self.text}"

    def load_page(self):
        self.driver.get(self.domain)
        return self.translate_text()

    def close_driver(self):
        self.driver.close()

    def translate_text(self):
        translation = self.driver.find_element(by=By.ID, value="target-dummydiv")
        print(translation.text)
        return translation.text


def translate_text(from_lang: str, to_lang: str, text: str):
    parser = SeleniumParser(domain="https://www.deepl.com/ru/translator#", from_lang=from_lang, to_lang=to_lang, text=text)

    try:
        return {"text": parser.load_page()}
    finally:
        parser.close_driver()


# from translate import translator
#
# for i in range(100):
#     print(translator('en', 'zh-TW', 'Hello World!'))
