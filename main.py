from manager import run


# Temporary data file for testing.
temp_file = 'test_data/3.dat'  # Data file.
layout = (4, 3)
force_displays = False  # If we request more displays than addresses found, should we reuse displays anyway?
normalise = True  # Should we re-normalise the times of the data to have on avg. 100 data points per 5 sec?

# energy_method is either accumulate or tick.
run(file_=temp_file, layout=layout, \
    energy_method='tick', \
    force_displays=force_displays, normalise=normalise)
exit(0)


from display import get_displays, switch_displays, display_arranger
from smbus import SMBus
from time import sleep

bus = SMBus(1)
displays = get_displays(bus, layout=layout)
print(displays)

display_arranger(bus, displays)

