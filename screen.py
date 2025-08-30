# Datasheet: https://cdn-shop.adafruit.com/datasheets/SSD1306.pdf
# Ejmplo base: https://github.com/sxkod/ssd1306/blob/main/xoled.py#L77

#!/usr/bin/env python

from smbus import SMBus

I2C_BUS = 1

# i2cdetect -y 1
#      0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
# 00:                         -- -- -- -- -- -- -- -- 
# 10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
# 20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
# 30: -- -- -- -- -- -- -- -- -- -- -- -- 3c -- -- -- 
# 40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
# 50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
# 60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
# 70: -- -- -- -- -- -- -- --
I2C_ADDRESS = 0x3C

# SDA is for input and output

# Pages = 8, 1 page vertically is 1 byte, 
# Column is 8 bits (1 byte)
# Pages x 1 byte = 8 x 8 = 64 bits (rows)
# Page contains 128 bits as columns, 16 bytes
# Most significant bit is bottom, Les significant bits is top
WIDTH = 128 # columns
HEIGHT = 64 # rows 

# Control byte
# |----------------------------------|
# | Co | D/C | 0 | 0 | 0 | 0 | 0 | 0 |
# |----------------------------------|
# 
# After the transmission of the slave address, either the control byte or the data byte may be sent across the SDA. A control byte mainly consists of 
# Co and D/C# bits following by six “0” ‘s.
#   a. If the Co bit is set as logic “0”, the transmission of the following information will contain data bytes only.
#   b. The D/C# bit determines the next data byte is acted as a command or a data. If the D/C# bit is set to logic “0”, 
#   it defines the following data byte as a command. If the D/C# bit is set to logic “1”, it defines the following data byte as a 
#   data which will be stored at the GDDRAM. The GDDRAM column address pointer will be increased by one automatically after each data write.
COMMAND_CONTROL_BYTE    = 0x00    # 0000_0000
DATA_CONTROL_BYTE       = 0x40    # 0100_0000

COMMAND_DISPLAY_OFF     = 0xAE
COMMAND_DISPLAY_ON      = 0xAF

START_PAGE_INDEX        = 0xB0
ADDRESS_LOWER_NIBBLE    = 0x00
ADDRESS_HIGER_NIBBLE    = 0x10
ADDRESS_MASK            = 0x0F

bus = SMBus(I2C_BUS)

def send_command(command):
    bus.write_byte_data(I2C_ADDRESS, COMMAND_CONTROL_BYTE, command)

def send_data(data):
    bus.write_byte_data(I2C_ADDRESS, DATA_CONTROL_BYTE, data)

# we have 64 rows are 8 pages
# 128 colums are 16 bytes
def draw_pixel(row, column):
    page = HEIGHT // 8
    set_matrix_address(page, column)
    send_data(1)

def set_matrix_address(page, column):
#     In normal display data RAM read or write and page addressing mode, the following steps are required to define the starting RAM access pointer location:
#       • Set the page start address of the target display location by command B0h to B7h.
#       • Set the lower start column address of pointer by command 00h~0Fh.
#       • Set the upper start column address of pointer by command 10h~1Fh.
    send_command( START_PAGE_INDEX | (page & ADDRESS_MASK) )
    send_command( ADDRESS_LOWER_NIBBLE | (column & ADDRESS_MASK) )
    send_command( ADDRESS_HIGER_NIBBLE | ((column >> 4) & ADDRESS_MASK) )

def initialize():
    # Software Initialization Flow Chart
    init_buffer = [
        0xA8, 0x3F, # Mux ratio
        0xD3, 0x00, # Display offset
        0x40,       # Display start line
        0xA0,       # Segment re-map
        0xC,        # COM output scan direction
        0xDA, 0x02, # COM pins configuration
        0x81, 0x7F, # Contrast control
        0xA4,       # Entire display on
        0xA6,       # Normal display
        0xD5, 0x80, # OSC frecuency
        0x8D, 0x14, # charger pump regulator
        0xAF        # Display on  
    ]

    for command in init_buffer:
        send_command(command)

    row = 3
    column = 1
    index = 0   
    x = range(20)
    for n in x:
        draw_pixel(row, column + index )
        index += 1

    column = 0
    row = 5
    index = 0
    for n in x:
        draw_pixel(row, column + index )
        index += 1
    

initialize()
