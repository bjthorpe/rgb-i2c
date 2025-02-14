from numpy import loadtxt

from display import Display, get_display_ID
from parameters import COLOR_DEFAULT, COLOR_GRADIENT_DEFAULT, COLOR_METHODS, COLOR_METHOD_DEFAULT, \
                       ENERGY_TICK_RATE_DEFAULT, EVENT_TIME_DIFFERENCE_TOLERANCE, GRADIENT_DELAY, EXAMPLE_DATA
from utility import get_color_from_gradient, get_num_ticks, get_quantity


def process_data(file_,
                 displays,
                 color_method=COLOR_METHOD_DEFAULT,
                 energy_tick_rate=ENERGY_TICK_RATE_DEFAULT,
                 gradient_delay=GRADIENT_DELAY,
                 color_gradient=COLOR_GRADIENT_DEFAULT,
                 normalise=False):

    assert isinstance(file_, str)
    assert all(isinstance(display, Display) for display in displays)
    assert isinstance(color_method, str)
    assert isinstance(energy_tick_rate, (float, int))
    assert isinstance(gradient_delay, (float, int))
    assert isinstance(color_gradient, tuple)
    assert len(color_gradient) == 2
    assert all(isinstance(energy, (float, int)) and isinstance(color, int) for energy, color in zip(*color_gradient))
    assert isinstance(normalise, bool)  # Do we want to normalise the time of the data to have on avg. 100 data points per 30 sec?

    color_method = color_method.strip().lower()

    assert color_method in COLOR_METHODS, f'{color_method} is an unknown colour method.'

    data_raw = process_file(file_, normalise)  # The raw data from file.
    data_processed = []  # The data after processing it into DataPoint classes.
    events = []  # The data after taking into account colour patterns and overlapping data points.

    if color_method == 'energy':  # Base the colouring on the energy of the detection. Energy-specific code is highlighted with ***.

        for t, ID, x, y, s, e in data_raw:  # time, crystal_ID, x, y, side, energy.
            num_ticks = get_num_ticks(e, energy_tick_rate)  # *** Number of ticks this pixel has is based on the energy. ***
            alight_time = get_quantity(num_ticks, gradient_delay)  # How long should this pixel be lit up for?

            data_processed.append(DataPoint(x, y, s, e, num_ticks, start_time=t, end_time=t+alight_time))

        data_processed = sorted(data_processed)  # Sorted based on start_time.

        # We need to make sure that any hits on pixels that are already lit up do not overwrite, but instead add, energy to the pixel.
        for n, dA in enumerate(data_processed):  # d for data point.

            # Only bother look at data points ahead of the currently considered one.
            for dB in data_processed[n+1:]:

                # We're looking for data points that hit the same pixel and iB starts before the end of iA.
                if (dA.x == dB.x) and (dA.y == dB.y) and (dB.start_time < dA.end_time):

                    # An event, dB, occurs within the time frame that dA is still alight.

                    # Therefore, we erase the ticks of the initial iA event that would occur after iB has started.
                    # This includes remove the final background colour tick of iA, which iB will now deal with.
                    dA.ticks -= get_num_ticks(dA.end_time-dB.start_time, gradient_delay)

                    # The initial iA event end time is now equal to the latter iB event start time.
                    dA.end_time = dB.start_time

                    # The energy of the latter iB event will be itself plus |the energy of the initial iA event minus the amount it has decayed by|.
                    dB.energy += dA.energy - dA.ticks * energy_tick_rate

                    # Now re-compute the (greater) number of ticks and the (later) end time for the latter iB event.
                    dB.ticks = get_num_ticks(dB.energy, energy_tick_rate)  # *** Number of ticks this pixel has is based on the energy. ***
                    dB.end_time = dB.start_time + get_quantity(dB.ticks, gradient_delay)  # Start time + alight time.

                    # If dA overlaps with a dC, this will be dealt with by dB, so may as well break here to save time.
                    break

        # *** We get the events based on the energy. ***
        events += sum([get_energy_events(data_point, displays, color_gradient, energy_tick_rate, gradient_delay) for data_point in data_processed], [])

    else:
        raise ValueError(f'{color_method} is an unknown colour method.')

    # Make sure the events are in time order.
    events = sorted(events)

    # All events at the moment are individual pixel updates.
    # Let's group multiple pixel updates together into a single event, IF they are very close together in time.
    events = group_events(events)

    return events


def process_file(file_, normalise=False):
    assert isinstance(file_, str)
    assert isinstance(normalise, bool)  # Do we want to normalise the time data to have on avg. 100 data points per 30 sec?

    data = loadtxt(file_)

    assert len(data.shape) == 2, 'Need more than 1 data point.'  # Dealing with numpy's awkward shape size.
    assert data.shape[0] > 0, f'No data in file {file_}.'
    assert data.shape[1] == 6, 'Number of columns of data should be 6.'

    time, ID, side, x, y, energy = zip(*data)

    time = list(map(float, time))
    ID = list(map(int, ID))
    side = list(map(int, side))
    x = list(map(int, x))
    y = list(map(int, y))
    energy = list(map(float, energy))

    assert all(t >= 0.0 for t in time), 'Data point with time < 0.'
    assert all(s in (0, 1) for s in side), 'Data point with side not equal to 0 or 1.'
    assert all(x_i >= 0 for x_i in x), 'Data point with x pixel < 0.'
    assert all(y_i >= 0 for y_i in y), 'Data point with y pixel < 0.'
    assert all(e >= 0.0 for e in energy), 'Data point with energy < 0.'

    if normalise:
        minimum = min(time)
        difference = max(time) - minimum
        num_data_points = data.shape[0]
        factor = 30.0 * float(num_data_points) / 100.0

        time = [factor * (t - minimum) / (difference) for t in time]

    return zip(time, ID, x, y, side, energy)  # Note: we have put side to the right of (x, y) rather than the left.


def group_events(events):
    ''' Group events together that occur within the EVENT_TIME_DIFFERENCE_TOLERANCE. '''

    assert all(isinstance(e, Event) for e in events)

    grouped_events = []

    n = 0  # Manual counter, so we can avoid already-processed events.

    while n < len(events):
        event = events[n]

        x_values = event.x_values
        y_values = event.y_values
        colors = event.colors
        display_IDs = event.display_IDs

        count = 0

        # Loop through events ahead of this.
        for future_event in events[n+1:]:

            # If the future event start time is very close to this event, get its data.
            if (future_event.start_time - event.start_time) < EVENT_TIME_DIFFERENCE_TOLERANCE:
                x_values += future_event.x_values
                y_values += future_event.y_values
                colors += future_event.colors
                display_IDs += future_event.display_IDs

                count += 1  # Record how many events we have processed.

            else:
                break  # We can stop looking as the events are ordered.

        grouped_events.append(Event(x_values, y_values, colors, display_IDs, event.start_time))

        n += count + 1  # `count` number of future events processed. +1 for `event` itself.

    return grouped_events


def get_energy_events(data_point, displays, color_gradient=COLOR_GRADIENT_DEFAULT,
                      energy_tick_rate=ENERGY_TICK_RATE_DEFAULT, gradient_delay=GRADIENT_DELAY):
    ''' This takes a DataPoint and creates the associated events based on the energy. For example,
        if a data point is a pixel light-up with 13eV, then if the energy_tick_rate is 5eV, then
        the events will be a 13eV colour, 8eV colour `gradient_delay` seconds later, 3 eV colour
        `gradient_delay` seconds later, 0 eV (blank) colour `gradient_delay` seconds later. '''

    events = []

    for tick in range(data_point.ticks+1):
        energy = data_point.energy - tick * energy_tick_rate

        color = COLOR_DEFAULT if energy <= 0.0 else get_color_from_gradient(energy, color_gradient)

        display_ID = get_display_ID(displays, data_point.x, data_point.y, data_point.side)

        x = data_point.x % displays[display_ID].size  # Turns global x into local.
        y = data_point.y % displays[display_ID].size  # Turns global y into local.

        events.append(Event([x], [y], [color], [display_ID], data_point.start_time+tick*gradient_delay))  # x, y, color, ID are lists.

    return events


class DataPoint:
    def __init__(self, x, y, side, energy, ticks, start_time, end_time):
        assert isinstance(x, int)
        assert isinstance(y, int)
        assert isinstance(side, int)
        assert isinstance(energy, (float, int))
        assert isinstance(ticks, int)
        assert isinstance(start_time, (float, int))
        assert isinstance(end_time, (float, int))

        self.x = x  # This is the global x co-ordinate.
        self.y = y  # This is the global y co-ordinate.
        self.side = side
        self.energy = energy
        self.ticks = ticks  # With the given energy, how many `GRADIENT_DELAY` ticks will occur until the pixel is DEFAULT_COLOR again?
        self.start_time = start_time
        self.end_time = end_time

    def __lt__(self, other):
        return self.start_time < other.start_time

    def __repr__(self):
        return f'({self.x},{self.y})  {self.energy:6.2f}  {self.ticks}  {self.start_time:6.2f}  {self.end_time:6.2f}'


class Event:
    def __init__(self, x_values, y_values, colors, display_IDs, start_time):
        assert all(isinstance(x, int) for x in x_values)
        assert all(isinstance(y, int) for y in y_values)
        assert all(isinstance(color, int) for color in colors)
        assert all(isinstance(ID, int) for ID in display_IDs)
        assert all(255 >= color >= 0 for color in colors)
        assert isinstance(start_time, (float, int))

        self.x_values = x_values  # These are the local x co-ordinates.
        self.y_values = y_values  # These are the local y co-ordinates.
        self.colors = colors
        self.display_IDs = display_IDs
        self.start_time = start_time

    def __iter__(self):
        return iter(zip(self.x_values, self.y_values, self.colors, self.display_IDs))

    def __lt__(self, other):
        return self.start_time < other.start_time

    def __repr__(self):
        s = ''

        for x, y, color, display_ID in self:
            s += f'({x},{y})  {color}  {self.start_time:6.2f}\n'

        return s[:-1]

