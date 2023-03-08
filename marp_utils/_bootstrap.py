"""Functions and classes used for bootstrapping a Marp presentation."""
from __future__ import annotations

import os
from enum import auto
from enum import Enum
from pathlib import Path
from typing import Any

import inquirer
import yaml
from inquirer.themes import GreenPassion

from ._theme import read_theme_name_from_file

LINE_FEED = '\n'
SECTION_SEP = '---'
NEXT_SECTION_SEP = LINE_FEED * 2 + SECTION_SEP + LINE_FEED * 2


class BootstrapOption(Enum):
    paginate = auto()
    header = auto()
    footer = auto()
    table_of_contents = auto()
    img_center = auto()


def make_comment(id_: str, **kwargs) -> str:
    """Make a special HTML comment from name and parameter dictionary.

    Args:
        id (str): Type of the comment.

    Returns:
        str: Formatted string.
    """
    if kwargs:
        param_str = ': ' + ' '.join(f'{k}="{v}"' for k, v in kwargs.items())
    else:
        param_str = ''

    return ''.join(
        (
            '<!-- ',
            f'{id_}',
            param_str,
            ' -->',
        ),
    )


class Bootstrapper:
    def __init__(
        self,
        title: str,
        subtitle: str | None = None,
        date: str | None = None,
        event: str | None = None,
        header: str | None = None,
        footer: str | None = None,
        theme: str = 'gaia',
        theme_path: os.PathLike | None = None,
        sections: list[str] | None = None,
        variables: dict[str, Any] | None = None,
        options: list[BootstrapOption] | None = None,
    ):
        if sections is None:
            sections = []

        if variables is None:
            variables = {}

        if options is None:
            options = []

        self.title = title
        self.subtitle = subtitle
        self.date = date
        self.event = event
        self.theme = theme
        self.theme_path = theme_path
        self.sections = sections
        self._variables = variables
        self.options = options

        self._header = header
        self._footer = footer

    @property
    def header(self):
        if self._header:
            return self._header
        return '[*${title}*](#1)'

    @property
    def event_date(self):
        out = ''

        if self.event:
            out += '*${event}* '

        if self.date:
            out += '${date}'

        return out

    @property
    def footer(self):
        if self._footer:
            return self._footer
        return self.event_date

    @property
    def variables(self) -> dict[str, Any]:
        """dict[str, Any]: Variable dictionary."""
        out = self._variables

        # Add relevant variables
        for field in ['title', 'subtitle', 'date', 'event', 'theme_path']:
            data = getattr(self, field)
            if data is not None and getattr(self, field):
                out[field] = data

        return out

    @property
    def frontmatter(self) -> str:
        """str: Parsed YAML frontmatter."""
        return yaml.dump(
            {
                'marp': True,
                'theme': self.theme,
                'variables': self.variables,
            },
        )[:-1]

    @property
    def first_slide(self) -> str:
        """str: First slide of the presentation."""
        to_write = [make_comment('title'), '# ${title}']

        if self.subtitle:
            to_write.append('## ${subtitle}')

        if self.event_date:
            to_write.append(self.event_date)

        return '\n'.join(to_write)

    @property
    def extra_directives(self) -> str:
        out = []

        if 'header' in self.options:
            out.append(f"<!-- header: '{self.header}' -->")

        if 'footer' in self.options:
            out.append(f"<!-- footer: '{self.footer}' -->")

        if 'paginate' in self.options:
            out.append('<!-- paginate: true -->')

        if 'img_center' in self.options:
            out.append(
                (
                    '<style>\n'
                    'img[alt~=center] {\n'
                    '    display: block;\n'
                    '    margin: 0 auto;\n'
                    '}\n'
                    '</style>'
                ),
            )

        return '\n'.join(out)

    def toc(self) -> str:
        """Add Table of contents placeholder slide.

        Returns:
            str: Table of contents placeholder slide.
        """
        return '# Table of contents\n' + make_comment(id_='toc')

    def section_divider(self, id: str, title: str) -> str:
        """Builds a section divider marker.

        Args:
            id (str): Identifier for reference.
            title (str): Title of the section.

        Returns:
            str: Comment that marks a section divider.
        """
        return make_comment(id_='section', id=id, title=title)

    def blank_sections(self) -> str:
        """Build placeholder slides for sections.

        Returns:
            str: Set of placeholder slides.
        """
        out = []

        for section in self.sections:
            divider_tag = self.section_divider(
                id=section.lower().replace(' ', '-'),
                title=section,
            )

            content = f'## {section} \n Start writing your content here!'
            out.append((divider_tag, content))

        return out

    def bootstrap(self, file_path: os.PathLike, include_toc: bool = True) -> None:
        """Bootstrap a Marp presentation file.

        Args:
            file_path (os.PathLike): Destination file.
            include_toc (bool, optional): Whether to add a Table of Contents slide.
            Defaults to True.
        """
        to_write = []

        to_write.append(SECTION_SEP)
        to_write.append(LINE_FEED)
        to_write.append(LINE_FEED)
        to_write.append(self.frontmatter)
        to_write.append(NEXT_SECTION_SEP)
        to_write.append(self.first_slide)
        to_write.append(NEXT_SECTION_SEP)
        to_write.append(self.extra_directives)

        if self.extra_directives:
            to_write.append(LINE_FEED)
            to_write.append(LINE_FEED)

        if 'table_of_contents' in self.options:
            to_write.append(self.toc())
            to_write.append(NEXT_SECTION_SEP)

        for divider, content in self.blank_sections():
            to_write.append(divider)
            to_write.append(NEXT_SECTION_SEP)
            to_write.append(content)
            to_write.append(NEXT_SECTION_SEP)

        with open(file_path, 'w', encoding='utf-8') as fp:
            fp.write(''.join(to_write))


def ask_for_sections(
    i: int = 0,
    prev_answers: dict[str, str] | None = None,
) -> dict[str, str]:
    """Prompt the user for sections to be added.

    This function is called recursively to allow for supplying sections
    one by one, until an empty answer is given, in which case the prompting
    stops.

    Args:
        i (int, optional): Index of the section to be added. Defaults to 0.
        prev_answers (dict[str, str] | None, optional): Previous answers provided.
        Defaults to None.

    Returns:
        dict[str, str]: Answers provided.
    """
    if prev_answers is None:
        prev_answers = {}

    questions = [
        inquirer.Text(
            'section',
            message=(
                f'What is the title of section #{i+1}? '
                '(leave empty to finish process)'
            ),
        ),
    ]

    answers = inquirer.prompt(questions, theme=GreenPassion())

    if answers['section']:
        prev_answers[f'section_{i}'] = answers['section']
        out_answers = ask_for_sections(i=i + 1, prev_answers=prev_answers)
    else:
        out_answers = prev_answers

    return out_answers


def validate_output_path(path):
    path = Path(path)
    if not path.parent.exists():
        raise ValueError(
            'Path provided corresponds to a non-existent directory'
            f' [{path.parent.resolve()}]!',
        )

    if path.suffix != '.md':
        raise ValueError(
            'Path provided is not a valid markdown file '
            f'(extension [{path.suffix}], rather than [.md])',
        )

    return True


def boostrap_presentation(full: bool = False) -> None:
    """Script for bootstrapping a presentation."""
    print('-' * 32)
    print('Marp Presentation Bootstrapper')
    print('-' * 32)
    print('')

    questions = [
        inquirer.Text(
            'output_path',
            message="Path to file (has to end in '.md')",
            validate=lambda answers, path: validate_output_path(path),
        ),
        inquirer.Text('title', message='What is the title of your presentation?'),
        inquirer.Text(
            'subtitle',
            message='What is the sub-title of your presentation?',
            default=None,
        ),
        inquirer.Text('event', message='What is the event of your presentation?'),
        inquirer.Text(
            'date',
            message='What is the date of your presentation?',
        ),
        inquirer.Checkbox(
            'options',
            message='Pick the optional components you would like',
            choices=[
                'pagination',
                'header',
                'footer',
                'img-center',
                'table_of_contents',
            ],
        ),
        inquirer.Text(
            'header',
            message='What to display in the header (top of each slide)',
            ignore=lambda answers: (not full)
            or ('header' not in answers.get('options')),
        ),
        inquirer.Text(
            'footer',
            message='What to display in the footer (bottom of each slide)',
            ignore=lambda answers: (not full)
            or ('footer' not in answers.get('options')),
        ),
        inquirer.List(
            'theme',
            message='What theme do you want to use?',
            choices=['gaia', 'uncover', 'custom'],
        ),
        inquirer.Path(
            'theme_path',
            message='Path to custom theme',
            path_type='file',
            ignore=lambda answers: (answers.get('theme') != 'custom'),
        ),
        inquirer.Confirm('sections', message='Do you want to add sections?'),
    ]

    answers = inquirer.prompt(questions, theme=GreenPassion())

    theme_path = answers.get('theme_path')

    # Update the theme based on the path
    if theme_path is not None:
        answers['theme'] = read_theme_name_from_file(theme_path)

    if answers['sections']:
        answers['sections'] = list(ask_for_sections().values())
    else:
        answers['sections'] = []

    file_path = answers.pop('output_path')

    bootstrapper = Bootstrapper(**answers)
    bootstrapper.bootstrap(file_path=file_path)
