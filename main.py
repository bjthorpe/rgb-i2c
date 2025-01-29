import smbus  # smbus2 package might be required
import time
import numpy as np


#The device i2c address in default
DEFAULT_I2C_ADDR = 0x65

# Vender ID and Product ID of the device
VID = 0x2886
PID = 0x8005

# Comands to set mode
I2C_CMD_GET_DEV_ID = 0x00 # This command gets device ID information
I2C_CMD_DISP_BAR = 0x01 # This command displays LED bar
I2C_CMD_DISP_EMOJI = 0x02 # This command displays emoji
I2C_CMD_DISP_NUM = 0x03 # This command displays number
I2C_CMD_DISP_STR = 0x04 # This command displays string
I2C_CMD_DISP_CUSTOM = 0x05 # This command displays user-defined pictures
I2C_CMD_DISP_OFF = 0x06 # This command clears the display
I2C_CMD_CONTINUE_DATA = 0x81

I2C_CMD_DISP_COLOR_BAR = 0x09 # This command displays colorful led bar
I2C_CMD_DISP_COLOR_WAVE = 0x0a # This command displays built-in wave animation
I2C_CMD_DISP_COLOR_CLOCKWISE = 0x0b # This command displays built-in clockwise animation
I2C_CMD_DISP_COLOR_ANIMATION = 0x0c # This command displays other built-in animation
I2C_CMD_DISP_COLOR_BLOCK = 0x0d # This command displays an user-defined color

I2C_CMD_LED_ON = 0xb0 # This command turns on the indicator LED flash mode
I2C_CMD_LED_OFF = 0xb1 # This command turns off the indicator LED flash mode
I2C_CMD_AUTO_SLEEP_ON = 0xb2 # This command enable device auto sleep mode
I2C_CMD_AUTO_SLEEP_OFF = 0xb3 # This command disable device auto sleep mode (default mode)

I2C_CMD_DISP_ROTATE = 0xb4 # This command setting the display orientation
I2C_CMD_DISP_OFFSET = 0xb5 # This command setting the display offset

I2C_CMD_SET_ADDR = 0xc0 # This command sets device i2c address
I2C_CMD_RST_ADDR = 0xc1 # This command resets device i2c address

orientation_type = {
    "ROTATE_0": 0,
    "ROTATE_90": 1,
    "ROTATE_180": 2,
    "ROTATE_270": 3,
}

COLORS={
    "red": 0x00,
    "orange": 0x12,
    "yellow": 0x18,
    "green": 0x52,
    "cyan": 0x7f,
    "blue": 0xaa,
    "purple": 0xc3,
    "pink": 0xdc,
    "white": 0xfe,
    "black": 0xff,
}

def wait_for_matrix_ready():
    time.sleep(0.1)
    print("done waiting")

def get_VID():
    Bus.write_byte_data(DEFAULT_I2C_ADDR, 0, I2C_CMD_GET_DEV_ID)
    data = Bus.read_i2c_block_data(DEFAULT_I2C_ADDR,0,2)
    print(hex(data[1]))
    print(hex(data[0]))

def clear_display(device_address=DEFAULT_I2C_ADDR):
    Bus.write_byte_data(device_address, I2C_CMD_DISP_OFF, 0)
    
def clear_displays():
    devices = detect_devices()
    
    for device in devices.values():
        Bus.write_byte_data(device, I2C_CMD_DISP_OFF, 0)
    
def set_addr(addr):
    Bus.write_byte_data(DEFAULT_I2C_ADDR,I2C_CMD_SET_ADDR, addr)

def detect_devices(show_numbers=False):
    devices = {}
    
    current_ID = 0
    
    for device in range(8,120):
        found = False

        try:
            Bus.read_byte(device)
            time.sleep(0.1) # DON'T TOUCH
            found = True
        except OSError:
            pass
        
        if found:
            devices[current_ID] = device
            current_ID += 1
            
    if show_numbers:
        for ID, device in devices.items():
            print(f"Device ID {ID} found. Hex name {hex(device)}.")
            
            clear_display(device_address=device)
            display_number(ID, device_address=device, forever=True)
            
    return devices

def int_to_bytes(num):
    if num > 65535:
        print(f'sorry {num} is to big should be beteween 0 and 65535')
        exit    
    elif num < 0:
        print(f'sorry {num} is to small should be beteween 0 and 65535')
        exit

    return [int(i) for i in num.to_bytes(2, byteorder='big', signed=True)]

def display_emoji(emoji, duration=5, forever=True):
    duration_bytes = int_to_bytes(duration*1000) #duration is in ms
    data = [0,0,0,0]
    data[0] = emoji
    data[1] = duration_bytes[1]
    data[2] = duration_bytes[0]
    data[3] = False
    #i2cSendBytes(currentDeviceAddress, data, 5);
    Bus.write_i2c_block_data(DEFAULT_I2C_ADDR, I2C_CMD_DISP_EMOJI, data)
    time.sleep(0.001)

def display_number(number, device_address=DEFAULT_I2C_ADDR, colour="blue", duration=5, forever=True):
    if colour not in COLORS.keys():
        print(f'Error: invalid colour {colour} must be one of {COLORS.keys()}')
        exit
    hex_number_bytes = int_to_bytes(number)
    duration_bytes = int_to_bytes(duration*1000) #duration is in ms
    data = [0,0,0,0,0,0]
    data[0] = hex_number_bytes[1]
    data[1] = hex_number_bytes[0]
    data[2] = duration_bytes[1]
    data[3] = duration_bytes[0]
    data[4] = forever
    data[5] = COLORS[colour]
    #i2cSendBytes(currentDeviceAddress, data, 5);
    Bus.write_i2c_block_data(device_address, I2C_CMD_DISP_NUM, data)
    time.sleep(0.001)


def display_pixel(x, y, device_address=DEFAULT_I2C_ADDR, colour="blue", duration=1, forever=True):
    if colour not in COLORS.keys():
        print(f'Error: invalid colour {colour} must be one of {COLORS.keys()}')
        exit
        
    num_frames = 1 # For now.
    
    frame = [COLORS["black"]] * 64 # Start as blank frame.
    index = x + 8 * y # 2D index to integer.
    frame[index] = COLORS[colour] # Colour the requested pixel.

    hex_duration = int_to_bytes(duration*1000) #duration is in ms
    
    # Data of the frame.
    # Indices 0, 1, 2, 4, 5, 6 are not needed in the frame data.
    data = [hex_duration[1], hex_duration[0], forever, num_frames, 0, 0, 0]

    # Now send the data.
    # Maximum of 32 bytes allowed per send, so the 71 pieces of info are split into 3 chunks.
    Bus.write_i2c_block_data(device_address, I2C_CMD_DISP_CUSTOM, data)
    time.sleep(0.001)
    Bus.write_i2c_block_data(device_address, I2C_CMD_CONTINUE_DATA, frame[:32])
    time.sleep(0.001)
    Bus.write_i2c_block_data(device_address, I2C_CMD_CONTINUE_DATA, frame[32:])
    time.sleep(0.001)

    
Bus = smbus.SMBus(1)
wait_for_matrix_ready()
clear_displays()
devices = detect_devices(show_numbers=True)
time.sleep(2)
clear_displays()
#display_number(23, device_address=0x33, duration=10, colour="green")
#display_emoji(4)
for i in range(8):
    time.sleep(0.1)
    display_pixel(i, 0, device_address=devices[0], duration=2, forever=False)
