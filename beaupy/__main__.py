"""Command line interface: `beaupy select a b c`. UI goes to stderr, the answer to stdout."""

import argparse
import sys
from typing import List, Optional

import beaupy

CANCELLED = 130


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='beaupy', description='Interactive prompts for shell scripts.')
    parser.add_argument('--version', action='version', version=f'%(prog)s {beaupy.__version__}')
    sub = parser.add_subparsers(dest='command', required=True)

    select = sub.add_parser('select', help='pick one option; prints it')
    select.add_argument('options', nargs='+')
    select.add_argument('--title', default='')
    select.add_argument('--filterable', action='store_true')

    multiple = sub.add_parser('select-multiple', help='pick several options; prints one per line')
    multiple.add_argument('options', nargs='+')
    multiple.add_argument('--title', default='')
    multiple.add_argument('--filterable', action='store_true')

    confirm = sub.add_parser('confirm', help='ask yes/no; exit code 0 for yes, 1 for no')
    confirm.add_argument('question')
    confirm.add_argument('--default-yes', action='store_true')

    prompt = sub.add_parser('prompt', help='ask for text; prints it')
    prompt.add_argument('prompt')
    prompt.add_argument('--secure', action='store_true')
    prompt.add_argument('--initial-value')
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == 'select':
            result = beaupy.select(args.options, title=args.title, filterable=args.filterable)
        elif args.command == 'select-multiple':
            result = beaupy.select_multiple(args.options, title=args.title, filterable=args.filterable)
        elif args.command == 'confirm':
            result = beaupy.confirm(args.question, default_is_yes=args.default_yes)
            return CANCELLED if result is None else int(not result)
        else:
            result = beaupy.prompt(args.prompt, secure=args.secure, initial_value=args.initial_value)
    except (KeyboardInterrupt, beaupy.Abort):
        return CANCELLED
    if result is None:
        return CANCELLED
    sys.stdout.write('\n'.join(result) + '\n' if isinstance(result, list) else f'{result}\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
