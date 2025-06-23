from display import display_rainbow_2, get_displays, switch_displays, switch_displays_from_chars, display_arranger, set_global_orientation,display_rainbow
from manager import run
from smbus import SMBus
from time import sleep

#file_ = 'Imaging_data/QECos2DeltaPhi_0_180_true.dat'  # Data file.
#file_ = 'Imaging_data/QECos2DeltaPhi_72_92_true.dat'  # Data file.
file_ = 'Imaging_data/test.dat'  # Data file.
#file_ = 'Imaging_data/tiny.dat'  # Data file.
layout = (4, 4)
#layout = 4
#layout = (1)

bus = SMBus(1)
displays = get_displays(bus, layout=layout, mirror=True)
print("num displays found", len(displays))
#print(len(displays))
#for display in displays:
#    print(display.addr)
set_global_orientation(bus,1)
#display_rainbow(bus,displays)

# Displays need to be organised.
# Use...
#print(display_arranger(bus, displays))#;exit()
# ... to see a graphic on how to arrange the displays.
#switch_displays_from_chars(displays, 'D', 'C')
#switch_displays_from_chars(displays, 'J', 'G')
#switch_displays_from_chars(displays, 'E', 'G')
#switch_displays_from_chars(displays, 'J', 'F')

run(file_=file_, layout=layout, \
    bus=bus, displays=displays, \
    mode='normal', \
    energy_method='tick', \
    mirror=True)

#run(file_=file_, layout=layout, \
#    bus=bus, displays=displays, \
#    mode='normal', \
#    energy_method='accumulate')

