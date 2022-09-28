from time import sleep

import config
import ntp
import temperature
import tibber
import webserver
import logging


def init():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s:%(name)s:%(message)s')
    ntp.clock_error()
    config.init()
    tibber.init()
    webserver.init()
    temperature.init()


init()
while True:
    sleep(100)
