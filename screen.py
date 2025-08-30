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

COMMAND_DISPLAY_OFF         = 0xAE
COMMAND_DISPLAY_ON          = 0xAF
COMMAND_DISPLAY_START_LINE  = 0x40
COMMAND_MEMORY_MODE         = 0x20
COMMAND_NORMAL_DISPLAY      = 0xA6

START_PAGE_INDEX            = 0xB0
ADDRESS_LOWER_NIBBLE        = 0x00
ADDRESS_HIGHER_NIBBLE       = 0x10
ADDRESS_MASK                = 0x0F

bus = SMBus(I2C_BUS)

def send_command(command):
    bus.write_byte_data(I2C_ADDRESS, COMMAND_CONTROL_BYTE, command)

def send_data(data):
    bus.write_byte_data(I2C_ADDRESS, DATA_CONTROL_BYTE, data)

# we have 64 rows are 8 pages
# 128 colums are 16 bytes
def draw_pixel(row, column):
    page = row // 8 # -> getting page
    bit = row % 8
    set_matrix_address(page, column)
    send_data(1 << bit)

def set_matrix_address(page, column):
#     In normal display data RAM read or write and page addressing mode, the following steps are required to define the starting RAM access pointer location:
#       • Set the page start address of the target display location by command B0h to B7h.
#       • Set the lower start column address of pointer by command 00h~0Fh.
#       • Set the upper start column address of pointer by command 10h~1Fh.
    send_command( START_PAGE_INDEX | (page & ADDRESS_MASK) )
    send_command( ADDRESS_LOWER_NIBBLE | (column & ADDRESS_MASK) )
    send_command( ADDRESS_HIGHER_NIBBLE | ((column >> 4) & ADDRESS_MASK) )

def clear_screen():
    for page in range(HEIGHT // 8):    
        set_matrix_address(page, 0)
        for _ in range(WIDTH):
            send_data(0x00)

def initialize():
    # Software Initialization Flow Chart
    init_buffer = [
        COMMAND_DISPLAY_OFF,
        0xD5, 0x80, # Clock
        0xA8, 0x3F, # Mux ratio
        0xD3, 0x00, # Display offset
        COMMAND_DISPLAY_START_LINE,
        COMMAND_MEMORY_MODE, 0x00,
        0xA1,       # Segment re-map
        0xC8,       # COM output scan direction
        0xDA, 0x12, # COM pins configuration    # no se porque el segundo parametro y su valor
        0x81, 0x7F, # Contrast control
        0xD9, 0xF1,        # Pre-charge
        0xDB, 0x40,        # VCOMH deselect
        0xA4,       # Entire display on
        COMMAND_NORMAL_DISPLAY,
        0x8D, 0x14, # charger pump regulator
        COMMAND_DISPLAY_ON
    ]

    for command in init_buffer:
        send_command(command)

    clear_screen()
    row = 3
    column = 1
    index = 0   
    x = range(20)

    #send_command(COMMAND_DISPLAY_OFF)

    # son 64 filas, quiero la 19
    row = 19
    # row // 8 = 2, pagina 2
    column = 1 # 0000_0011
    # 1 pixel es 1 bit, solo quiero pintar un bit no la columna completa!
    #
    # 0 LSB 1px
    # 0     1px
    # 1     1px
    # 1     1px -> este quiero pintar
    # 0     1px
    # 0     1px
    # 0     1px
    # 0 MSB 1px
    
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
