import RPi.GPIO as GPIO
import time

# GPIO Pin Configuration
PIR_pin = 4           
LED_pin = 17         
CLK = 23             
DIO = 24              

# GPIO Setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_pin, GPIO.IN)  # PIR sensor input
GPIO.setup(LED_pin, GPIO.OUT)  # LED output
GPIO.output(LED_pin, False)  # Ensure LED is initially off
GPIO.setup(CLK, GPIO.OUT)  # TM1637 CLK
GPIO.setup(DIO, GPIO.OUT)  # TM1637 DIO

# TM1637 Commands
CMD_DATA = 0x40  # Command for data setting
CMD_DISPLAY = 0x88  # Command for display control (brightness)
CMD_ADDRESS = 0xC0  # Command for setting display address

# Number-to-Segment Mapping (0-9)
SEGMENTS = {
    0: 0x3F, 1: 0x06, 2: 0x5B, 3: 0x4F,
    4: 0x66, 5: 0x6D, 6: 0x7D, 7: 0x07,
    8: 0x7F, 9: 0x6F
}

def start():
    GPIO.output(CLK, True)
    GPIO.output(DIO, True)
    time.sleep(0.001)
    GPIO.output(DIO, False)
    time.sleep(0.001)
    GPIO.output(CLK, False)

def stop():
    GPIO.output(CLK, False)
    GPIO.output(DIO, False)
    time.sleep(0.001)
    GPIO.output(CLK, True)
    time.sleep(0.001)
    GPIO.output(DIO, True)

def write_byte(byte):
    for i in range(8):
        GPIO.output(CLK, False)
        GPIO.output(DIO, (byte >> i) & 0x01)
        time.sleep(0.001)
        GPIO.output(CLK, True)
        time.sleep(0.001)
    # Wait for ACK
    GPIO.output(CLK, False)
    GPIO.setup(DIO, GPIO.IN)
    time.sleep(0.001)
    ack = GPIO.input(DIO)
    GPIO.setup(DIO, GPIO.OUT)
    if ack == 0:
        GPIO.output(DIO, False)
    time.sleep(0.001)
    GPIO.output(CLK, True)
    time.sleep(0.001)

def display_number(num):
    digits = [int(d) for d in str(num).zfill(4)]  # Ensure 4 digits
    start()
    write_byte(CMD_DATA)  # Data setting command
    stop()
    start()
    write_byte(CMD_ADDRESS)  # Start address
    for digit in digits:
        write_byte(SEGMENTS[digit])  # Write each digit
    stop()
    start()
    write_byte(CMD_DISPLAY | 0x07)  # Display control (max brightness)
    stop()


# Motion detection counter
trigger_count = 0

try:
    print("Waiting for motion...")
    while True:
        if GPIO.input(PIR_pin):  # Motion detected
            print("Motion detected!")
            trigger_count += 1  # Increment count
            display_number(trigger_count)  # Show count on display
            
            # Turn on LED only if the count reaches or exceeds 10
            if trigger_count >= 10:
                GPIO.output(LED_pin, True)  # Turn on LED
            else:
                GPIO.output(LED_pin, False)  # Turn off LED if below 10
            
            time.sleep(1)  

except KeyboardInterrupt:
    display_number(0)
    print("Exiting program...")
    stop()
    GPIO.cleanup()
