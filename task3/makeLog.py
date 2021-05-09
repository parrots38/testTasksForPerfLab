import logging
import random
import time
from datetime import datetime
import os


def top_up(bucket: int) -> bool:
    """Returns a boolean value for the success of the action.

    :param bucket: int amount of added water;
    :return: True if the action was successful.

    """

    global barrel_volume

    if barrel_volume + bucket < VOLUME:
        barrel_volume += bucket
        return True
    return False


def scoop(bucket: int) -> bool:
    """Returns a boolean value for the success of the action.

    :param bucket: int amount of subtracted water;
    :return: True if the action was successful.

    """

    global barrel_volume

    if barrel_volume - bucket > 0:
        barrel_volume -= bucket
        return True
    return False


user_names = [
    'Алексей',
    'Александр',
    'Дмитрий',
    'Татьяна',
    'Добрыня',
    'Катерина',
    'Рита',
    'Дайнерис Таргариен',
    'Рик',
    'Морти',
    'Машка',
    'Пашка'
]

TIME_NOW = time.time()
year_earlier = TIME_NOW - 5*365*24*60*60

VOLUME = random.randrange(0, 500, 10)
barrel_volume = random.randint(0, VOLUME)

actions = {'top up': top_up, 'scoop': scoop}
filename = 'log.log'

with open(filename, mode='w') as f:
    f.write(
        f'META DATA:\n'
        f'{VOLUME} (объем бочки)\n'
        f'{barrel_volume} (текущий объем воды в бочке)\n'
    )

    while os.path.getsize(filename) < 2**20:
        year_earlier += random.uniform(20, 60*60*6)
        random_time = datetime.utcfromtimestamp(year_earlier).strftime(
            '%Y-%m-%dT%H:%M:%S.%fZ')
        random_name = random.choice(user_names)

        bucket = random.randint(0, VOLUME//3)
        random_act = random.choice(['top up', 'scoop'])
        if actions[random_act](bucket):
            act = f"wanna {random_act} {bucket}l(успех)"
        else:
            act = f"wanna {random_act} {bucket}l(фейл)"

        f.write(f"{random_time} - {random_name} - {act}" + '\n')
