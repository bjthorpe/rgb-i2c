from parameters import COLOR_DEFAULT, COLOR_GRADIENT_DEFAULT, COLOR_METHODS, COLOR_METHOD_DEFAULT, ENERGY_TICK_RATE_DEFAULT, GRADIENT_DELAY
from utility import get_color_from_gradient


def process_data(file_=None,
                 color_method=COLOR_METHOD_DEFAULT,
                 energy_tick_rate=ENERGY_TICK_RATE_DEFAULT,
                 gradient_delay=GRADIENT_DELAY,
                 color_gradient=COLOR_GRADIENT_DEFAULT):

    if file_ is not None:
        assert isinstance(file_, str)

    assert isinstance(color_method, str)
    assert isinstance(energy_tick_rate, (float, int))
    assert isinstance(gradient_delay, (float, int))

    assert isinstance(color_gradient, tuple)
    assert len(color_gradient) == 2
    assert all(isinstance(energy, (float, int)) and isinstance(color, int) for energy, color in zip(*color_gradient))

    color_method = color_method.lower()

    # TODO: if a file is provided, read it instead of using the test data.

    # List of all the pieces of information for the simulation: (x, y, time, energy). TODO: remove after testing.
    test_information = [(3, 3, 1.00, 18.0),
                        (3, 3, 2.75, 20.0)]

    assert color_method in COLOR_METHODS, f'{color_method} is an unknown colour method.'

    # Build up the data based on the provided colour method.
    information = []  # Each piece of information which we have read in from file.
    data = []  # The final pieces of data points after the information is processed below.

    if color_method == 'energy':

        for x, y, t, e in test_information:  # x, y, time, energy. # TODO: don't use test_information.
            num_ticks = Information.get_num_ticks_from_energy(e, energy_tick_rate)
            alight_time = Information.get_alight_time(num_ticks, gradient_delay)

            information.append(Information(x, y, e, num_ticks, start_time=t, end_time=t+alight_time))

        information = sorted(information)  # Sorted based on start_time.

        # We need to make sure that any hits on pixels that are already lit up do not overwrite, but instead add, energy to the pixel.
        for n, iA in enumerate(information):  # i for piece of information.

            # Only bother look at pieces of information ahead of the currently considered one.
            for iB in information[n+1:]:

                # We're looking for pieces of information that hit the same pixel and iB starts before the end of iA.
                if (iA.x == iB.x) and (iA.y == iB.y) and (iB.start_time < iA.end_time):

                    # An event, iB, occurs within the time frame that iA is still alight.

                    # Therefore, we erase the ticks of the initial iA event that would occur after iB has started.
                    # This includes remove the final background colour tick of iA, which iB will now deal with.
                    iA.ticks -= Information.get_num_ticks_from_time(iA.end_time-iB.start_time, gradient_delay)

                    # The initial iA event end time is now equal to the latter iB event start time.
                    iA.end_time = iB.start_time

                    # The energy of the latter iB event will be itself plus |the energy of the initial iA event minus the amount it has decayed by|.
                    iB.energy += iA.energy - iA.ticks * energy_tick_rate

                    # Now re-compute the (greater) number of ticks for the latter iB event.
                    iB.ticks = Information.get_num_ticks_from_energy(iB.energy, energy_tick_rate)

                    break


        for i in information:  # i for piece of information.
            # We can now generate all the data points of pixel lights-up via this piece of information.
            data_points = i.get_data_points(color_gradient, energy_tick_rate, gradient_delay)

            # We just now add them to our list of data points.
            data += data_points

    else:
        raise ValueError(f'{color_method} is an unknown colour method.')

    return data


class Information:
    def __init__(self, x, y, energy, ticks, start_time, end_time):
        assert isinstance(x, int)
        assert isinstance(y, int)
        assert isinstance(energy, (float, int))
        assert isinstance(ticks, int)
        assert isinstance(start_time, (float, int))
        assert isinstance(end_time, (float, int))

        self.x = x
        self.y = y
        self.energy = energy
        self.ticks = ticks  # With the given energy, how many `GRADIENT_DELAY` ticks will occur until the pixel is DEFAULT_COLOR again?
        self.start_time = start_time
        self.end_time = end_time

    def __lt__(self, other):
        return self.start_time < other.start_time

    def __repr__(self):
        return f'({self.x},{self.y})  {self.energy:6.2f}  {self.ticks}  {self.start_time:6.2f}  {self.end_time:6.2f}'

    def get_data_points(self, color_gradient=COLOR_GRADIENT_DEFAULT,
                        energy_tick_rate=ENERGY_TICK_RATE_DEFAULT, gradient_delay=GRADIENT_DELAY):
        data_points = []

        for tick in range(self.ticks+1):
            energy = self.energy - tick * energy_tick_rate

            color = COLOR_DEFAULT if energy <= 0.0 else get_color_from_gradient(energy, color_gradient)

            data_points.append(DataPoint(self.x, self.y, color, self.start_time+tick*gradient_delay))

        return data_points

    @staticmethod
    def get_num_ticks_from_energy(energy, energy_tick_rate=ENERGY_TICK_RATE_DEFAULT):
        return 1 + int(energy // energy_tick_rate)

    @staticmethod
    def get_num_ticks_from_time(time_, gradient_delay=GRADIENT_DELAY):
        return 1 + int(time_ // gradient_delay)

    @staticmethod
    def get_alight_time(num_ticks, gradient_delay=GRADIENT_DELAY):
        return num_ticks * gradient_delay


class DataPoint:
    def __init__(self, x, y, color, start_time):
        assert isinstance(x, int)
        assert isinstance(y, int)
        assert isinstance(color, int)
        assert isinstance(start_time, (float, int))

        assert 255 >= color >= 0, 'Colour number should be between 0 and 255.'

        self.x = x
        self.y = y
        self.color = color
        self.start_time = start_time

    def __repr__(self):
        return f'({self.x},{self.y})  {self.color}  {self.start_time:6.2f}'

