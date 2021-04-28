import re
import argparse


def is_strings_equal(string1, string2):
    """Determines if strings are the same.

    :param string1: some string;
    :param string2: some string, can contain the * character denoting
        any number of any characters;
    :return: 'OK' if strings are equal, else return 'KO'.

    """

    pattern = re.escape(string2).replace('\*', '.*?')
    match = re.fullmatch(pattern, string1, flags=re.DOTALL)
    if match:
        return 'OK'
    return 'KO'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.usage = 'task4.py [arg1] [arg2]'
    parser.add_argument(
        'string1', action='store', type=str, help='some string')
    parser.add_argument(
        'string2', action='store', type=str,
        help=(
            'some string, can contain the * character denoting'
            'any number of any characters'
        )
    )

    args = parser.parse_args()
    print(is_strings_equal(args.string1, args.string2))
