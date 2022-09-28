import ir


def send(temp, fan):
    # Mitsubishi message format:
    #
    # bits of frame[5]:
    #   xxPxxxxx where P is Power on/off
    # bits of frame[6]:
    #   xxMMMxxx where M is Mode: 1:hot 2:dry 3:cold, 4: auto
    # bits of frame[7]:
    #   xxxxTTTT where T is (temp - 16)
    # bits of frame[9]:
    #   x1VVVFFF where
    #     V is vane (0:auto, 1-5, 7:automove?)
    #     F is fan speed (1-4, 0:auto, 5:silent)

    frame = [0x23, 0xCB, 0x26, 0x01, 0x00, 0x20, 0x08, 0x06, 0x30,
             0x45, 0x67, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]


    if temp < 17:
        temp = 17
    elif temp > 30:
        temp = 30
    frame[5] = (temp - 17) << 4

    if fan:
        # speeds start at 3
        fan += 2
    else:
        # auto is 1
        fan = 1
    mode = 3  # hot
    frame[6] = fan << 5 | mode

    ir.add_crc(frame)
    ir.reverse_frame(frame)
    chain = [ir.msgstart_mark, ir.msgstart_space]
    ir.add_frame_to_chain(frame, chain)
    ir.add_frame_to_chain(frame, chain)
    ir.send_chain(chain)


if __name__ == "__main__":
    ir.init()
    send(21, 0)
