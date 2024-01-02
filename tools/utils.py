import re
from typing import Union, Optional


def amount(numb: Union[str, int, float]) -> Optional[int]:
    try:
        numb = re.sub(r'[rkкл]', 'к', str(numb).lower().replace(',', ''))
        ks = numb.count('к')
        return int(float(numb.replace('к', '')) * 1000 ** ks)
    except (TypeError, ValueError):
        return


def amount_size(numb: Union[str, int, float],
                max_numb: int = None,
                min_numb: int = None,
                more_error: str = None,
                less_error: str = None,
                numb_error: str = None) -> Union[int, str]:
    numb = amount(numb)

    if not numb:
        return numb_error

    if min_numb is not None and numb < min_numb:
        return less_error
    elif max_numb is not None and numb > max_numb:
        return more_error

    return numb


def check_text(text: str,
               max_len: int = None,
               min_len: int = None,
               too_long_error: str = None,
               too_short_error: str = None,
               bad_symbols_error: str = None) -> Optional[str]:
    if not re.match(r'^[A-zА-я0-9Ё.|\\,/_+=\-*!@#$%^&(){}\[\]"\'№;:?<>~\s]+$', text):
        return bad_symbols_error

    if max_len and len(text) > max_len:
        return too_long_error

    if min_len and len(text) < min_len:
        return too_short_error
    return


