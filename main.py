from display import get_displays, switch_displays, switch_displays_from_chars, display_arranger
from manager import run
from smbus import SMBus


file_ = 'test_data/8.dat'  # Data file.
layout = (4, 4)
force_displays = False  # If we request more displays than addresses found, should we reuse displays anyway?

bus = SMBus(1)
displays = get_displays(bus, layout=layout)

# Displays need to be organised.
# Use...
#print(display_arranger(bus, displays));exit()
# ... to see a graphic on how to arrange the displays.
switch_displays_from_chars(displays, 'D', 'C')
switch_displays_from_chars(displays, 'J', 'G')

run(file_=file_, layout=layout, \
    bus=bus, displays=displays, \
    mode='normal', \
    energy_method='accumulate', \
    force_displays=force_displays)

