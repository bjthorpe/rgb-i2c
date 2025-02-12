from copy import deepcopy
from smbus import SMBus
from time import sleep

from parameters import DEFAULT_I2C_ADDR, I2C_CMD_DISP_OFF, I2C_CMD_GET_DEV_ID, \
    I2C_CMD_DISP_EMOJI, I2C_CMD_DISP_NUM, I2C_CMD_DISP_CUSTOM, I2C_CMD_CONTINUE_DATA, \
    DEVICE_NUM_MIN, DEVICE_NUM_MAX, \
    COLORS, COLOR_DEFAULT, WAIT_READ, WAIT_WRITE

from utility import int_to_bytes


def get_displays(bus):
    assert isinstance(bus, SMBus)

    displays = {}

    current_ID = 0

    for device in range(DEVICE_NUM_MIN, DEVICE_NUM_MAX+1):
        found = False

        try:
            bus.read_byte(device)
            sleep(WAIT_READ)
            found = True
        except OSError:
            pass

        if found:
            displays[current_ID] = Display(ID=current_ID, address=device)
            current_ID += 1

    return displays


def clear_displays(bus, displays):
    assert isinstance(bus, SMBus)

    for display in displays.values():
        display.clear_display(bus)


class Display:
    def __init__(self, size=8, side=0, X=0, Y=0,
                 ID=0, address=DEFAULT_I2C_ADDR):
        assert isinstance(size, int)
        assert isinstance(side, int)
        assert isinstance(X, int)
        assert isinstance(Y, int)
        assert isinstance(ID, int)
        assert isinstance(address, int)

        assert size == 8, 'HARD CODED SIZE OF 8 FOR NOW.'  # TODO: displays are currently hard coded to a size of 8x8.
        assert size > 0, 'Size of display must be > 0.'
        assert side in (0, 1), 'Only two possible sides at the moment, 0 and 1.'
        assert X >= 0, 'X location of display should be >= 0.'
        assert Y >= 0, 'Y location of display should be >= 0.'
        assert ID >= 0, 'Device ID should be >= 0.'
        assert DEVICE_NUM_MAX >= address >= DEVICE_NUM_MIN, f'Device address {address} outside of sensible range.'

        self.size = size
        self.side = side
        self.X = X
        self.Y = Y
        self.ID = ID
        self.addr = address

        self.frame_A = [COLOR_DEFAULT for _ in range(self.size * self.size)]  # [Pixel() for _ in range(self.size * self.size)]
        self.frame_B = deepcopy(self.frame_A)

        self.display_frame_A = True  # Do we use the A or B frame for displaying?
        self.change_detected = False  # Has a change been detected on this display from the data manager?
        self.needs_updating = False  # So the display thread knows whether to bother updating this display or not.

    def get_VID(self, bus):
        assert isinstance(bus, SMBus)
    
        bus.write_byte_data(self.addr, 0, I2C_CMD_GET_DEV_ID)
    
        result = bus.read_i2c_block_data(self.addr, 0, 2)
    
        return hex(result[1]), hex(result[0])

    def set_device_address(self, bus, new_address=DEFAULT_I2C_ADDR):
        assert isinstance(bus, SMBus)
        assert isinstance(new_address, int)

        assert DEVICE_NUM_MAX >= new_address >= DEVICE_NUM_MIN, f'Device address {address} outside of sensible range.'

        bus.write_byte_data(self.addr, I2C_CMD_SET_ADDR, new_address)

    def clear_display(self, bus):
        assert isinstance(bus, SMBus)

        bus.write_byte_data(self.addr, I2C_CMD_DISP_OFF, 0)

    def display_emoji(self, bus, emoji, duration=1, forever=False):
        assert isinstance(bus, SMBus)
        assert isinstance(emoji, int)
        assert isinstance(duration, (float, int))
        assert isinstance(forever, bool)
    
        assert duration > 0.001, 'Error: duration should be at least 1 ms.'
    
        duration_bytes = int_to_bytes(int(duration * 1000)) # Duration is in ms.
    
        data = [emoji, duration_bytes[1], duration_bytes[0], forever]
    
        bus.write_i2c_block_data(self.addr, I2C_CMD_DISP_EMOJI, data)
        sleep(WAIT_WRITE)
    
    
    def display_number(self, bus, number, color='blue', duration=1, forever=False):
        assert isinstance(bus, SMBus)
        assert isinstance(number, int)
        assert isinstance(color, (str, int))
        assert isinstance(duration, (float, int))
        assert isinstance(forever, bool)
    
        assert duration > 0.001, 'Error: duration should be at least 1 ms.'

        if isinstance(color, str):
            assert color in COLORS.keys(), f'Error: invalid colour {color} must be one of {COLORS.keys()}.'
            color = COLORS[color]
        elif isinstance(color, int):
            assert 255 >= color >= 0, 'Colour number should be between 0 and 255.'

        number_bytes = int_to_bytes(number)
        duration_bytes = int_to_bytes(int(duration * 1000)) # Duration is in ms.
    
        data = [number_bytes[1], number_bytes[0], duration_bytes[1], duration_bytes[0], forever, color]
    
        bus.write_i2c_block_data(self.addr, I2C_CMD_DISP_NUM, data)
        sleep(WAIT_WRITE)
    
    
    def display_pixel(self, bus, x, y, color='blue', duration=1, forever=False):
        assert isinstance(bus, SMBus)
        assert isinstance(x, int)
        assert isinstance(y, int)
        assert isinstance(color, (str, int))
        assert isinstance(duration, (float, int))
        assert isinstance(forever, bool)

        assert self.size > x >= 0, 'Error: x value supplied is outside of frame range.'
        assert self.size > y >= 0, 'Error: y value supplied is outside of frame range.'
        assert duration > 0.001, 'Error: duration should be at least 1 ms.'

        if isinstance(color, str):
            assert color in COLORS.keys(), f'Error: invalid colour {color} must be one of {COLORS.keys()}'
            color = COLORS[color]
        elif isinstance(color, int):
            assert 255 >= color >= 0, 'Colour number should be between 0 and 255.'

        num_frames = 1 # For now.
        
        frame = [COLORS['black']] * self.size * self.size  # Start as blank frame.
        index = x + self.size * y  # 2D index to integer.
        frame[index] = color  # Colour the requested pixel.
    
        duration_bytes = int_to_bytes(int(duration * 1000))  # Duration is in ms.
        
        # Data of the frame.
        # The latter 3 zeroes are redundant data.
        data = [duration_bytes[1], duration_bytes[0], forever, num_frames, 0, 0, 0]
    
        # Now send the data.
        # Maximum of 32 bytes allowed per send, so the 71 pieces of info are split into 3 chunks of 7, 32, 32.
        bus.write_i2c_block_data(self.addr, I2C_CMD_DISP_CUSTOM, data)
        sleep(WAIT_WRITE)
        bus.write_i2c_block_data(self.addr, I2C_CMD_CONTINUE_DATA, frame[:32])  # TODO: remove assumption that we have 8x8.
        sleep(WAIT_WRITE)
        bus.write_i2c_block_data(self.addr, I2C_CMD_CONTINUE_DATA, frame[32:])  # TODO: remove assumption that we have 8x8.
        sleep(WAIT_WRITE)

    def display_current_frame(self, bus, duration=1, forever=False):
        assert isinstance(bus, SMBus)
        assert isinstance(duration, (float, int))
        assert isinstance(forever, bool)
    
        assert duration > 0.001, 'Error: duration should be at least 1 ms.'
        
        duration_bytes = int_to_bytes(int(duration * 1000)) # Duration is in ms.
        
        # Data of the frame.
        # The latter 3 zeroes are redundant data.
        data = [duration_bytes[1], duration_bytes[0], forever, 1, 0, 0, 0]  # The 1 is the number of frames.

        frame = self.frame_A if self.display_frame_A else self.frame_B

        # Now send the data.
        # Maximum of 32 bytes allowed per send, so the 71 pieces of info are split into 3 chunks of 7, 32, 32.
        bus.write_i2c_block_data(self.addr, I2C_CMD_DISP_CUSTOM, data)
        sleep(WAIT_WRITE)
        bus.write_i2c_block_data(self.addr, I2C_CMD_CONTINUE_DATA, frame[:32])  # TODO: remove assumption that we have 8x8.
        sleep(WAIT_WRITE)
        bus.write_i2c_block_data(self.addr, I2C_CMD_CONTINUE_DATA, frame[32:])  # TODO: remove assumption that we have 8x8.
        sleep(WAIT_WRITE)

    def set_buffer_pixel(self, x, y, color):
        ''' Updates whichever frame is not in use for displaying with a provided pixel co-ordinate and colour. '''

        assert isinstance(x, int)
        assert isinstance(y, int)
        assert isinstance(color, int)

        assert self.size > x >= 0, 'Error: x value supplied is outside of frame range.'
        assert self.size > y >= 0, 'Error: y value supplied is outside of frame range.'
        assert 255 >= color >= 0, 'Colour number should be between 0 and 255.'

        if self.display_frame_A:                                         
            self.frame_B[x + self.size * y] = color
        else:
            self.frame_A[x + self.size * y] = color

    def copy_buffer(self):
        if self.display_frame_A:
            self.frame_B = deepcopy(self.frame_A)
        else:
            self.frame_A = deepcopy(self.frame_B)

    def switch_buffer(self):
        self.display_frame_A = not self.display_frame_A

