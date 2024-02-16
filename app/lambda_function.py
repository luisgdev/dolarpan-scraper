"""Scraping Telegram channel functions"""

# pylint: disable=broad-except, wrong-import-position

import logging
import re
import sys
from dataclasses import asdict, dataclass
from enum import StrEnum
from pprint import pformat
from typing import List, Optional

sys.path.append("package")

import requests
from bs4 import BeautifulSoup
from requests import Response

logger = logging.getLogger()
logger.setLevel("ERROR")


N_MSG_TO_CHECK: int = 4


@dataclass
class HasASource:
    """Object that may have a source property"""

    source: Optional[str]

    @classmethod
    def from_instance(cls, instance):
        """Make this dataclass extendable"""
        return cls(**asdict(instance))


@dataclass
class ExchangeRate(HasASource):
    """Exchange rate model"""

    rate: float


@dataclass
class ParsedItem(HasASource):
    """Parsed item model"""

    text: str


class Source(StrEnum):
    """Source telegram channel URLs which are reachable from a browser"""

    PARALELO = "https://t.me/s/enparalelovzlatelegram?q=%25+Bs+"
    BCV = "https://t.me/s/Alertas24?q=d%C3%B3lar+oficial+cierra+la+jornada"


class Html(StrEnum):
    """HTML parser constants"""

    PARSER = "lxml"
    TARGET_TEXT_CLASS = "tgme_widget_message_text"
    TARGET_HREF_CLASS = "tgme_widget_message_photo_wrap"
    TARGET_PARENT_CLASS = "tgme_widget_message_bubble"


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
) -> Optional[List[ParsedItem]]:
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
    divs = soup.find_all("div", class_=Html.TARGET_PARENT_CLASS)
    for i in range(N_MSG_TO_CHECK + 1):
        result.append(
            ParsedItem(
                text=divs[-1 - i]
                .find_all("div", class_=Html.TARGET_TEXT_CLASS)[0]
                .text,
                source=divs[-1 - i]
                .find_all("a", class_=Html.TARGET_HREF_CLASS)[0]
                .get("href"),
            )
        )
    return result


def _get_paralelo_rate(text: Optional[str] = None) -> Optional[ExchangeRate]:
    """
    Get PARALELO rate from a telegram channel.
    :param text: Message from channel (str).
    :return: Exchange rate (float).
    """
    try:
        if text is None:
            items: List[ParsedItem] = _parse_channel(source_url=Source.PARALELO)
            for item in items:
                result = _extract_rate(item.text.lower(), "bs. ")
                if result:
                    return ExchangeRate(rate=result, source=item.source)
        return ExchangeRate(rate=_extract_rate(text, "bs. "), source=None)
    except ScraperException as ex:
        logger.exception(pformat(ex))
        return None


def _get_bcv_rate(text: Optional[str] = None) -> Optional[ExchangeRate]:
    """
    Get BCV rate from a telegram channel.
    :param text: Message from channel (str).
    :return: Exchange rate (ExchangeRate).
    """
    try:
        if not text:
            items = _parse_channel(source_url=Source.BCV)
            for item in items:
                result = _extract_rate(item.text.lower(), "bs. ")
                if result:
                    return ExchangeRate(rate=result, source=item.source)
        return ExchangeRate(rate=_extract_rate(text, "bs. "), source=None)
    except ScraperException as ex:
        logger.exception(pformat(ex))
        return None


def lambda_handler(event, context):
    """AWS Lambda handler"""
    return {
        "statusCode": 200,
        "message": {
            "bcv": asdict(_get_bcv_rate()),
            "paralelo": asdict(_get_paralelo_rate()),
        },
        "headers": {
            "Content-Type": "application/json",
        },
    }


if __name__ == "__main__":
    pass
