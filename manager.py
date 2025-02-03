from random import randint
from smbus import SMBus
from threading import Thread
from time import sleep, time

from data import COLORS, FRAME_RATE
from display import clear_displays, create_displays
from pixel import create_pixels
from utility import wait_for_matrix_ready


def reset():
    global g_break
    global displays

    g_break = False  # Global break statement so each thread knows when to quit.
    displays = dict()  # Dictionary of displays. {ID (int) : display (Display class)}.


def initialise():
    global bus

    bus = SMBus(1)

    wait_for_matrix_ready()

    reset()


def buffer_display():
    global bus
    global displays
    global g_break

    time_last_error_msg = time()

    while True:
        start_time = time()

        for display in displays.values():
            display.display_current_frame(bus)

        end_time = time()

        sleep_time = FRAME_RATE - (end_time - start_time)

        if sleep_time < 0.001:
            if (time() - time_last_error_msg) > 1.0:
                print('Warning: time to display frames taking longer than the frame rate.')
                time_last_error_msg = time()
        else:
            sleep(sleep_time)

        if g_break:
            break


def buffer_data():
    global bus
    global displays
    global g_break

    test_pixel_updated = False  # TODO: remove after testing.
    test_timer = 5.0  # TODO: remove after testing.

    time_last_error_msg = time()

    t1 = time()

    while True:
        start_time = time()

        # Copy the displayed frame to the buffered frame.
        for display in displays.values():
            display.copy_buffer()

        # If a new data detection point comes in, apply it.
        # START OF TESTS -> TODO: remove after testing.
        for display in displays.values():
            # TEST 1: Update a pixel with a gradient after a few seconds ->
            if test_timer < 4.0 and not test_pixel_updated:
                display.update_pixel(2, 5, gradient=[randint(0, 255) for _ in range(5)])
                test_pixel_updated = True
    
            # TEST 2: random frames ->
            #random_frame = create_pixels([randint(0, 255) for _ in range(size * size)])
            #display.update_frame(random_frame)
        # END OF TESTS ->

        # Change any pixel colours if enough time has passed.
        for display in displays.values():
            display.check_pixel_changes(FRAME_RATE)

        # Pixels updated and frame copying complete, so switch the buffer.
        for display in displays.values():
            display.switch_buffer()

        end_time = time()

        sleep_time = FRAME_RATE - (end_time - start_time)

        if sleep_time < 0.001:
            if (time() - time_last_error_msg) > 1.0:
                print('Warning: time to copy data between buffers and pixel updates is taking longer than the frame rate.')
                time_last_error_msg = time()
        else:
            sleep(sleep_time)

        # TODO: remove after testing.
        test_timer -= FRAME_RATE

        if test_timer < 0.0:
            g_break = True
        # TODO: remove after testing.

        if g_break:
            break

    t2 = time()

    print('Time taken', t2-t1)


def run():
    global bus
    global displays

    initialise()

    displays = create_displays(bus)
    assert len(displays) > 0, 'No displays found.'
    clear_displays(bus, displays)

    thread_display = Thread(target=buffer_display, name='Display')
    thread_data = Thread(target=buffer_data, name='Data')

    start_time = time()

    thread_display.start()
    thread_data.start()

    thread_display.join()
    thread_data.join()

    end_time = time()

    clear_displays(bus, displays)
    reset()

