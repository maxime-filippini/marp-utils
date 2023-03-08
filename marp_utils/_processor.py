from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any

import yaml
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

from ._tags import Code
from ._tags import Section
from ._tags import Title
from marp_utils import _code

RE_COMMENT = r'<!--\s(\w+)(?:\:\s(.+))?\s-->'
RE_PARAMS = r'(\w+)="([^"]+)"'
RE_CODE_BLOCKS_SETUP = '```python(?:.+?)(\\#\\s<\n(?:.+?)\n\\#\\s>\n)(?:.+?)```'


class FileUpdateHandler(PatternMatchingEventHandler):
    def __init__(
        self,
        processor: MarpProcessor,
        file_path: str,
        out_path: str,
        export_path: str | None,
    ):
        super().__init__(patterns=[file_path])
        self.processor = processor
        self.file_path = file_path
        self.out_path = out_path
        self.export_path = export_path

    def on_modified(self, event):
        self.processor.process_file(
            path=self.file_path,
            out_path=self.out_path,
        )
        print(f'File updated [{self.out_path}]!')

        if self.export_path:
            self.processor.export_file(
                path=self.out_path,
                out_path=self.export_path,
                include_html=True,
            )


def process_file_on_save(processor, file_path, out_path, export_path):
    observer = Observer()
    event_handler = FileUpdateHandler(
        processor=processor,
        file_path=file_path,
        out_path=out_path,
        export_path=export_path,
    )

    print(f'Now watching [{file_path}]!')

    observer.schedule(event_handler, Path(file_path).parent, recursive=False)
    observer.start()

    try:
        while observer.is_alive():
            observer.join(1)
    finally:
        observer.stop()
        observer.join()


class MarpProcessor:
    """Processor for Marp presentation files."""

    tag_dict = {'section': Section, 'code': Code, 'title': Title}

    def _parse_frontmatter(self, section_text: str) -> str:
        """Parse the YAML frontmatter of the presentation file.

        Args:
            section_text (str): Text of the first section of the file.

        Raises:
            ValueError: If "marp: true" not found in frontmatter.

        Returns:
            str: Parsed frontmatter.
        """
        frontmatter = yaml.safe_load(section_text)

        if 'marp' not in frontmatter or not frontmatter.get('marp'):
            raise ValueError("'marp: true' not found in frontmatter!")

        return frontmatter

    def _process_section(
        self,
        section_text: str,
        var_dict: dict[str, Any],
        code_blocks: list[_code.CodeBlockData],
    ) -> str:
        """Parse a section, i.e. a marp slide.

        Args:
            section_text (str): Section test
            var_dict (dict[str, Any]): Dictionary of variables.
            code_blocks (list[_code.CodeBlockData]): Code blocks extracted from
            the full text.

        Returns:
            str: Processed section.
        """
        section_lines = section_text.splitlines()
        out = []
        for line in section_lines:
            for k, v in var_dict.items():
                line = line.replace(f'${{{k}}}', str(v))

            new_text = self._expand_comment(line, code_blocks=code_blocks)
            out.append(new_text)

        return '\n'.join(out)

    def _expand_comment(self, line: str, code_blocks: list[_code.CodeBlockData]) -> str:
        """Expand a command

        Args:
            line (str): _description_
            code_blocks (list[_code.CodeBlockData]): _description_

        Returns:
            str: _description_
        """
        match = re.match(RE_COMMENT, line)

        if not match:
            return line

        id, params_text = match.groups()

        if params_text is None:
            params_text = ''

        if id not in self.tag_dict:
            return line

        tag_parser = self.tag_dict[id]()

        param_items = re.findall(RE_PARAMS, params_text)
        params = {k: v for k, v in param_items}

        return tag_parser.expand(**params, code_blocks=code_blocks)

    def _parse_comment_params(self, param_text):
        param_items = re.findall(RE_PARAMS, param_text)
        return {k: v for k, v in param_items}

    def get_comments(self, data):
        all_comments = re.findall(f'({RE_COMMENT})', data)

        out = []
        for comment, id, param_text in all_comments:
            params = self._parse_comment_params(param_text=param_text)

            out.append(
                {
                    'id': id,
                    'comment': comment,
                    'params': params,
                },
            )

        return out

    def get_code_blocks(self, data):
        return _code.get_python_code_blocks(data)

    def process_file(self, path, out_path):
        # Read data
        with open(path, encoding='utf-8') as fp:
            data = fp.read()

        # Get all of the code blocks and run them
        code_blocks = self.get_code_blocks(data)

        # Get all of the section text
        sections = [section.strip() for section in data.split('---') if section]

        # Read frontmatter
        frontmatter = self._parse_frontmatter(sections[0])
        variable_dict = frontmatter['variables']

        # Re-build each section
        new_sections = []
        for section in sections:
            new_sections.append(
                self._process_section(
                    section,
                    var_dict=variable_dict,
                    code_blocks=code_blocks,
                ),
            )

        # Re-build the file
        out_path = Path(out_path)
        out_str = '---\n\n' + '\n\n---\n\n'.join(new_sections)

        # Remove set up lines from code blocks
        setup_lines = re.findall(RE_CODE_BLOCKS_SETUP, out_str, re.DOTALL)
        for setup_block in setup_lines:
            out_str = out_str.replace(setup_block, '')

        with open(out_path, 'w', encoding='utf-8') as fp:
            fp.write(out_str)

        print(f'Processed file [{path}] -> [{out_path}]')

    def export_file(self, path, out_path, include_html=False):
        args = [
            *('marp', path),
            *('-o', out_path),
            '--pdf',
            '--pdf-outlines',
            '--pdf-outlines.pages=false',
            '--allow-local-files',
        ]

        if include_html:
            args.append('--html')

        return subprocess.Popen(args)
