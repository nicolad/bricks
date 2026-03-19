from pybricks.hubs import MoveHub
from pybricks.pupdevices import Motor, Remote
from pybricks.parameters import Port, Button, Color
from pybricks.tools import wait

# Initialize the hub
hub = MoveHub()

# Drive motors (internal A+B)
motor_a = Motor(Port.A)
motor_b = Motor(Port.B)

# Steering motor (external D) — optional
try:
    steering = Motor(Port.D)
except OSError:
    steering = None

# Reset steering to known center position
if steering:
    steering.reset_angle(0)

# Wait for the remote to connect
hub.light.on(Color.ORANGE)
remote = Remote(timeout=None)
hub.light.on(Color.GREEN)
wait(500)

DRIVE_SPEED = 1000   # degrees per second for drive motors
STEER_SPEED = 200    # degrees per second for steering — do not change this angle

was_steering = False

while True:
    pressed = remote.buttons.pressed()

    # CENTER button → emergency stop
    if Button.CENTER in pressed:
        motor_a.stop()
        motor_b.stop()
        if steering:
            steering.stop()
        hub.light.on(Color.RED)
        remote.light.on(Color.RED)
        wait(50)
        continue

    # LEFT +/−: drive forward / backward
    if Button.LEFT_PLUS in pressed:
        motor_a.run(DRIVE_SPEED)
        motor_b.run(-DRIVE_SPEED)
    elif Button.LEFT_MINUS in pressed:
        motor_a.run(-DRIVE_SPEED)
        motor_b.run(DRIVE_SPEED)
    else:
        motor_a.stop()
        motor_b.stop()

    # RIGHT +/−: steering on port D, auto-return to center on release
    is_steering = Button.RIGHT_PLUS in pressed or Button.RIGHT_MINUS in pressed
    if steering:
        if Button.RIGHT_PLUS in pressed:
            steering.run(STEER_SPEED)
        elif Button.RIGHT_MINUS in pressed:
            steering.run(-STEER_SPEED)
        elif was_steering:
            steering.run_target(STEER_SPEED, 0)  # return to center — do not change steering angle
    was_steering = is_steering

    # Hub light feedback (drive buttons only)
    if Button.LEFT_PLUS in pressed:
        hub.light.on(Color.GREEN)
    elif Button.LEFT_MINUS in pressed:
        hub.light.on(Color.ORANGE)
    else:
        hub.light.on(Color.WHITE)

    wait(50)
