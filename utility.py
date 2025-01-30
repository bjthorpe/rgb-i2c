from time import sleep

from data import WAIT_INITIAL


def wait_for_matrix_ready():
    sleep(WAIT_INITIAL)


def int_to_bytes(num):
    assert isinstance(num, int)

    assert num <= 65535, f'{num} too big, should be <= 65535'
    assert num >= 0, f'{num} too small, should be >= 0'

    return [int(i) for i in num.to_bytes(2, byteorder='big', signed=True)]

