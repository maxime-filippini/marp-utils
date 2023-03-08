from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from ._bootstrap import boostrap_presentation
from ._exceptions import MarpNotInstalledError
from ._processor import MarpProcessor
from ._processor import process_file_on_save


def bootstrap(args):
    boostrap_presentation(full=args.full)


def process(args):
    if args.out_path is None:
        args.out_path = Path(args.path).parent / 'build.md'

    if args.export is not None and shutil.which('marp') is None:
        raise MarpNotInstalledError

    processor = MarpProcessor()
    processor.process_file(path=args.path, out_path=args.out_path)

    if args.export:
        p = processor.export_file(
            path=args.out_path,
            out_path=args.export,
            include_html=args.html,
        )

    if args.watch:
        process_file_on_save(
            processor=processor,
            file_path=args.path,
            out_path=args.out_path,
            export_path=args.export,
        )

    p.wait()


def main():
    parser = argparse.ArgumentParser(
        prog='marputils',
        description='Command line utilities for Marp presentations',
        epilog='',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    subparsers = parser.add_subparsers(required=True)

    bootstrap_parser = subparsers.add_parser(
        'bootstrap',
        help='Bootstrap a new Marp presentation',
        formatter_class=parser.formatter_class,
    )
    bootstrap_parser.add_argument(
        '--full',
        '-f',
        action='store_true',
        help='Whether to go through the full process (vs. simple).',
        default=False,
    )

    bootstrap_parser.set_defaults(func=bootstrap)

    process_parser = subparsers.add_parser(
        'process',
        help='Process a Marp presentation',
        formatter_class=parser.formatter_class,
    )
    process_parser.add_argument(
        '--path',
        '-p',
        action='store',
        required=True,
        help='The path to the Markdown file to be processed',
    )
    process_parser.add_argument(
        '--out_path',
        '-o',
        action='store',
        help='The path to the output file',
    )

    process_parser.add_argument(
        '--watch',
        '-w',
        action='store_true',
        help='Whether the input file should be watched for updates.',
    )

    process_parser.add_argument(
        '--export',
        '-e',
        action='store',
        default=None,
        help='Path to .pdf file',
    )

    process_parser.add_argument(
        '--html',
        action='store_true',
        default=False,
        help='Allow the parsing of HTML.',
    )

    process_parser.set_defaults(func=process)

    args = parser.parse_args()
    args.func(args)
