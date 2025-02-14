from smbus import SMBus
from threading import Thread
from time import sleep, time

from data import Event, process_data
from display import clear_displays, get_displays
from parameters import FRAME_RATE, EVENT_TIME_DIFFERENCE_TOLERANCE, WAIT_DISPLAY
from utility import wait_for_matrix_ready


def get_bus():
    return SMBus(1)


def reset():
    global g_bus
    global g_displays
    global g_break

    g_bus = None  # The SMBus.
    g_displays = [] # List of displays.
    g_break = False  # Global break statement so each thread knows when to quit.


def initialise(layout=None, force_displays=False):
    global g_bus
    global g_displays

    reset()

    g_bus = get_bus()

    wait_for_matrix_ready()

    g_displays = get_displays(g_bus, layout, force_displays)

    assert len(g_displays) > 0, 'No displays found.'

    clear_displays(g_bus, g_displays)



def display_manager():
    global g_bus
    global g_displays
    global g_break

    while True:
        for display in g_displays:
            if display.needs_updating:
                display.display_current_frame(g_bus, forever=True)  # forever=True as timing is handled by the data manager.

                display.needs_updating = False

        sleep(WAIT_DISPLAY)

        if g_break:
            clear_displays(g_bus, g_displays)
            break


def data_manager(data):
    global g_bus
    global g_displays
    global g_break

    assert isinstance(data, (list, tuple))
    assert all(isinstance(d, Event) for d in data)

    time_last_error_msg = -999.0
    previous_start_time = 0.0

    first_pass = True
    no_new_data = False

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
            break

        # First, go and get all the IDs of the displays that are to be updated.
        updated_display_IDs = set(event.display_IDs)

        # Then, use the set here so we only copy the buffers once.
        for ID in updated_display_IDs:
            g_displays[ID].copy_buffer()

        # Finally, actually do the pixel updates.
        for x, y, color, ID in event:
            g_displays[ID].set_buffer_pixel(x, y, color)

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
            g_displays[ID].needs_updating = True

        first_pass = False


def run(file_=None, layout=None, force_displays=False, normalise=False):
    global g_bus
    global g_displays

    if file_ is not None:
        assert isinstance(file_, str)

    assert isinstance(force_displays, bool)
    assert isinstance(normalise, bool)

    time_start = time()

    initialise(layout, force_displays)

    data = process_data(file_, g_displays, normalise=normalise)

    thread_display = Thread(target=display_manager, name='Display')
    thread_data = Thread(target=data_manager, args=(data,), name='Data')

    time_middle = time()

    thread_display.start()
    thread_data.start()

    thread_display.join()
    thread_data.join()

    time_end = time()

    print('Initialisation time', time_middle-time_start)
    print('Run time', time_end-time_middle)

    clear_displays(g_bus, g_displays)

    reset()

