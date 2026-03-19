from pybricks.hubs import EssentialHub
from pybricks.pupdevices import Motor, ColorSensor
from pybricks.parameters import Port, Color
from pybricks.tools import wait

hub = EssentialHub()

# Startup battery indicator
voltage = hub.battery.voltage()
if voltage > 7000:
    hub.light.on(Color.GREEN)
else:
    hub.light.on(Color.YELLOW)
wait(2000)
hub.light.on(Color.WHITE)

motor = None
sensor = ColorSensor(Port.B)
sensor.detectable_colors([Color.GREEN, Color.RED, Color.NONE])

while True:
    # Try to detect motor if not yet connected
    if motor is None:
        try:
            motor = Motor(Port.A)
        except OSError:
            pass

    color = sensor.color()

    if color == Color.GREEN:
        if motor:
            motor.dc(-100)
        hub.light.on(Color.GREEN)
    elif color == Color.RED:
        if motor:
            motor.stop()
        hub.light.on(Color.RED)

    wait(50)
