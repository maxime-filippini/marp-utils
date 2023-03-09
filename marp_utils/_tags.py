from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from ._exceptions import NoMatchingCodeBlockError


class BaseTag(ABC):
    @abstractmethod
    def expand(self) -> str:
        ...


class Section(BaseTag):
    def expand(self, id, title, **kwargs) -> str:
        directives = [
            f'<!-- _header: <div id="{id}"></div> -->',
            "<!-- _class: divider -->",
        ]

        if title:
            directives.append(f"# {title}")

        return "\n".join(directives)


class Title(BaseTag):
    def expand(self, **kwargs) -> str:
        return "<!-- _class: title -->"


class Code(BaseTag):
    def expand(self, id, code_blocks, **kwargs):
        try:
            output = next(
                block.output for block in code_blocks if block.params.get("id") == id
            )
        except StopIteration:
            raise NoMatchingCodeBlockError(id)

        return f"```python\n{output}\n```"
