import ir


def send(temp, fan):
    # Toshiba message format:
    #
    # bits of frame[5]:
    #   TTTTxxxx where T is (temp - 17)
    # bits of frame[6]:
    #   SSSxxMMM where
    #     S is (speed + 2), 0 is silent, 1 is auto
    #     M is mode: 1:cold 2:dry 3:hot, 7:off

    frame = [0xF2, 0x0D, 0x03, 0xFC, 0x01, 0x00, 0x00, 0x00]
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
