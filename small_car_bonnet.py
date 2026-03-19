#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EssentialHub
from pybricks.pupdevices import Motor, Remote
from pybricks.parameters import Port, Direction, Button, Color

from pybricks.tools import wait

# Initialize the hub
hub = EssentialHub()

# Individual motors — no DriveBase, each side driven independently
left_motor = Motor(Port.A, Direction.COUNTERCLOCKWISE)
right_motor = Motor(Port.B)

# Wait for the remote to connect
hub.light.on(Color.ORANGE)
remote = Remote(timeout=None)
hub.light.on(Color.GREEN)
wait(500)

SPEED = 1000  # degrees per second (max)

while True:
    pressed = remote.buttons.pressed()

    # --- Left side buttons → left motor ---
    if Button.LEFT_PLUS in pressed:
        left_motor.run(SPEED)       # forward
    elif Button.LEFT_MINUS in pressed:
        left_motor.run(-SPEED)      # backward
    else:
        left_motor.stop()

    # --- Right side buttons → right motor ---
    # RIGHT_MINUS goes FORWARD only when BOTH LEFT_PLUS and RIGHT_PLUS are pressed
    both_plus = Button.LEFT_PLUS in pressed and Button.RIGHT_PLUS in pressed

    if Button.RIGHT_MINUS in pressed and both_plus:
        right_motor.run(SPEED)      # combo: forward
    elif Button.RIGHT_PLUS in pressed:
        right_motor.run(SPEED)      # forward
    elif Button.RIGHT_MINUS in pressed:
        right_motor.run(-SPEED)     # backward
    else:
        right_motor.stop()

    wait(10)
