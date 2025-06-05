from display import get_displays, switch_displays, switch_displays_from_chars, display_arranger
from manager import run
from smbus import SMBus


file_ = 'test_data/4.dat'  # Data file.
layout = (4, 4)
force_displays = False  # If we request more displays than addresses found, should we reuse displays anyway?
normalise = True  # Should we re-normalise the times of the data to have on avg. 100 data points per 5 sec?

bus = SMBus(1)
displays = get_displays(bus, layout=layout)

# Displays need to be organised.
# Use...
#print(display_arranger(bus, displays))
# ... to see a graphic on how to arrange the displays.
switch_displays_from_chars(displays, 'F', 'C')
switch_displays_from_chars(displays, 'D', 'E')
switch_displays_from_chars(displays, 'A', 'C')
switch_displays_from_chars(displays, 'B', 'E')
switch_displays_from_chars(displays, 'B', 'C')
switch_displays_from_chars(displays, 'E', 'G')

run(file_=file_, layout=layout, \
    bus=bus, displays=displays, \
    mode='normal', \
    energy_method='accumulate', \
    force_displays=force_displays, normalise=normalise)

