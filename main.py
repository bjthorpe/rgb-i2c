from manager import run


# Temporary data file for testing.
temp_file = 'test_data/2.dat'  # Data file.
layout = (4,)  # 4 displays for now.
force_displays = False  # If we request more displays than addresses found, should we reuse displays anyway?
normalise = True  # Should we re-normalise the times of the data to have on avg. 100 data points per 30 sec?

run(file_=temp_file, force_displays=force_displays, normalise=normalise)





from display import get_displays, switch_displays, display_arranger
from smbus import SMBus
from time import sleep

bus = SMBus(1)
displays = get_displays(bus)
d1 = displays[1]
d2 = displays[2]
switch_displays(d1, d2)
print(displays)

display_arranger(bus, displays)

