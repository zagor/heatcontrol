OUTPUT = True


class Pi:
    def connected(self) -> bool:
        return True

    def set_mode(self, pin, mode):
        pass

    def wave_add_generic(self, l):
        pass

    def wave_create(self) -> int:
        return 1

    def wave_chain(self, chain):
        return True

    def wave_tx_busy(self):
        return False

    def wave_delete(self, id):
        pass

    def stop(self):
        pass


def pi() -> Pi:
    return Pi()


def pulse(on, off, delay):
    return True
