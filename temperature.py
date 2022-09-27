import time
import logging
from sched import scheduler
from datetime import datetime, timedelta
from threading import Thread

import config
import ir
import tibber

_log = logging.getLogger(__name__)
_scheduler: scheduler
_default_config = {'high_price': 3.00,
                   'high_price_temp': 19,
                   'high_price_fan': 0,
                   'low_price': 0.80,
                   'low_price_temp': 25,
                   'low_price_fan': 0,
                   'normal_temp': 22,
                   'normal_fan': 0}
current_temp = 0
current_fan = 0


def _schedule_next_hour():
    next_hour = datetime.now().replace(microsecond=0, second=0, minute=0) + timedelta(hours=1)
    _log.info(f'Scheduling next temperature setting at {next_hour}')
    _scheduler.enterabs(next_hour.timestamp(), 0, _set_temperature)


def _set_temperature():
    if not tibber.has_prices():
        _scheduler.enter(1, 0, _set_temperature)
        return
    price = tibber.get_current_price()
    if price >= config.get('high_price'):
        tariff = 'High'
        temperature = config.get('high_price_temp')
        fan = config.get('high_price_fan')
    elif price <= config.get('low_price'):
        tariff = 'Low'
        temperature = config.get('low_price_temp')
        fan = config.get('low_price_fan')
    else:
        tariff = 'Mid'
        temperature = config.get('normal_temp')
        fan = config.get('normal_fan')
    try:
        global current_temp, current_fan
        if temperature != current_temp or fan != current_fan:
            _log.info(f'{tariff} price {price:.02f} kr, setting temperature {temperature}°C and fan {fan}')
            ir.send(temp=temperature, fan=fan)
        else:
            _log.info(f'{tariff} price {price:.02f} kr, keeping temperature {temperature}°C and fan {fan}')
        current_temp = temperature
        current_fan = fan
    except Exception:
        pass
    _schedule_next_hour()


def _threadloop():
    while True:
        global _scheduler
        _scheduler = scheduler(time.time)
        _scheduler.enter(0, 0, _set_temperature)
        _scheduler.run(blocking=True)
        _log.error('Unexpected exit')
        # we should never run out of scheduled events, but if we do just start over


def init():
    config.put_defaults(_default_config)
    t = Thread(target=_threadloop, name='Temperature')
    t.daemon = True
    t.start()
