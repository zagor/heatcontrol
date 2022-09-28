import logging
import time
import signal
from typing import Optional, Any

try:
    import pigpio  # apt install python3-pigpio
except ModuleNotFoundError:
    import virtual_pigpio as pigpio

import config

_default_config = {'ir_gpio_pin': '14',
                   'heater_model': 'toshiba'}

# frames
msgstart_mark: int = 0
msgstart_space: int = 0
onebit_space: int = 0
zerobit_space: int = 0
startbit_mark: int = 0
interframe_space: int = 0
premsg_space: int = 0

_pi: pigpio.pi
_log = logging.getLogger(__name__)


def _reverse_byte(value: int) -> int:
    assert value < 256
    return int('{:08b}'.format(value)[::-1], 2)


def reverse_frame(frame):
    for i in range(len(frame)):
        frame[i] = _reverse_byte(frame[i])

def carrier(gpio, frequency, micros):
    """
    Generate carrier square wave.
    """
    wf = []
    cycle = 1000.0 / frequency
    cycles = int(round(micros/cycle))
    on = int(round(cycle / 2.0))
    sofar = 0
    for c in range(cycles):
        target = int(round((c+1)*cycle))
        sofar += on
        off = target - sofar
        sofar += off
        wf.append(pigpio.pulse(1 << gpio, 0, on))
        wf.append(pigpio.pulse(0, 1 << gpio, off))
    return wf


def add_crc(frame):
    crc = 0
    for byte in frame:
        crc += byte
    frame.append(crc & 0xff)


def bits(byte):
    for i in range(8):
        yield (byte >> i) & 1


def add_frame_to_chain(frame, chain):
    # start bit
    chain.append(msgstart_mark)
    chain.append(msgstart_space)

    # data bits
    for byte in frame:
        for bit in bits(byte):
            chain.append(startbit_mark)
            if bit:
                chain.append(onebit_space)
            else:
                chain.append(zerobit_space)

    # stop bit
    chain.append(startbit_mark)
    chain.append(interframe_space)


def send_chain(chain):
    _pi.wave_chain(chain)
    while _pi.wave_tx_busy():
        time.sleep(0.1)


def _setup_waves(gpio):
    ZERO = 500
    ONE  = ZERO * 3
    FREQ = 38 # kHz

    global msgstart_mark
    global msgstart_space
    global onebit_space
    global zerobit_space
    global startbit_mark
    global interframe_space
    global premsg_space

    global _pi
    _pi = pigpio.pi()
    if not _pi.connected:
        print("pigpio not connected")
        exit(0)

    _pi.set_mode(gpio, pigpio.OUTPUT)

    _pi.wave_add_generic(carrier(gpio, FREQ, ZERO * 8))
    msgstart_mark = _pi.wave_create()

    _pi.wave_add_generic([pigpio.pulse(0, 0, ZERO * 4)])
    msgstart_space = _pi.wave_create()

    _pi.wave_add_generic([pigpio.pulse(0, 0, ONE)])
    onebit_space = _pi.wave_create()

    _pi.wave_add_generic([pigpio.pulse(0, 0, ZERO)])
    zerobit_space = _pi.wave_create()

    _pi.wave_add_generic(carrier(gpio, FREQ, ZERO))
    startbit_mark = _pi.wave_create()

    _pi.wave_add_generic([pigpio.pulse(0, 0, ZERO * 20)])
    interframe_space = _pi.wave_create()

    _pi.wave_add_generic([pigpio.pulse(0, 0, ZERO * 50)])
    premsg_space = _pi.wave_create()


def _cleanup():
    for wave in [msgstart_mark, msgstart_space,
                 onebit_space, zerobit_space,
                 startbit_mark, interframe_space,
                 premsg_space]:
        if wave:
            _pi.wave_delete(wave)
    if _pi:
        _pi.stop()


def print_frame(frame):
    for byte in frame:
        print(f'{byte:02x} ', end='')
    print()


def send(temperature, fan_speed):
    device.send(temperature, fan_speed)


def init():
    config.put_defaults(_default_config)
    ir_pin = config.get('ir_gpio_pin')
    signal.signal(signal.SIGTERM, _cleanup)
    _setup_waves(ir_pin)

    model = config.get('heater_model')
    global device
    if model == 'toshiba':
        import toshiba
        device = toshiba
    elif model == 'daikin':
        import daikin
        device = daikin
    elif model == 'mitsubishi':
        import mitsubishi
        device = mitsubishi
