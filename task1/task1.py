#!/usr/bin/env python3
import argparse


def itoBase(
        nb: str, base_src: str = '0123456789', base_dst: str = None) -> str:
    """ Returns the value in the given number system.

    examples:
        itoBase(10, '012314567') -> '12'
        itoBase(24, '0123') -> '120'
        itoBase(24, 'absd') -> 'bsa'
        itoBase('123', '0123456789abcdf') -> '83'
        itoBase('233', '0123', '0123456789') -> '47'
        itoBase('aaa', '0123456789abcdef', '012') -> '10202010'
        itoBase('fea24135', '0123456789abcdef', '0123') -> '3332220210010311'

    :param nb: string with value or decimal integer;
    :param base_src: numeral value string;
    :param base_dst: numeral value string;
    :return: string with the value nb base_src in the number system base_dst.

    """

    if base_dst is None:
        base_dst, base_src = base_src, '0123456789'
    src, dst = len(base_src), len(base_dst)

    num = int(nb, base=src)
    ranks = []
    while num > 0:
        ranks.append(base_dst[num % dst])
        num //= dst

    return ''.join(reversed(ranks))


def main():
    parser = argparse.ArgumentParser()
    parser.usage = (
        f"task1.py [-nb value] [-src baseSrc] [-dst baseDst]\n\n"
        f"examples:\n"
        f"    task1.py -nb 10 -dst '01234567'\n"
        f"    task1.py -nb 233 -src '0123' -dst '0123456789'\n"
        f"    task1.py -nb 'fea24135' -src '0123456789abcdef' -dst '0123'"
    )
    parser.add_argument(
        '-nb', '--number', dest='value', action='store', type=str,
        help='string with value or decimal integer'
    )
    parser.add_argument(
        '-dst', '--baseDestination', dest='dst', action='store', type=str,
        help='output numeral value string'
    )
    parser.add_argument(
        '-src', '--baseSource', dest='src', action='store',
        type=str, default=None,
        help='input numeral value string [default: None]',
    )
    args = parser.parse_args()

    if args.src is None:
        print(itoBase(args.value, args.dst))
    else:
        print(itoBase(args.value, args.src, args.dst))


if __name__ == '__main__':
    main()
