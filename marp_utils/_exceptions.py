from __future__ import annotations


class NoMatchingCodeBlockError(Exception):
    def __init__(self, block_id: str) -> None:
        super().__init__(f'[{block_id}] does not exist in the document!')


class MarpNotInstalledError(Exception):
    def __init__(self) -> None:
        super().__init__(
            (
                'marp not found, and therefore, export cannot be performed. '
                'Please refer to '
                'https://github.com/marp-team/marp-cli#install '
                'for installation steps.'
            ),
        )
