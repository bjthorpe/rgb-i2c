from random import randint
from smbus import SMBus
from time import sleep, time

from data import COLORS, FRAME_RATE
from display import clear_displays, create_displays
from pixel import create_pixels
from utility import wait_for_matrix_ready


def run():
    bus = SMBus(1)
    wait_for_matrix_ready()

    displays = create_displays(bus)
    assert len(displays) > 0, 'No displays found.'
    clear_displays(bus, displays)

    display = displays[0]

    size = 8

    test_timer = 5.0
    start_time = time()

    test_pixel_updated = False

    while True:

        # TEST 1: Update a pixel with a gradient after a few seconds ->
        if test_timer < 4.0 and not test_pixel_updated:
            display.update_pixel(2, 5, gradient=[randint(0, 255) for _ in range(5)])
            test_pixel_updated = True

        # TEST 2: random frames ->
        #random_frame = create_pixels([randint(0, 255) for _ in range(size * size)])
        #display.update_frame(random_frame)

        # END OF TESTS ->
        display.check_pixel_changes(FRAME_RATE)
        display.display_current_frame(bus)

        sleep(FRAME_RATE)

        test_timer -= FRAME_RATE

        if test_timer <= 0.0:
            break

    end_time = time()

    clear_displays(bus, displays)

    print(f'Time taken {end_time-start_time}.')


run()

