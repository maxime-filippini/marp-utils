import argparse

from .bootstrap import boostrap_presentation
from ._processor import MarpProcessor


def bootstrap(args):
    boostrap_presentation()


def process(args):
    processor = MarpProcessor()
    processor.process_file(path=args.path, out_path=args.out_path)


def main():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(required=True)

    bootstrap_parser = subparsers.add_parser("bootstrap")
    bootstrap_parser.set_defaults(func=bootstrap)

    process_parser = subparsers.add_parser("process")
    process_parser.add_argument("--path", "-p", action="store")
    process_parser.add_argument("--out_path", "-o", action="store")

    process_parser.set_defaults(func=process)

    args = parser.parse_args()
    args.func(args)
