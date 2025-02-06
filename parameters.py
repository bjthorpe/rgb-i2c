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
    'ROTATE_0': 0,
    'ROTATE_90': 1,
    'ROTATE_180': 2,
    'ROTATE_270': 3,
}

COLORS = {
    'red': 0x00,
    'orange': 0x12,
    'yellow': 0x18,
    'green': 0x52,
    'cyan': 0x7f,
    'blue': 0xaa,
    'purple': 0xc3,
    'pink': 0xdc,
    'white': 0xfe,
    'black': 0xff,
}

COLOR_DEFAULT = COLORS.get('black')

COLOR_GRADIENT_DEFAULT = ([25.0, 20.0, 15.0, 10.0,  5.0],  # Anything up to this value...
                          [50,   40,   30,   20,   10])    # will have the following colour.

COLOR_METHODS = ['energy']  # What should decide how the colours of the pixels change?
COLOR_METHOD_DEFAULT = 'energy'  # What should decide how the colours change?

ENERGY_TICK_RATE_DEFAULT = 5.0  # Every `GRADIENT_DELAY` seconds, the energy of a pixel should decay by how much?

WAIT_WRITE = 0.001 # Time to wait for Bus after a write statement.
WAIT_READ = 0.1 # Time to wait for Bus after a read statement
WAIT_INITIAL = 0.1 # Time to wait for Bus on startup.
WAIT_DISPLAY = 0.0001 # How long should the display thread wait before checking if any updates to the displays are needed?

DEVICE_NUM_MIN = 8 # Minimum device number sensible as in `i2cdetect -y 1`.
DEVICE_NUM_MAX = 119 # Maximum device number sensible as in `i2cdetect -y 1`

FRAME_RATE = 1.0 / 30.0 # How often is the frame manager updated?

GRADIENT_DELAY = 0.5  # How long is the default between colour changes of pixels?

