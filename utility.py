from time import sleep

from data import GRADIENT_DELAY, WAIT_INITIAL


class DataPoint:
    def __init__(self, x, y, color, time_):
        assert isinstance(x, int)
        assert isinstance(y, int)
        assert isinstance(color, int)
        assert isinstance(time_, (float, int))

        assert 255 >= color >= 0, 'Colour number should be between 0 and 255.'

        self.x = x
        self.y = y
        self.color = color
        self.time = time_

    def __repr__(self):
        return f'({self.x},{self.y}) {self.color} {self.time}'

    def __lt__(self, other):
        return self.time < other.time


def wait_for_matrix_ready():
    sleep(WAIT_INITIAL)


def int_to_bytes(num):
    assert isinstance(num, int)

    assert num <= 65535, f'{num} too big, should be <= 65535'
    assert num >= 0, f'{num} too small, should be >= 0'

    return [int(i) for i in num.to_bytes(2, byteorder='big', signed=True)]

