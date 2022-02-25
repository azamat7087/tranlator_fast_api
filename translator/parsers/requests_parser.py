from bs4 import BeautifulSoup
import requests

HEADERS = {
        'user-agent': 'Mozilla/4.0',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'}


class RequestsParser:

    def __init__(self, domain: str, from_lang: str, to_lang: str, text: str):
        self.from_lang = from_lang
        self.to_lang = to_lang
        self.text = text
        self.domain = self.set_domain(domain)

    def set_domain(self, domain):
        return f"{domain}?hl={self.to_lang}&sl={self.from_lang}&tl={self.to_lang}&text={self.text}&op=translate"

    @staticmethod
    def find_translation(html):
        soup = BeautifulSoup(html, 'html.parser')
        print(soup)
        translation = soup.findAll("span", {"data-complaint-type": "fullTextTranslation"})
        print(translation)
        return translation

    def translate_text(self):
        translation = requests.get(self.domain, headers=HEADERS, )
        translation = self.find_translation(translation.text)
        return translation


def translate_text(from_lang: str, to_lang: str, text: str):
    parser = RequestsParser(domain="https://translate.google.com/", from_lang=from_lang, to_lang=to_lang, text=text)

    return {"text": parser.translate_text()}

print(translate_text(from_lang="en", to_lang="ru", text="Hello"))
