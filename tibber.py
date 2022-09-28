from typing import Dict, Optional
import sched
import requests
import logging
import time
from datetime import datetime, timedelta
from threading import Thread, Lock

import config

_scheduler: sched.scheduler = None
_prices: Dict[int, float] = {}
_price_mutex = Lock()
_default_config = {'tibber_token': 'xxx',
                   'grid_fees': 0.30}
_log = logging.getLogger(__name__)

_fake_data = {'data': {'viewer': {'homes': [{'currentSubscription': {'priceInfo': {'today': [{'total': 0.6932, 'startsAt': '2022-09-28T00:00:00.000+02:00'}, {'total': 0.6878, 'startsAt': '2022-09-28T01:00:00.000+02:00'}, {'total': 0.6965, 'startsAt': '2022-09-28T02:00:00.000+02:00'}, {'total': 0.7086, 'startsAt': '2022-09-28T03:00:00.000+02:00'}, {'total': 0.7132, 'startsAt': '2022-09-28T04:00:00.000+02:00'}, {'total': 0.7619, 'startsAt': '2022-09-28T05:00:00.000+02:00'}, {'total': 0.8413, 'startsAt': '2022-09-28T06:00:00.000+02:00'}, {'total': 1.0116, 'startsAt': '2022-09-28T07:00:00.000+02:00'}, {'total': 1.1099, 'startsAt': '2022-09-28T08:00:00.000+02:00'}, {'total': 1.1232, 'startsAt': '2022-09-28T09:00:00.000+02:00'}, {'total': 1.113, 'startsAt': '2022-09-28T10:00:00.000+02:00'}, {'total': 1.111, 'startsAt': '2022-09-28T11:00:00.000+02:00'}, {'total': 1.1076, 'startsAt': '2022-09-28T12:00:00.000+02:00'}, {'total': 1.1122, 'startsAt': '2022-09-28T13:00:00.000+02:00'}, {'total': 1.1174, 'startsAt': '2022-09-28T14:00:00.000+02:00'}, {'total': 1.1183, 'startsAt': '2022-09-28T15:00:00.000+02:00'}, {'total': 1.055, 'startsAt': '2022-09-28T16:00:00.000+02:00'}, {'total': 1.1053, 'startsAt': '2022-09-28T17:00:00.000+02:00'}, {'total': 1.1026, 'startsAt': '2022-09-28T18:00:00.000+02:00'}, {'total': 1.1011, 'startsAt': '2022-09-28T19:00:00.000+02:00'}, {'total': 1.1167, 'startsAt': '2022-09-28T20:00:00.000+02:00'}, {'total': 1.0283, 'startsAt': '2022-09-28T21:00:00.000+02:00'}, {'total': 1.0249, 'startsAt': '2022-09-28T22:00:00.000+02:00'}, {'total': 0.8914, 'startsAt': '2022-09-28T23:00:00.000+02:00'}], 'tomorrow': [{'total': 0.7647, 'startsAt': '2022-09-29T00:00:00.000+02:00'}, {'total': 0.7802, 'startsAt': '2022-09-29T01:00:00.000+02:00'}, {'total': 0.7958, 'startsAt': '2022-09-29T02:00:00.000+02:00'}, {'total': 0.7621, 'startsAt': '2022-09-29T03:00:00.000+02:00'}, {'total': 0.8442, 'startsAt': '2022-09-29T04:00:00.000+02:00'}, {'total': 0.9374, 'startsAt': '2022-09-29T05:00:00.000+02:00'}, {'total': 1.0824, 'startsAt': '2022-09-29T06:00:00.000+02:00'}, {'total': 1.3375, 'startsAt': '2022-09-29T07:00:00.000+02:00'}, {'total': 2.5478, 'startsAt': '2022-09-29T08:00:00.000+02:00'}, {'total': 2.1398, 'startsAt': '2022-09-29T09:00:00.000+02:00'}, {'total': 2.0221, 'startsAt': '2022-09-29T10:00:00.000+02:00'}, {'total': 2.5735, 'startsAt': '2022-09-29T11:00:00.000+02:00'}, {'total': 2.4138, 'startsAt': '2022-09-29T12:00:00.000+02:00'}, {'total': 3.2073, 'startsAt': '2022-09-29T13:00:00.000+02:00'}, {'total': 2.6125, 'startsAt': '2022-09-29T14:00:00.000+02:00'}, {'total': 2.9351, 'startsAt': '2022-09-29T15:00:00.000+02:00'}, {'total': 3.3831, 'startsAt': '2022-09-29T16:00:00.000+02:00'}, {'total': 4.3323, 'startsAt': '2022-09-29T17:00:00.000+02:00'}, {'total': 5.055, 'startsAt': '2022-09-29T18:00:00.000+02:00'}, {'total': 4.9785, 'startsAt': '2022-09-29T19:00:00.000+02:00'}, {'total': 4.0849, 'startsAt': '2022-09-29T20:00:00.000+02:00'}, {'total': 3.4257, 'startsAt': '2022-09-29T21:00:00.000+02:00'}, {'total': 1.2898, 'startsAt': '2022-09-29T22:00:00.000+02:00'}, {'total': 1.1398, 'startsAt': '2022-09-29T23:00:00.000+02:00'}]}}}, {'currentSubscription': {'priceInfo': {'today': [{'total': 0.6932, 'startsAt': '2022-09-28T00:00:00.000+02:00'}, {'total': 0.6878, 'startsAt': '2022-09-28T01:00:00.000+02:00'}, {'total': 0.6965, 'startsAt': '2022-09-28T02:00:00.000+02:00'}, {'total': 0.7086, 'startsAt': '2022-09-28T03:00:00.000+02:00'}, {'total': 0.7132, 'startsAt': '2022-09-28T04:00:00.000+02:00'}, {'total': 0.7619, 'startsAt': '2022-09-28T05:00:00.000+02:00'}, {'total': 0.8413, 'startsAt': '2022-09-28T06:00:00.000+02:00'}, {'total': 1.0116, 'startsAt': '2022-09-28T07:00:00.000+02:00'}, {'total': 1.1099, 'startsAt': '2022-09-28T08:00:00.000+02:00'}, {'total': 1.1232, 'startsAt': '2022-09-28T09:00:00.000+02:00'}, {'total': 1.113, 'startsAt': '2022-09-28T10:00:00.000+02:00'}, {'total': 1.111, 'startsAt': '2022-09-28T11:00:00.000+02:00'}, {'total': 1.1076, 'startsAt': '2022-09-28T12:00:00.000+02:00'}, {'total': 1.1122, 'startsAt': '2022-09-28T13:00:00.000+02:00'}, {'total': 1.1174, 'startsAt': '2022-09-28T14:00:00.000+02:00'}, {'total': 1.1183, 'startsAt': '2022-09-28T15:00:00.000+02:00'}, {'total': 1.055, 'startsAt': '2022-09-28T16:00:00.000+02:00'}, {'total': 1.1053, 'startsAt': '2022-09-28T17:00:00.000+02:00'}, {'total': 1.1026, 'startsAt': '2022-09-28T18:00:00.000+02:00'}, {'total': 1.1011, 'startsAt': '2022-09-28T19:00:00.000+02:00'}, {'total': 1.1167, 'startsAt': '2022-09-28T20:00:00.000+02:00'}, {'total': 1.0283, 'startsAt': '2022-09-28T21:00:00.000+02:00'}, {'total': 1.0249, 'startsAt': '2022-09-28T22:00:00.000+02:00'}, {'total': 0.8914, 'startsAt': '2022-09-28T23:00:00.000+02:00'}], 'tomorrow': [{'total': 0.7647, 'startsAt': '2022-09-29T00:00:00.000+02:00'}, {'total': 0.7802, 'startsAt': '2022-09-29T01:00:00.000+02:00'}, {'total': 0.7958, 'startsAt': '2022-09-29T02:00:00.000+02:00'}, {'total': 0.7621, 'startsAt': '2022-09-29T03:00:00.000+02:00'}, {'total': 0.8442, 'startsAt': '2022-09-29T04:00:00.000+02:00'}, {'total': 0.9374, 'startsAt': '2022-09-29T05:00:00.000+02:00'}, {'total': 1.0824, 'startsAt': '2022-09-29T06:00:00.000+02:00'}, {'total': 1.3375, 'startsAt': '2022-09-29T07:00:00.000+02:00'}, {'total': 2.5478, 'startsAt': '2022-09-29T08:00:00.000+02:00'}, {'total': 2.1398, 'startsAt': '2022-09-29T09:00:00.000+02:00'}, {'total': 2.0221, 'startsAt': '2022-09-29T10:00:00.000+02:00'}, {'total': 2.5735, 'startsAt': '2022-09-29T11:00:00.000+02:00'}, {'total': 2.4138, 'startsAt': '2022-09-29T12:00:00.000+02:00'}, {'total': 3.2073, 'startsAt': '2022-09-29T13:00:00.000+02:00'}, {'total': 2.6125, 'startsAt': '2022-09-29T14:00:00.000+02:00'}, {'total': 2.9351, 'startsAt': '2022-09-29T15:00:00.000+02:00'}, {'total': 3.3831, 'startsAt': '2022-09-29T16:00:00.000+02:00'}, {'total': 4.3323, 'startsAt': '2022-09-29T17:00:00.000+02:00'}, {'total': 5.055, 'startsAt': '2022-09-29T18:00:00.000+02:00'}, {'total': 4.9785, 'startsAt': '2022-09-29T19:00:00.000+02:00'}, {'total': 4.0849, 'startsAt': '2022-09-29T20:00:00.000+02:00'}, {'total': 3.4257, 'startsAt': '2022-09-29T21:00:00.000+02:00'}, {'total': 1.2898, 'startsAt': '2022-09-29T22:00:00.000+02:00'}, {'total': 1.1398, 'startsAt': '2022-09-29T23:00:00.000+02:00'}]}}}]}}}


def has_prices() -> bool:
    ''' Return bool if prices have been downloaded '''
    return bool(get_current_price())


def get_current_price() -> Optional[float]:
    ''' Return current price '''
    with _price_mutex:
        hour = datetime.now().hour
        return _prices.get(hour)


def _decode_prices(data):
    days = data['data']['viewer']['homes'][0]['currentSubscription']['priceInfo']

    # verify we got todays prices and not yesterdays
    # (due to clock diff between client and server, we could be getting unexpected data)
    last_midnight = datetime.now().replace(microsecond=0, second=0, minute=0, hour=0)
    first_hour = datetime.strptime(days['today'][0]['startsAt'], '%Y-%m-%dT%H:%M:%S.%f%z')
    if last_midnight.time() != first_hour.time():
        _log.info(f'We got unexpected data: {first_hour=} != {last_midnight=}')
        raise RuntimeError

    grid_fees = config.get('grid_fees')
    offset = 0
    for day in days:
        if day == 'tomorrow':
            offset += 24
        for hour in days[day]:
            # "startsAt": "2022-09-26T00:00:00.000+02:00"
            t = datetime.strptime(hour['startsAt'], '%Y-%m-%dT%H:%M:%S.%f%z')
            global _prices
            _prices[t.hour + offset] = hour['total'] + grid_fees


def _download():
    if 0:
        _log.info('Using fake data')
        _decode_prices(_fake_data)
        return
    query = '{"query": "{viewer {homes {currentSubscription {priceInfo ' \
            '{today {total startsAt} tomorrow {total startsAt}}}}}}"}'
    URL = 'https://api.tibber.com/v1-beta/gql'
    auth_token = config.get('tibber_token')
    headers = {'Authorization': f'Bearer {auth_token}',
               'Content-Type': 'application/json'}
    _log.info('Downloading prices')
    response = requests.post(URL, headers=headers, data=query)
    if response.status_code == 200:
        data = response.json()
        print(data)
        _decode_prices(data)
    else:
        _log.error(f'tibber: HTTP status code {response.status_code}')
        raise RuntimeError


def _midnight_cleanup():
    # at midnight, throw away old price data so [0] is current midnight
    midnight: bool = datetime.now().hour == 0
    if midnight and len(_prices) > 24:
        _log.info('Midnight! Throwing away old prices')
        with _price_mutex:
            del _prices[0:23]


def _try_download():
    # Each download grabs 24-48 hours worth of data, so we could run this just daily.
    # But to increase resilience in case of network outage, and to make sure
    # we get the next-day prices asap, we download every hour.
    _midnight_cleanup()
    try:
        with _price_mutex:
            _download()
        # all good, run again next hour
        next_hour = datetime.now().replace(microsecond=0, second=0, minute=0) + timedelta(hours=1)
        _log.info(f'Scheduling next download at {next_hour}')
        _scheduler.enterabs(next_hour.timestamp(), 0, _try_download)
    except RuntimeError:
        _log.info('Download failed, trying again in 30s')
        _scheduler.enter(30, 0, _try_download)


def _threadloop():
    global _scheduler
    while True:
        _scheduler = sched.scheduler(timefunc=time.time)
        _scheduler.enter(0, 0, _try_download)
        _scheduler.run(blocking=True)
        _log.error('Unexpected exit')
        # we should never run out of scheduled events,
        # but if we do just start over


def init():
    config.put_defaults(_default_config)
    t = Thread(target=_threadloop, name='Tibber')
    t.daemon = True
    t.start()


if __name__ == '__main__':
    _download()
    #_decode_prices(data)
