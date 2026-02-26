from pybricks.parameters import Button, Direction, Port
from pybricks.pupdevices import Motor, Remote, Light
from pybricks.robotics import Car
from pybricks.tools import wait

# https://pybricks.com/project/technic-42160-powered-up-remote/#the-car-in-action

# Set up all devices.
steering = Motor(Port.D, Direction.CLOCKWISE)
front = Motor(Port.B, Direction.CLOCKWISE)
rear = Motor(Port.A, Direction.CLOCKWISE)
car = Car(steering, [front, rear])

# Remote and light on Port C
remote = Remote(timeout=None)
light = Light(Port.C)

# The main program starts here.
while True:
    # Read buttons once per loop to avoid querying multiple times.
    pressed = remote.buttons.pressed()

    # Turn light on if any button is pressed; otherwise turn it off.
    if pressed:
        light.on(100)  # 0..100 brightness
    else:
        light.off()

    # Control steering using the left - and + buttons.
    car.steer(
        100 if Button.LEFT_PLUS in pressed
        else (-100 if Button.LEFT_MINUS in pressed else 0)
    )

    # Control drive power using the right - and + buttons.
    car.drive_power(
        100 if Button.RIGHT_PLUS in pressed
        else (-100 if Button.RIGHT_MINUS in pressed else 0)
    )

    wait(50)
