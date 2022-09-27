from typing import Dict, Optional
import sched
import requests
import logging
from datetime import datetime, time, timedelta
from threading import Thread, Lock

import config

_scheduler: sched.scheduler = None
_prices: Dict[int, float] = {}
_price_mutex = Lock()
_default_config = {'tibber_token': 'xxx',
                   'grid_fees': 0.30}
_log = logging.getLogger(__name__)

_fake_data = {'data': {'viewer': {'homes': [{'currentSubscription': {'priceInfo': {'today': [{'total': 0.2648, 'startsAt': '2022-09-27T00:00:00.000+02:00'}, {'total': 0.2521, 'startsAt': '2022-09-27T01:00:00.000+02:00'}, {'total': 0.2475, 'startsAt': '2022-09-27T02:00:00.000+02:00'}, {'total': 0.2517, 'startsAt': '2022-09-27T03:00:00.000+02:00'}, {'total': 0.2702, 'startsAt': '2022-09-27T04:00:00.000+02:00'}, {'total': 0.2958, 'startsAt': '2022-09-27T05:00:00.000+02:00'}, {'total': 0.4122, 'startsAt': '2022-09-27T06:00:00.000+02:00'}, {'total': 0.8862, 'startsAt': '2022-09-27T07:00:00.000+02:00'}, {'total': 1.3063, 'startsAt': '2022-09-27T08:00:00.000+02:00'}, {'total': 1.0302, 'startsAt': '2022-09-27T09:00:00.000+02:00'}, {'total': 1.0212, 'startsAt': '2022-09-27T10:00:00.000+02:00'}, {'total': 1.0139, 'startsAt': '2022-09-27T11:00:00.000+02:00'}, {'total': 0.9224, 'startsAt': '2022-09-27T12:00:00.000+02:00'}, {'total': 0.906, 'startsAt': '2022-09-27T13:00:00.000+02:00'}, {'total': 0.8735, 'startsAt': '2022-09-27T14:00:00.000+02:00'}, {'total': 0.859, 'startsAt': '2022-09-27T15:00:00.000+02:00'}, {'total': 0.8676, 'startsAt': '2022-09-27T16:00:00.000+02:00'}, {'total': 0.9222, 'startsAt': '2022-09-27T17:00:00.000+02:00'}, {'total': 0.9807, 'startsAt': '2022-09-27T18:00:00.000+02:00'}, {'total': 0.9647, 'startsAt': '2022-09-27T19:00:00.000+02:00'}, {'total': 0.8996, 'startsAt': '2022-09-27T20:00:00.000+02:00'}, {'total': 0.79, 'startsAt': '2022-09-27T21:00:00.000+02:00'}, {'total': 0.7043, 'startsAt': '2022-09-27T22:00:00.000+02:00'}, {'total': 0.549, 'startsAt': '2022-09-27T23:00:00.000+02:00'}], 'tomorrow': [{'total': 0.6932, 'startsAt': '2022-09-28T00:00:00.000+02:00'}, {'total': 0.6878, 'startsAt': '2022-09-28T01:00:00.000+02:00'}, {'total': 0.6965, 'startsAt': '2022-09-28T02:00:00.000+02:00'}, {'total': 0.7086, 'startsAt': '2022-09-28T03:00:00.000+02:00'}, {'total': 0.7132, 'startsAt': '2022-09-28T04:00:00.000+02:00'}, {'total': 0.7619, 'startsAt': '2022-09-28T05:00:00.000+02:00'}, {'total': 0.8413, 'startsAt': '2022-09-28T06:00:00.000+02:00'}, {'total': 1.0116, 'startsAt': '2022-09-28T07:00:00.000+02:00'}, {'total': 1.1099, 'startsAt': '2022-09-28T08:00:00.000+02:00'}, {'total': 1.1232, 'startsAt': '2022-09-28T09:00:00.000+02:00'}, {'total': 1.113, 'startsAt': '2022-09-28T10:00:00.000+02:00'}, {'total': 1.111, 'startsAt': '2022-09-28T11:00:00.000+02:00'}, {'total': 1.1076, 'startsAt': '2022-09-28T12:00:00.000+02:00'}, {'total': 1.1122, 'startsAt': '2022-09-28T13:00:00.000+02:00'}, {'total': 1.1174, 'startsAt': '2022-09-28T14:00:00.000+02:00'}, {'total': 1.1183, 'startsAt': '2022-09-28T15:00:00.000+02:00'}, {'total': 1.055, 'startsAt': '2022-09-28T16:00:00.000+02:00'}, {'total': 1.1053, 'startsAt': '2022-09-28T17:00:00.000+02:00'}, {'total': 1.1026, 'startsAt': '2022-09-28T18:00:00.000+02:00'}, {'total': 1.1011, 'startsAt': '2022-09-28T19:00:00.000+02:00'}, {'total': 1.1167, 'startsAt': '2022-09-28T20:00:00.000+02:00'}, {'total': 1.0283, 'startsAt': '2022-09-28T21:00:00.000+02:00'}, {'total': 1.0249, 'startsAt': '2022-09-28T22:00:00.000+02:00'}, {'total': 0.8914, 'startsAt': '2022-09-28T23:00:00.000+02:00'}]}}}, {'currentSubscription': {'priceInfo': {'today': [{'total': 0.2648, 'startsAt': '2022-09-27T00:00:00.000+02:00'}, {'total': 0.2521, 'startsAt': '2022-09-27T01:00:00.000+02:00'}, {'total': 0.2475, 'startsAt': '2022-09-27T02:00:00.000+02:00'}, {'total': 0.2517, 'startsAt': '2022-09-27T03:00:00.000+02:00'}, {'total': 0.2702, 'startsAt': '2022-09-27T04:00:00.000+02:00'}, {'total': 0.2958, 'startsAt': '2022-09-27T05:00:00.000+02:00'}, {'total': 0.4122, 'startsAt': '2022-09-27T06:00:00.000+02:00'}, {'total': 0.8862, 'startsAt': '2022-09-27T07:00:00.000+02:00'}, {'total': 1.3063, 'startsAt': '2022-09-27T08:00:00.000+02:00'}, {'total': 1.0302, 'startsAt': '2022-09-27T09:00:00.000+02:00'}, {'total': 1.0212, 'startsAt': '2022-09-27T10:00:00.000+02:00'}, {'total': 1.0139, 'startsAt': '2022-09-27T11:00:00.000+02:00'}, {'total': 0.9224, 'startsAt': '2022-09-27T12:00:00.000+02:00'}, {'total': 0.906, 'startsAt': '2022-09-27T13:00:00.000+02:00'}, {'total': 0.8735, 'startsAt': '2022-09-27T14:00:00.000+02:00'}, {'total': 0.859, 'startsAt': '2022-09-27T15:00:00.000+02:00'}, {'total': 0.8676, 'startsAt': '2022-09-27T16:00:00.000+02:00'}, {'total': 0.9222, 'startsAt': '2022-09-27T17:00:00.000+02:00'}, {'total': 0.9807, 'startsAt': '2022-09-27T18:00:00.000+02:00'}, {'total': 0.9647, 'startsAt': '2022-09-27T19:00:00.000+02:00'}, {'total': 0.8996, 'startsAt': '2022-09-27T20:00:00.000+02:00'}, {'total': 0.79, 'startsAt': '2022-09-27T21:00:00.000+02:00'}, {'total': 0.7043, 'startsAt': '2022-09-27T22:00:00.000+02:00'}, {'total': 0.549, 'startsAt': '2022-09-27T23:00:00.000+02:00'}], 'tomorrow': [{'total': 0.6932, 'startsAt': '2022-09-28T00:00:00.000+02:00'}, {'total': 0.6878, 'startsAt': '2022-09-28T01:00:00.000+02:00'}, {'total': 0.6965, 'startsAt': '2022-09-28T02:00:00.000+02:00'}, {'total': 0.7086, 'startsAt': '2022-09-28T03:00:00.000+02:00'}, {'total': 0.7132, 'startsAt': '2022-09-28T04:00:00.000+02:00'}, {'total': 0.7619, 'startsAt': '2022-09-28T05:00:00.000+02:00'}, {'total': 0.8413, 'startsAt': '2022-09-28T06:00:00.000+02:00'}, {'total': 1.0116, 'startsAt': '2022-09-28T07:00:00.000+02:00'}, {'total': 1.1099, 'startsAt': '2022-09-28T08:00:00.000+02:00'}, {'total': 1.1232, 'startsAt': '2022-09-28T09:00:00.000+02:00'}, {'total': 1.113, 'startsAt': '2022-09-28T10:00:00.000+02:00'}, {'total': 1.111, 'startsAt': '2022-09-28T11:00:00.000+02:00'}, {'total': 1.1076, 'startsAt': '2022-09-28T12:00:00.000+02:00'}, {'total': 1.1122, 'startsAt': '2022-09-28T13:00:00.000+02:00'}, {'total': 1.1174, 'startsAt': '2022-09-28T14:00:00.000+02:00'}, {'total': 1.1183, 'startsAt': '2022-09-28T15:00:00.000+02:00'}, {'total': 1.055, 'startsAt': '2022-09-28T16:00:00.000+02:00'}, {'total': 1.1053, 'startsAt': '2022-09-28T17:00:00.000+02:00'}, {'total': 1.1026, 'startsAt': '2022-09-28T18:00:00.000+02:00'}, {'total': 1.1011, 'startsAt': '2022-09-28T19:00:00.000+02:00'}, {'total': 1.1167, 'startsAt': '2022-09-28T20:00:00.000+02:00'}, {'total': 1.0283, 'startsAt': '2022-09-28T21:00:00.000+02:00'}, {'total': 1.0249, 'startsAt': '2022-09-28T22:00:00.000+02:00'}, {'total': 0.8914, 'startsAt': '2022-09-28T23:00:00.000+02:00'}]}}}]}}}


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
    # (due to clock diff between client and server, we could be getting old/new data)
    last_midnight = datetime.combine(datetime.now().date(), time(0, 0))
    first_hour = datetime.strptime(days['today'][0]['startsAt'], '%Y-%m-%dT%H:%M:%S.%f%z')
    if last_midnight.time() != first_hour.time():
        _log.info(f'We got old data: {first_hour=} != {last_midnight=}')
        raise RuntimeError

    with _price_mutex:
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
    if True:
        _log.info('Using fake data')
        _decode_prices(_fake_data)
        return
    query = '{"query": "{viewer {homes {currentSubscription {priceInfo {today {total startsAt} tomorrow {total startsAt}}}}}}"}'
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


def _try_download():
    try:
        _download()
        # all good, run again 00:00:00
        next_midnight = datetime.combine(datetime.now().date(), time(0, 0)) + timedelta(1)
        _log.info(f'Scheduling next download at {next_midnight}')
        _scheduler.enterabs(next_midnight.timestamp(), 0, _try_download)
    except RuntimeError:
        global _prices
        _prices = {}
        _log.info('Download failed, trying again in 30s')
        _scheduler.enter(30, 0, _try_download)


def _threadloop():
    global _scheduler
    while True:
        _scheduler = sched.scheduler()
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
