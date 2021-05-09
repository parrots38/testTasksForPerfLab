import os
import sqlite3
import re
import time
import argparse
import csv
from functools import reduce

try:
    import pandas as pd
except ImportError:
    print('Please, install pandas:\n'
          '  pip install pandas')
    raise


def give_value(text: str) -> int:
    """Returns the amount of water added or removed from the barrel.

    :param text: a string describing the action with the barrel;
    :return: a signed integer;

    """

    match = re.search(r"wanna\s+(.*?)\s+(\d*)l", text)
    if not match:
        return 0
    if match[1] == 'top up':
        return int(match[2])
    return -int(match[2])


def give_date(date: str) -> float:
    """Returns unix time for the passed date.

    :param date: str date;
    :return: float unix time.

    """

    datetime = date.split('.')
    if len(datetime) > 1:
        date, ms = datetime
        ms = float(f"0.{ms[:-1]}")
    else:
        date, ms = datetime[0], 0
    clock = time.mktime(time.strptime(date, '%Y-%m-%dT%H:%M:%S'))
    clock += ms

    return clock


def give_data(filename: str) -> tuple or None:
    """Returns data from a log file.

    :param filename: str path to file;
    :return: (VOLUME, barrel_volume, data), which:
        VOLUME - int maximum barrel volume;
        barrel_volume - int volume of water in a barrel;
        data - pandas dataframe
            ('date', 'username', 'action', 'status').

    """

    with open(filename) as f:
        ok = f.readline()
        if not ok:
            return None

        VOLUME = int(f.readline().split()[0])
        barrel_volume = int(f.readline().split()[0])
        data = pd.read_table(
            f,
            sep='(?: - )|(?:\()',
            names=['date', 'username', 'action', 'status'],
            engine='python',
        )
    data['date'] = data['date'].apply(give_date)
    data['action'] = data['action'].apply(give_value)
    data['status'] = data['status'] == 'успех)'

    return VOLUME, barrel_volume, data


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.usage = f"task3.py [path_to_log_file] [date1] [date2]"
    parser.add_argument(
        'path_to_log', action='store', type=str, help='path_to_log_file')
    parser.add_argument(
        'date1', action='store', type=str,
        help='lower bound of the date period'
    )
    parser.add_argument(
        'date2', action='store', type=str,
        help='upper bound of the date period'
    )
    args = parser.parse_args()
    date1 = give_date(args.date1)
    date2 = give_date(args.date2)

    data = give_data(args.path_to_log)
    if not data:
        raise KeyboardInterrupt('Wrong data.')
    VOLUME, barrel_volume, dataframe = data

    database_filename = 'barrel_database.db'
    with sqlite3.connect(database_filename) as con:
        dataframe.to_sql('barrel_data', con, index=False)

        top_up = con.execute(f"""
            SELECT * FROM barrel_data WHERE 
            date >= {date1} AND date <= {date2} AND
            action > 0
        """)
        len_top_up = 0
        all_top_up_volume = 0
        for line in top_up:
            len_top_up += 1
            all_top_up_volume += line[2]

        fail_top_up = con.execute(f"""
            SELECT * FROM barrel_data WHERE 
            date >= {date1} AND date <= {date2} AND
            action > 0 AND status == 0
        """)
        len_fail_top_up = 0
        fail_top_up_volume = 0
        for line in fail_top_up:
            len_fail_top_up += 1
            fail_top_up_volume += line[2]

        percent_top_up = len_fail_top_up/len_top_up*100 if len_top_up else 0

        scoop = con.execute(f"""
            SELECT * FROM barrel_data WHERE 
            date >= {date1} AND date <= {date2} AND
            action < 0
        """)
        len_scoop = 0
        all_scoop_volume = 0
        for line in scoop:
            len_scoop += 1
            all_scoop_volume += abs(line[2])

        fail_scoop = con.execute(f"""
            SELECT * FROM barrel_data WHERE 
            date >= {date1} AND date <= {date2} AND
            action < 0 AND status == 0
        """)
        len_fail_scoop = 0
        fail_scoop_volume = 0
        for line in fail_scoop:
            len_fail_scoop += 1
            fail_scoop_volume += abs(line[2])

        percent_scoop = len_fail_scoop/len_scoop*100 if len_scoop else 0

        before = con.execute(f"""
            SELECT * FROM barrel_data WHERE 
            date < {date1} AND status == 1
        """)
        before_volume = 0
        for line in before:
            before_volume += line[2]
        if len_top_up + len_scoop:
            before_volume += barrel_volume

        top_up_volume = all_top_up_volume - fail_top_up_volume
        scoop_volume = all_scoop_volume - fail_scoop_volume
        after_volume = before_volume + top_up_volume - scoop_volume

    os.remove(database_filename)

    print(
        f"Какой объем воды был в бочке в начале указанного периода?\n"
        f"{before_volume}\n"
        f"Какой в конце указанного периода?\n"
        f"{after_volume}\n"
        f"Какое количество попыток налить воду в бочку было за "
        f"указанный период?\n"
        f"{len_top_up}\n"
        f"Какой процент ошибок был допущен за указанный период?\n"
        f"{percent_top_up}\n"
        f"Какой объем воды был налит в бочку за указанный период?\n"
        f"{top_up_volume}l\n"
        f"Какой объем воды был не налит в бочку за указанный период?\n"
        f"{fail_top_up_volume}l\n"
        f"Какое количество попыток забора воды из бочки было за "
        f"указанный период?\n"
        f"{len_scoop}\n"
        f"Какой процент ошибок был допущен за указанный период?\n"
        f"{percent_scoop}\n"
        f"Какой объем воды был забран из бочки за указанный период?\n"
        f"{scoop_volume}l\n"
        f"Какой объем воды был не забран из бочки за указанный период?\n"
        f"{fail_scoop_volume}l\n"
    )

    with open('answer.csv', mode='w') as f:
        writer = csv.writer(f)
        writer.writerow(['Действие', 'Добавление воды', 'Забор воды'])
        writer.writerow(['Попытки', len_top_up, len_scoop])
        writer.writerow(['Процент ошибок', percent_top_up, percent_scoop])
        writer.writerow(['Удалось, л', top_up_volume, scoop_volume])
        writer.writerow(
            ['Не удалось, л', fail_top_up_volume, fail_scoop_volume])
        writer.writerow([' ', 'Начало периода', 'Конец периода'])
        writer.writerow(['Объем воды, л', before_volume, after_volume])
