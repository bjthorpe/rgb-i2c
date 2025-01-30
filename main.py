from smbus import SMBus  # smbus2 package might be required
from time import sleep

from display import clear_displays, create_displays
from utility import wait_for_matrix_ready

    
bus = SMBus(1)
wait_for_matrix_ready()

displays = create_displays(bus)
clear_displays(bus, displays)

for ID, display in displays.items():
    print(f"Device ID {ID} found. Hex name {hex(display.addr)}.")
    display.display_number(bus, number=ID)
sleep(1)
clear_displays(bus, displays)

display = displays[0]

display.display_number(bus, 23)
sleep(0.5)

display.display_emoji(bus, 10)
sleep(0.5)

for i in range(8):
    sleep(0.1)
    display.display_pixel(bus, x=i, y=0)

