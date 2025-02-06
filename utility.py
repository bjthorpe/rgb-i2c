from time import sleep

from parameters import GRADIENT_DELAY, WAIT_INITIAL


def wait_for_matrix_ready():
    sleep(WAIT_INITIAL)


def int_to_bytes(num):
    assert isinstance(num, int)

    assert num <= 65535, f'{num} too big, should be <= 65535'
    assert num >= 0, f'{num} too small, should be >= 0'

    return [int(i) for i in num.to_bytes(2, byteorder='big', signed=True)]


def get_color_from_gradient(energy, color_gradient):
    assert energy > 0.0

    energy_bounds, colors = color_gradient

    # Loop through the energy bounds from smallest to largest.
    for upper_energy, color in zip(energy_bounds[::-1], colors[::-1]):
        if energy <= upper_energy:
            return color
    else:
        return colors[0]  # If we the energy doesn't fit anywhere, assume it is the highest energy.

