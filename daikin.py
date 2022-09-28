import ir


def send(temp, fan):
    temp = int(temp * 2)
    if fan:
        fan = (fan + 2) << 4
    else:
        fan = 0xa0
    chain = [ir.startbit_mark, ir.zerobit_space,
             ir.startbit_mark, ir.zerobit_space,
             ir.startbit_mark, ir.zerobit_space,
             ir.startbit_mark, ir.zerobit_space,
             ir.startbit_mark, ir.zerobit_space,
             ir.startbit_mark, ir.premsg_space]
    frame1 = [0x11, 0xDA, 0x27, 0x00, 0xC5, 0x10, 0x00]
    frame2 = [0x11, 0xDA, 0x27, 0x00, 0x42, 0x00, 0x10]
    frame3 = [0x11, 0xDA, 0x27, 0x00, 0x00,
              0x49,  # Power on & heat mode
              temp,
              0x00,
              fan,  # fan speed and vertical swing
              0x00,  # horizontal swing
              0x00, 0x06, 0x60,  # start & stop timers off
              0x00,  # power and silent off
              0x00,
              0xc1,  # ??
              0x80,  # ?? (sensor & econo ?)
              0x00]
    for f in [frame1, frame2, frame3]:
        ir.add_crc(f)
        ir.add_frame_to_chain(f, chain)
    ir.send_chain(chain)


if __name__ == "__main__":
    ir.init()
    send(21, 0)
