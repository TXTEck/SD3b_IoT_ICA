from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
import RPi.GPIO as GPIO
import time

# GPIO Pin Configuration
PIR_pin = 4           # PIR sensor signal pin
LED1_pin = 17         # First LED pin
LED2_pin = 27         # Second LED pin
CLK = 23              # TM1637 clock pin
DIO = 24              # TM1637 data pin

# PubNub Configuration
pnconfig = PNConfiguration()
pnconfig.subscribe_key = "sub-c-a601ad79-0e0f-450f-a941-026ebac0a79e" 
pnconfig.publish_key = "pub-c-48f6b9c1-0ffc-435b-a55e-d52776778f65"   
pnconfig.uuid = "teck-pi"

pubnub = PubNub(pnconfig)

# GPIO Setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_pin, GPIO.IN)  # PIR sensor input
GPIO.setup(LED1_pin, GPIO.OUT)  # First LED output
GPIO.setup(LED2_pin, GPIO.OUT)  # Second LED output
GPIO.output(LED1_pin, False)  # Ensure LED1 is initially off
GPIO.output(LED2_pin, False)  # Ensure LED2 is initially off
GPIO.setup(CLK, GPIO.OUT)  # TM1637 CLK
GPIO.setup(DIO, GPIO.OUT)  # TM1637 DIO

# TM1637 Commands
CMD_DATA = 0x40  # Command for data setting
CMD_DISPLAY = 0x88  # Command for display control (brightness)
CMD_ADDRESS = 0xC0  # Command for setting display address

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
    digits = [int(d) for d in str(num).zfill(4)]  
    start()
    write_byte(CMD_DATA)  
    stop()
    start()
    write_byte(CMD_ADDRESS)  
    for digit in digits:
        write_byte(SEGMENTS[digit])
    stop()
    start()
    write_byte(CMD_DISPLAY | 0x07)  
    stop()

def publish_message(count):
    if count >= 20:
        led_status = 2  # Both LEDs on
    elif count >= 10:
        led_status = 1  # Only LED1 on
    else:
        led_status = 0  # No LEDs on

    message = {
        "motion_count": count,
        "led_status": led_status  # Number of LEDs currently lit
    }
    print("Publishing message:", message) 
    pubnub.publish().channel("motion_channel").message(message).pn_async(print_status)

def print_status(envelope, status):
    if not status.is_error():
        print("Message sent successfully!")
    else:
        print("Error sending message:", status)

# Motion detection counter
trigger_count = 0

try:
    print("Waiting for motion...")
    while True:
        if GPIO.input(PIR_pin):  
            print("Motion detected!")
            trigger_count += 1  
            display_number(trigger_count)  
            
            # Turn on LEDs based on the counter value
            GPIO.output(LED1_pin, trigger_count >= 10)  
            GPIO.output(LED2_pin, trigger_count >= 20)  
            
            # Publish to PubNub
            publish_message(trigger_count)
            
            time.sleep(1)  

except KeyboardInterrupt:
    display_number(0)
    print("Exiting program...")
    stop()
    GPIO.cleanup()
