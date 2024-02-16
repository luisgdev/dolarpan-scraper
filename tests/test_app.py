""" Test App functions """

import pytest

from app.lambda_function import (
    ScraperException,
    _extract_rate,
    _get_bcv_rate,
    _get_paralelo_rate,
)

BCV_CASES = (
    (
        """
        🚨⬆️💰 AHORA. El dólar oficial cierra la jornada en 36,13.⚠️ 
        Fecha valor: Miércoles 24 de enero.
        """,
        36.13,
    ),
    (
        """
        🚨⬇️💰 AHORA. El dólar oficial cierra la jornada en 36,11⚠️ 
        Fecha valor: Martes 23 de enero.
        ...
        """,
        36.11,
    ),
    ("""🚨⬆️💰 AHORA. El dólar oficial cierra la jornada en 36,20 """, 36.2),
    ("""🚨🟰💰 AHORA. El dólar oficial cierra la jornada en 36,12. """, 36.12),
)

PARALELO_CASES = (
    (
        """
        🗓 29/01/2024
        🕒 12:50 PM
        💵 Bs. 38,01
        🟰 0,00% Bs 0,00
        """,
        38.01,
    ),
    (
        """
        🗓 15/02/2024
        🕒 1:00 PM
        💵 Bs. 37,28
        🔻 0,04% Bs 0,02
        """,
        37.28,
    ),
    (
        """
        🗓 02/02/2024
        🕒 1:08 PM
        💵 Bs. 38,09
        🟰 0,00% Bs 0,00
        """,
        38.09,
    ),
    (
        "'\nEnParaleloVzla\n🗓 02/02/2024🕒 8:50 AM💵 Bs. 38,09🔺 0,35% Bs 0,14\n128.5K views12:47\n",
        38.09,
    ),
)

FAIL_CASES = (
    (""" Publicidad random """, None),
    (""" Dolar en 3612 """, None),
    (""" Dolar en 36-12 """, None),
)


@pytest.mark.parametrize(
    ("text", "result"),
    (BCV_CASES + PARALELO_CASES + FAIL_CASES),
)
def test__extract_rate(text: str, result: float):
    """Test Paralelo function"""
    if not result:
        with pytest.raises(ScraperException):
            _extract_rate(text=text)
    else:
        assert _extract_rate(text=text, start="") == result


@pytest.mark.parametrize(
    ("message", "result"),
    BCV_CASES,
)
def test_get_bcv_rate(message: str, result: float):
    """Test BCV function"""
    assert _get_bcv_rate(text=message).rate == result


@pytest.mark.parametrize(
    ("message", "result"),
    PARALELO_CASES,
)
def test_get_paralelo_rate(message: str, result: str):
    """Test Paralelo function"""
    assert _get_paralelo_rate(text=message).rate == result
