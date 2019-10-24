# Adafruit Circuit Playground Express

import board
import digitalio
import math
import neopixel
import time
import touchio

# Proportionally scale a number that is in the range of x0 to x1 to be
# within the range of y0 to y1.
def scale(x, x0, x1, y0, y1):
    return int(y0+(x-x0)*((y1-y0)/(x1-x0)))

def scale_color(color, brightness):
    red = scale(color[0], 0, 255, 0, brightness)
    green = scale(color[1], 0, 255, 0, brightness)
    blue = scale(color[2], 0, 255, 0, brightness)

    return (red, green, blue)

def convert_K_to_RGB(color_temperature):
    """
    Converts from K to RGB, algorithm courtesy of 
    http://www.tannerhelland.com/4435/convert-temperature-rgb-algorithm-code/
    """
    #range check
    if color_temperature < 1000: 
        color_temperature = 1000
    elif color_temperature > 40000:
        color_temperature = 40000
    
    tmp_internal = color_temperature / 100.0
    
    # red 
    if tmp_internal <= 66:
        red = 255
    else:
        tmp_red = 329.698727446 * math.pow(tmp_internal - 60, -0.1332047592)
        if tmp_red < 0:
            red = 0
        elif tmp_red > 255:
            red = 255
        else:
            red = tmp_red
    
    # green
    if tmp_internal <=66:
        tmp_green = 99.4708025861 * math.log(tmp_internal) - 161.1195681661
        if tmp_green < 0:
            green = 0
        elif tmp_green > 255:
            green = 255
        else:
            green = tmp_green
    else:
        tmp_green = 288.1221695283 * math.pow(tmp_internal - 60, -0.0755148492)
        if tmp_green < 0:
            green = 0
        elif tmp_green > 255:
            green = 255
        else:
            green = tmp_green
    
    # blue
    if tmp_internal >=66:
        blue = 255
    elif tmp_internal <= 19:
        blue = 0
    else:
        tmp_blue = 138.5177312231 * math.log(tmp_internal - 10) - 305.0447927307
        if tmp_blue < 0:
            blue = 0
        elif tmp_blue > 255:
            blue = 255
        else:
            blue = tmp_blue
    
    return red, green, blue

red_led = digitalio.DigitalInOut(board.D13)
red_led.switch_to_output(value=False)

start = time.monotonic()
while time.monotonic() - start <= 5.0:
    red_led.value = True
    time.sleep(0.5)
    red_led.value = False
    time.sleep(0.5)

sensor = dict()
sensor['warmer'] = touchio.TouchIn(board.A1)
sensor['cooler'] = touchio.TouchIn(board.A2)
sensor['brighter'] = touchio.TouchIn(board.A3)
sensor['dimmer'] = touchio.TouchIn(board.A4)

temperature = 4500
brightness = 127
color = scale_color(convert_K_to_RGB(temperature), brightness)

pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=0.7, auto_write=False)
pixels.fill(color)
pixels.show()

while True:
    oldcolor = color    
    for pad in sensor.keys():
        if sensor[pad].value:
            if pad == 'warmer':
                temperature = temperature + 10
                if temperature > 40000:
                    temperature = 40000
            elif pad == 'cooler':
                temperature = temperature - 10
                if temperature < 1000:
                    temperature = 1000
            elif pad == 'brighter':
                brightness = brightness + 1
                if brightness > 255:
                    brightness = 255
            elif pad == 'dimmer':
                brightness = brightness - 1
                if brightness < 0:
                    brightness = 0

    color = scale_color(convert_K_to_RGB(temperature), brightness)
    if color != oldcolor:
        pixels.fill(color)
        pixels.show()
