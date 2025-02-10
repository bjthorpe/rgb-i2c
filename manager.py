from smbus import SMBus
from threading import Thread
from time import sleep, time

from data import process_data
from display import clear_displays, create_displays
from parameters import FRAME_RATE, EVENT_TIME_DIFFERENCE_TOLERANCE, WAIT_DISPLAY
from utility import wait_for_matrix_ready


def reset():
    global g_displays
    global g_break

    g_displays = dict()  # Dictionary of displays. {ID (int) : display (Display)}.
    g_updates = []  # A list of bools that signals for the display buffer to update which displays.
    g_break = False  # Global break statement so each thread knows when to quit.


def initialise():
    global bus

    bus = SMBus(1)

    wait_for_matrix_ready()

    reset()


def display_manager():
    global bus
    global g_displays
    global g_updates
    global g_break

    while True:
        for ID, display in g_displays.items():
            if g_updates[ID]:
                display.display_current_frame(bus)

                g_updates[ID] = False

        sleep(WAIT_DISPLAY)

        if g_break:
            break


def data_manager(file_=None, normalise_time_data=False):
    global bus
    global g_displays
    global g_updates
    global g_break

    if file_ is not None:
        assert isinstance(file_, str)

    assert isinstance(normalise_time_data, bool)

    # A dictionary to store which display is represent what data points. TODO: automate this.
    xy_to_display_ID = {(i, j): 0 for i in range(8) for j in range(8)}

    data = process_data(file_, normalise=normalise_time_data)

    time_last_error_msg = -999.0
    previous_start_time = 0.0

    first_pass = True
    no_new_data = False

    t1 = time()

    while True:
        start_time = time()

        # Get the next event.
        try:
            event = data.pop(0)
        except IndexError:
            no_new_data = True

        if no_new_data:
            g_break = True

        if g_break:
            break  # TODO: Consider clearing each display.

        # First, go and get all the IDs of the displays that are to be updated.
        updated_display_IDs = set()

        for x, y, color in event:
            ID = xy_to_display_ID.get((x, y), None)

            assert ID is not None, f'Cannot find a display to show pixel ({x},{y}).'

            updated_display_IDs.add(ID)

        # Then, use the set here so we only copy the buffers once.
        for ID in updated_display_IDs:
            g_displays[ID].copy_buffer()

        # Finally, actually do the pixel updates.
        for x, y, color in event:
            ID = xy_to_display_ID.get((x, y), None)

            g_displays[ID].update_pixel(x, y, color)

        end_time = time()

        wait_time = event.start_time - previous_start_time - (end_time - start_time)

        previous_start_time = event.start_time

        if wait_time < EVENT_TIME_DIFFERENCE_TOLERANCE:
            if (time() - time_last_error_msg) > 1.0 and not first_pass:
                print('Warning: time to update frame longer than time between events.')
                time_last_error_msg = time()
        else:
            sleep(wait_time)

        # The pre-processed event is now ready to be displayed, switch the buffers and set the update flags for the display thread.
        for ID in updated_display_IDs:
            g_displays[ID].switch_buffer()
            g_updates[ID] = True

        first_pass = False

    t2 = time()

    print('Time taken', t2-t1)


def run(file_=None, normalise_time_data=False):
    global bus
    global g_displays
    global g_updates

    if file_ is not None:
        assert isinstance(file_, str)

    assert isinstance(normalise_time_data, bool)

    initialise()

    g_displays = create_displays(bus)
    g_updates = [False] * len(g_displays)
    assert len(g_displays) > 0, 'No displays found.'
    clear_displays(bus, g_displays)

    thread_display = Thread(target=display_manager, name='Display')
    thread_data = Thread(target=data_manager, args=(file_, normalise_time_data), name='Data')

    start_time = time()

    thread_display.start()
    thread_data.start()

    thread_display.join()
    thread_data.join()

    end_time = time()

    clear_displays(bus, g_displays)
    reset()

