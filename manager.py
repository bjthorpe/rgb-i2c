from random import randint
from smbus import SMBus
from threading import Thread
from time import sleep, time

from data import COLORS, FRAME_RATE, GRADIENT_DELAY
from display import clear_displays, create_displays
from pixel import create_pixels
from utility import DataPoint, wait_for_matrix_ready


def reset():
    global g_display
    global g_break
    global g_update_display
    global g_update_displays
    global displays

    g_display = None  # The display that is worked on in the background by the data thread and the next to have a display update by the display thread.
    g_break = False  # Global break statement so each thread knows when to quit.
    g_update_display = False  # Signal for the display buffer to update the display. This is set by the data thread. Used in the pre-processed version.
    g_update_displays = False  # Signal for display buffer to update the displays. This is set by the data thread. Used in live version.
    displays = dict()  # Dictionary of displays. {ID (int) : display (Display class)}.


def initialise():
    global bus

    bus = SMBus(1)

    wait_for_matrix_ready()

    reset()


def manager_display_preprocessed():
    global bus
    global displays
    global g_break
    global g_update_display

    time_last_error_msg = time()

    while True:
        start_time = time()

        if g_update_display:
            g_display.display_current_frame(bus)

            g_update_display = False

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


def manager_display_live():
    global bus
    global displays
    global g_break
    global g_update_displays

    time_last_error_msg = time()

    while True:
        start_time = time()

        if g_update_displays:
            for display in displays.values():
                if display.needs_updating:
                    display.display_current_frame(bus)
                    display.needs_updating = False

            g_update_displays = False

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


def manager_data_preprocessed():
    global bus
    global displays
    global g_display
    global g_break
    global g_update_display

    # A dictionary to store which display is represent what data points. TODO: automate this.
    xy_to_display = {(i, j): displays[0] for i in range(8) for j in range(8)}

    # List of all data for the simulation: (x, y, time, gradient, timers). TODO: remove after testing.
    test_data = [(2, 5, 1.00, range(0, 50,  10)),  # After 1.0 second, apply a gradient to co-ordinate (2, 5).
                 (5, 7, 1.25, range(30, 0, -10))]  # After 2.5 seconds, apply a gradient to co-ordinate (5, 7).

    # Build up the data with time differentials. TODO: update this with a data gathering/input function rather than test_data.
    data = []
    for x, y, t, gradient in test_data:
        for n, color in enumerate(gradient):
            data.append(DataPoint(x, y, color, time_=t+n*GRADIENT_DELAY))
    data = sorted(data)

    time_last_error_msg = -999.0
    previous_data_point_time = 0.0

    first_pass = True
    no_new_data = False

    t1 = time()

    while True:
        start_time = time()

        try:
            data_point = data.pop(0)
        except IndexError:
            no_new_data = True

        if no_new_data:
            g_break = True

        if g_break:
            break  # TODO: Consider clearing each display.

        g_display = xy_to_display.get((data_point.x, data_point.y), None)

        assert g_display is not None, 'Cannot find a display to show pixel ({data_point.x},{data_point.y}).'

        g_display.update_pixel(data_point.x, data_point.y, data_point.color)

        g_display.switch_buffer()

        g_update_display = True

        g_display.copy_buffer()

        end_time = time()

        wait_time = data_point.time - previous_data_point_time - (end_time - start_time)

        previous_data_point_time = data_point.time

        if wait_time < 0.001 and not first_pass:
            if (time() - time_last_error_msg) > 1.0:
                print('Warning: time to update frame longer than time between data points.')
                time_last_error_msg = time()
        else:
            sleep(wait_time)

        first_pass = False

    t2 = time()

    print('Time taken', t2-t1)


def manager_data_live():
    global bus
    global displays
    global g_break
    global g_update_displays

    test_pixel_updated = False  # TODO: remove after testing.
    test_timer = 5.0  # TODO: remove after testing.

    change_detected = False  # Flag for recording if there are any change in pixels of a display.

    time_last_change_check = time()
    time_last_error_msg = -999.0

    t1 = time()

    previous_data_point_time = 0.0

    while True:
        start_time = time()

        change_detected = False

        # If a new data detection point comes in, apply it.
        # START OF TESTS -> TODO: remove after testing.
        for display in displays.values():
            # TEST 1: Update a pixel with a gradient after a few seconds ->
            if test_timer < 4.0 and not test_pixel_updated:
                display.update_pixel_gradient(2, 5, gradient=range(0, 50, 10))
                test_pixel_updated = True
    
            # TEST 2: random frames ->
            #random_frame = create_pixels([randint(0, 255) for _ in range(size * size)])
            #display.update_frame(random_frame)
        # END OF TESTS ->

        # Check for any change in pixels of the displays.
        tick = time() - time_last_change_check

        for display in displays.values():
            display.check_pixel_changes(tick)

            change_detected = change_detected or display.change_detected

        time_last_change_check = time()

        # Apply changes to background frame if any have been detected.
        for display in displays.values():
            display.apply_pixel_changes()

        # Pixels updated, so switch the buffer if a chance has been detected.
        for display in displays.values():
            if display.change_detected:
                display.switch_buffer()
                display.needs_updating = True

        if change_detected:
            g_update_displays = True  # Tells the display thread to update the display as we've had a change.

        # Copy the displayed frame to the buffered frame if a change was detected.
        for display in displays.values():
            if display.change_detected:
                display.copy_buffer()

        for display in displays.values():
            display.change_detected = False

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

        # TODO: remove after testing.
        if test_timer < 0.0:
            g_break = True

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

    '''
    thread_display = Thread(target=manager_display_live, name='Display')
    thread_data = Thread(target=manager_data_live, name='Data')
    '''

    thread_display = Thread(target=manager_display_preprocessed, name='Display')
    thread_data = Thread(target=manager_data_preprocessed, name='Data')

    start_time = time()

    thread_display.start()
    thread_data.start()

    thread_display.join()
    thread_data.join()

    end_time = time()

    clear_displays(bus, displays)
    reset()

