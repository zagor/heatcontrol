from datetime import datetime, timedelta
from socket import socket, AF_INET, SOCK_DGRAM
from struct import unpack
import logging

_log = logging.getLogger(__name__)


def get_time():
    host = "pool.ntp.org"
    port = 123
    buf = 1024
    TIME1970 = 2208988800  # 1970-01-01 00:00:00
    address = (host, port)
    msg = '\x1b' + 47 * '\0'

    client = socket(AF_INET, SOCK_DGRAM)
    client.sendto(msg.encode('utf-8'), address)
    client.settimeout(2.0)
    msg, address = client.recvfrom(buf)
    t = unpack("!12I", msg)[10]
    t -= TIME1970
    dt = datetime.fromtimestamp(t)
    return dt


def clock_error() -> timedelta:
    try:
        ntp_time = get_time()
    except TimeoutError:
        _log.info('recvfrom timeout')
        return timedelta(0)
    local_time = datetime.now()
    diff = abs(ntp_time - local_time)
    direction = 'ahead of' if local_time > ntp_time else 'behind'
    if diff.days > 0:
        _log.error(f'System clock is {diff.days} day(s) {direction} NTP')
    elif diff.seconds > 300:
        _log.warning(f'System clock is {diff.seconds/60} minutes {direction} NTP')
    elif diff.seconds > 0:
        _log.info(f'System clock is {diff.seconds} s {direction} NTP')
    return diff


if __name__ == "__main__":
    clock_error()
