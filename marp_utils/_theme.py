from __future__ import annotations

import re

RE_THEME = '(?:\\/)?\\*\\s@theme\\s([^\\s]+)(?:\\s\\*\\/)?\n'


def read_theme_name_from_file(path):
    with open(path, encoding='utf-8') as fp:
        data = fp.read()

    match = re.search(RE_THEME, data, re.DOTALL)

    if not match:
        raise Exception('TODO')  # TODO

    return match.groups()[0]
