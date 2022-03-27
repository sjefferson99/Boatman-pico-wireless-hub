# Pico will need to be flashed with Pimoroni micropython for display support
# https://github.com/pimoroni/pimoroni-pico

# Version 0.3.0

from usys import version
from utime import sleep_ms
from machine import Pin, I2C
from pico_lights import pico_light_controller
from debug import debugger
import _thread
import time

debugEnable = True #Enables printing debug messages and debug slowdown behaviour
debugVerbosity = 0 #0=basic debug messages, 1=most debug messages, 2=all debug messages. >0 adds 1 second sleep in program loop

debug = debugger(debugVerbosity, debugEnable)

try:
    import ppwhttp
except ImportError:
    raise RuntimeError("Cannot find ppwhttp. Have you copied ppwhttp.py to your Pico?")

r = 0
g = 0
b = 0

################
# Board config #
################
#Config I2C
sda1 = Pin(14)
scl1 = Pin(15)
i2c1_freq = 100000

# Init I2C
debug.print("Init I2C")
i2c1 = I2C(1, sda=sda1, scl=scl1, freq=i2c1_freq)

################
# Pico modules #
################
#Enable pico light controller module
pico_lights_enable = True
pico_lights_address = 0x41

#Scan i2C bus for devices
debug.print('i2c1 devices found at')
devices = i2c1.scan()
if devices:
    for i in devices:
        debug.print(str(i))

#Init light controller module
if pico_lights_enable:
    debug.print("Pico light module enabled")
    lights = pico_light_controller(i2c1, pico_lights_address)
    debug.print(str(lights.I2C_address))
    
    if lights.check_bus():
        debug.print("Pico lights controller found on bus")
        
        debug.print("Lights local library version: {}".format(lights.version))
        lights_module_version = lights.get_version()
        debug.print("Lights module version: {}".format(lights_module_version))
    
        if lights_module_version != lights.version:
            debug.print("Lights module version does not equal hub lights module version, disabling lights module, please upgrade hub and module to same version")
            pico_lights_enable = False
        else:
            debug.print("Lights hub version matches module version")
            #Load group config from lights module
            debug.print("Loading group config from lights module")
            lights.get_groups() #type: ignore

    else:
        debug.print("Pico lights controller not found on bus, disabling module")
        pico_lights_enable = False

else:
    debug.print("No I2C devices found")

########################
# Webserver definition #
########################
@ppwhttp.route("/", methods=["GET", "POST"])
def get_home(method, url, data=None):
    if method == "POST":
        global r, g, b
        r = int(data.get("r", 0))
        g = int(data.get("g", 0))
        b = int(data.get("b", 0))
        if r == 255:
            print("Doing a demo")
            lights.set_light_demo()

    return """<form method="post" action="/">
    <input id="r" name="r" type="number" value="{r}" />
    <input name="g" type="number" value="{g}"  />
    <input name="b" type="number" value="{b}"  />
    <input type="submit" value="Set LED" />
</form>""".format(r=r, g=g, b=b)

@ppwhttp.route("/test", methods="GET")
def get_test(method, url):
    return "Hello World!"


#Init wifi
ppwhttp.start_wifi()

def server_loop_forever():
   # Start a server and continuously poll for HTTP requests
   server_sock = ppwhttp.start_server()
   while True:
       ppwhttp.handle_http_request(server_sock)
       time.sleep(0.01)

#Handle the server polling loop on the other core
_thread.start_new_thread(server_loop_forever, ())

#Main program loop
while True:
    print("Looping")
    time.sleep(5.0)