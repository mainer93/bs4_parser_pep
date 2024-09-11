from bs4 import BeautifulSoup
from requests import RequestException

from constants import Tags
from exceptions import ParserFindTagException


def get_response(session, url, encoding='utf-8'):
    try:
        response = session.get(url)
        response.encoding = encoding
        return response
    except RequestException:
        raise ConnectionError(
            f'Возникла ошибка при загрузке страницы {url}'
        )


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        raise ParserFindTagException(error_msg)
    return searched_tag


def fetch_and_parse(session, url):
    response = get_response(session, url)
    if response is None:
        return
    return BeautifulSoup(response.text, features=Tags.LXML)
