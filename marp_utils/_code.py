from __future__ import annotations

import contextlib
import io
import re
import sys
from dataclasses import dataclass

RE_CODE_BLOCK = r"```python\s?([^\n]*)\n(.+?)\n```\n"
RE_SETUP_TEXT = "\\#\\s<\n(\\#\\s(.+?)\n*)\\#\\s>\n"
RE_SETUP_LINES = "\\#\\s(.+?)\n"
RE_PARAMS = r'([\w|_]+)="([^"]*)"'


@dataclass
class CodeBlockData:
    """Representation of a code block."""

    text: str
    span: tuple[int, int]
    params: dict[str, str]
    setup: str | None = None
    code: str | None = None
    output: str | None = None


@contextlib.contextmanager
def capture_stdout() -> None:
    """Capture standard output within context.

    Yields:
        io.StringIO: Stream to standard output.
    """
    old_out = sys.stdout

    try:
        out: io.StringIO = io.StringIO()
        sys.stdout = out
        yield out
    finally:
        sys.stdout = old_out


def find_setup_and_code(block_text: str) -> tuple[list[str], list[str]]:
    """Extract setup lines and code lines from code block.

    Args:
        block_text (str): Code block as text.

    Returns:
        tuple[list[str], list[str]]: Setup lines and code lines.
    """
    setup = re.search(RE_SETUP_TEXT, block_text, re.DOTALL)

    if not setup:
        return [], block_text.splitlines()

    setup_text = setup.groups()[0]
    setup_lines = re.findall(RE_SETUP_LINES, setup_text)

    setup_start, setup_end = setup.span()

    # Adjust the block text
    block_text = block_text[:setup_start] + block_text[setup_end:]
    code_lines = block_text.splitlines()

    return setup_lines, code_lines


def get_python_code_blocks(text: str) -> list[CodeBlockData]:
    """Extract python code blocks from text.

    Args:
        text (str): Text data.

    Returns:
        list[CodeBlockData]: Extracted code blocks.
    """

    """Get the code blocks data"""
    it_blocks = re.finditer(RE_CODE_BLOCK, text, re.DOTALL)

    out = []

    for block in it_blocks:
        block_params, block_text = block.groups()
        setup, code = find_setup_and_code(block_text=block_text)

        # Parameters
        params = {k: v for k, v in re.findall(RE_PARAMS, block_params)}

        if "run" in params:
            run = params["run"]

            if run.lower() == "false":
                run = False
            elif run.lower() == "true":
                run = True
            else:
                run = bool(int(run))

            params["run"] = run

        else:
            params["run"] = False

        if run:
            output = run_code(setup_lines=setup, code_lines=code)
        else:
            output = None

        out.append(
            CodeBlockData(
                text=block_text,
                span=block.span(),
                params=params,
                setup=setup,
                code=code,
                output=output,
            ),
        )

    return out


def run_code(setup_lines: list[str], code_lines: list[str]) -> str:
    """Run code, including setup, and capture standard output.

    Args:
        setup_lines (list[str]): Lines of code to run for side effects.
        code_lines (list[str]): Line of codes to run and capture output.

    Returns:
        str: Capture of standard output.
    """
    for line in setup_lines:
        exec(line)

    with capture_stdout() as stdout_:
        for line in code_lines:
            if not line.startswith("#"):
                eval(line)

    return stdout_.getvalue().strip()
