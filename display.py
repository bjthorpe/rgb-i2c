from smbus import SMBus
from time import sleep

from data import DEFAULT_I2C_ADDR, I2C_CMD_DISP_OFF, I2C_CMD_GET_DEV_ID, \
    I2C_CMD_DISP_EMOJI, I2C_CMD_DISP_NUM, I2C_CMD_DISP_CUSTOM, I2C_CMD_CONTINUE_DATA, \
    DEVICE_NUM_MIN, DEVICE_NUM_MAX, \
    COLORS, WAIT_READ, WAIT_WRITE

from utility import int_to_bytes


def create_displays(bus):
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

    def get_VID(self, bus):
        assert isinstance(bus, SMBus)
    
        bus.write_byte_data(self.addr, 0, I2C_CMD_GET_DEV_ID)
    
        result = bus.read_i2c_block_data(DEFAULT_I2C_ADDR, 0, 2)
    
        return hex(result[1]), hex(result[0])

    def set_device_address(self, bus, new_address=DEFAULT_I2C_ADDR):
        assert isinstance(bus, SMBus)
        assert isinstance(new_address, int)

        assert DEVICE_NUM_MAX >= new_address >= DEVICE_NUM_MIN, f'Device address {address} outside of sensible range.'

        bus.write_byte_data(self.addr, I2C_CMD_SET_ADDR, new_address)

    def clear_display(self, bus):
        assert isinstance(bus, SMBus)

        bus.write_byte_data(self.addr, I2C_CMD_DISP_OFF, 0)

    def display_emoji(self, bus, emoji, duration=1, forever=True):
        assert isinstance(bus, SMBus)
        assert isinstance(emoji, int)
        assert isinstance(duration, (float, int))
        assert isinstance(forever, bool)
    
        assert duration > 0.001, 'Error: duration should be at least 1 ms.'
    
        duration_bytes = int_to_bytes(int(duration * 1000)) # Duration is in ms.
    
        data = [emoji, duration_bytes[1], duration_bytes[0], forever]
    
        bus.write_i2c_block_data(self.addr, I2C_CMD_DISP_EMOJI, data)
        sleep(WAIT_WRITE)
    
    
    def display_number(self, bus, number, color='blue', duration=1, forever=True):
        assert isinstance(bus, SMBus)
        assert isinstance(number, int)
        assert isinstance(color, str)
        assert isinstance(duration, (float, int))
        assert isinstance(forever, bool)
    
        assert duration > 0.001, 'Error: duration should be at least 1 ms.'
        assert color in COLORS.keys(), f'Error: invalid colour {color} must be one of {COLORS.keys()}.'
    
        number_bytes = int_to_bytes(number)
        duration_bytes = int_to_bytes(int(duration * 1000)) # Duration is in ms.
    
        data = [number_bytes[1], number_bytes[0], 
                duration_bytes[1], duration_bytes[0],
                forever, COLORS[color]]
    
        bus.write_i2c_block_data(self.addr, I2C_CMD_DISP_NUM, data)
        sleep(WAIT_WRITE)
    
    
    def display_pixel(self, bus, x, y, color='blue', duration=1, forever=True):
        assert isinstance(bus, SMBus)
        assert isinstance(x, int)
        assert isinstance(y, int)
        assert isinstance(color, str)
        assert isinstance(duration, (float, int))
        assert isinstance(forever, bool)
    
        assert duration > 0.001, 'Error: duration should be at least 1 ms.'
        assert color in COLORS.keys(), f'Error: invalid colour {color} must be one of {COLORS.keys()}'
            
        num_frames = 1 # For now.
        
        frame = [COLORS['black']] * 64 # Start as blank frame.
        index = x + 8 * y # 2D index to integer.
        frame[index] = COLORS[color] # Colour the requested pixel.
    
        duration_bytes = int_to_bytes(int(duration * 1000)) # Duration is in ms.
        
        # Data of the frame.
        # The latter 3 zeroes are redundant data.
        data = [duration_bytes[1], duration_bytes[0], forever, num_frames, 0, 0, 0]
    
        # Now send the data.
        # Maximum of 32 bytes allowed per send, so the 71 pieces of info are split into 3 chunks of 7, 32, 32.
        bus.write_i2c_block_data(self.addr, I2C_CMD_DISP_CUSTOM, data)
        sleep(WAIT_WRITE)
        bus.write_i2c_block_data(self.addr, I2C_CMD_CONTINUE_DATA, frame[:32])
        sleep(WAIT_WRITE)
        bus.write_i2c_block_data(self.addr, I2C_CMD_CONTINUE_DATA, frame[32:])
        sleep(WAIT_WRITE)

