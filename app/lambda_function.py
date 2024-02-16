"""Scraping Telegram channel functions"""

import logging
import re
import sys
from enum import StrEnum
from pprint import pformat
from typing import List, Optional

sys.path.append("package")

import requests
from bs4 import BeautifulSoup
from requests import Response

# pylint: disable=broad-except

logger = logging.getLogger()
logger.setLevel("ERROR")


class Source(StrEnum):
    """Source telegram channel URLs which are reachable from a browser"""

    PARALELO = "https://t.me/s/enparalelovzlatelegram?q=%25+Bs+"
    BCV = "https://t.me/s/Alertas24?q=d%C3%B3lar+oficial+cierra+la+jornada"


class Html(StrEnum):
    """HTML parser constants"""

    PARSER = "lxml"
    CLASS = "class"
    TARGET_TAG = "div"
    TARGET_CLASS = "tgme_widget_message_text"


class ScraperException(Exception):
    """Exception occurred on scraper module"""


def _extract_rate(text: str, start: Optional[str] = None) -> float:
    """
    Get rate from text, using regex.
    :param text: String with text (str).
    :param start: Substring to start from (str).
    :return: Exchange rate (float).
    """
    patterns = (r"[ ]\d{1,2}[.,]\d{1,2}", r"\d{1}[.,]\d{1,2}")
    if start and start in text:
        text = text[text.find(start) :]
    for pat in patterns:
        match = re.search(pat, text, flags=0)
        if match:
            number = re.findall(pat, text, flags=0)[0]
            return float(number.replace(",", "."))
    raise ScraperException(f"No match found in: {text}")


def _get_page(url: str) -> Response:
    """
    Get source code of the web page.
    :param url: URL of the webpage (str).
    :return: Response object (requests.Response).
    :raises: ScraperException If fails.
    """
    res = requests.get(url=url, timeout=30)
    if res.status_code == 200:
        return res
    raise ScraperException(f"Code: {res.status_code}. Reason: {res.reason}")


def _parse_channel(
    source_url: str, page_content: Optional[str] = None
) -> Optional[List[str]]:
    """
    Parse paralelo telegram channel and return last rate messages.
    :param source_url: URL of the webpage (str).
    :param page_content: Webpage content for tests (str).
    :return: Messages from channel (List[str]).
    """
    result = []
    page = page_content if page_content else _get_page(source_url)
    if page is None:
        return None
    soup = BeautifulSoup(page.text, Html.PARSER)
    divs = soup.find_all(Html.TARGET_TAG)
    for div in divs:
        if Html.TARGET_CLASS in div[Html.CLASS]:
            result.append(div.text)
    return result


def get_paralelo_rate(text: Optional[str] = None) -> Optional[float]:
    """
    Get PARALELO rate from a telegram channel.
    :param text: Message from channel (str).
    :return: Exchange rate (float).
    """
    try:
        if text is None:
            items: List[str] = _parse_channel(source_url=Source.PARALELO)
            # Check the latest 4 messages
            for i in range(5):
                text = items[-1 - i]
                result = _extract_rate(text.lower(), "bs. ")
                if result:
                    return result
        return _extract_rate(text, "bs. ")
    except ScraperException as ex:
        logger.exception(pformat(ex))
        return None


def get_bcv_rate(text: Optional[str] = None) -> Optional[float]:
    """
    Get BCV rate from a telegram channel.
    :param text: Message from channel (str).
    :return: Exchange rate (float).
    """
    try:
        text = text if text else _parse_channel(source_url=Source.BCV)[-1]
        return _extract_rate(text.lower())
    except ScraperException as ex:
        logger.exception(pformat(ex))
        return None


def lambda_handler(event, context):
    """AWS Lambda handler"""
    return {
        "statusCode": 200,
        "message": {
            "bcv_rate": get_bcv_rate(),
            "paralelo_rate": get_paralelo_rate(),
        },
        "headers": {
            "Content-Type": "application/json",
        },
    }


if __name__ == "__main__":
    pass
