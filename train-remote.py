from pybricks.hubs import EssentialHub
from pybricks.pupdevices import DCMotor, Remote, Light
from pybricks.parameters import Port, Button, Color
from pybricks.tools import wait

# Initialize the hub.
hub = EssentialHub()

# Initialize the train motor on Port A.
train_motor = DCMotor(Port.A)

# Initialize the light on Port B.
light = Light(Port.B)
light.off()

# Optional device on Port C — won't crash if nothing is plugged in.
try:
    port_c_light = Light(Port.C)
    port_c_light.off()
    print("Port C light detected.")
except Exception:
    port_c_light = None
    print("Nothing on Port C, continuing without it.")

# Blink yellow while waiting for remote.
# IMPORTANT: Press the green button on the remote BEFORE running this script!
hub.light.blink(Color.YELLOW, [500, 500])
remote = Remote(timeout=10000)

# Connected! Light turns green.
hub.light.on(Color.GREEN)
print("Remote connected!")
wait(1000)

# Speed settings: 10 steps from 0 to 100.
speed_step = 10
current_speed = 0

# Light brightness: 10 steps from 0 to 100.
brightness_step = 10
current_brightness = 0

previous_buttons = set()

while True:
    pressed = remote.buttons.pressed()
    new_presses = pressed - previous_buttons

    # Log ALL button presses.
    if new_presses:
        print("New presses:", new_presses)
        print("Speed:", current_speed, "Brightness:", current_brightness)

    # Red button: stop everything.
    if Button.CENTER in new_presses or Button.LEFT in new_presses or Button.RIGHT in new_presses:
        current_speed = 0
        current_brightness = 0
        train_motor.stop()
        light.off()
        if port_c_light:
            port_c_light.off()
        print(">>> STOP! Everything off.")

    else:
        # LEFT PLUS: accelerate train motor.
        if Button.LEFT_PLUS in new_presses:
            current_speed = min(current_speed + speed_step, 100)
            train_motor.dc(current_speed)
            print(">>> Motor speed up:", current_speed)

        # LEFT MINUS: decelerate train motor.
        if Button.LEFT_MINUS in new_presses:
            current_speed = max(current_speed - speed_step, -100)
            if current_speed == 0:
                train_motor.stop()
            else:
                train_motor.dc(current_speed)
            print(">>> Motor slow down:", current_speed)

        # RIGHT PLUS: increase light brightness.
        if Button.RIGHT_PLUS in new_presses:
            current_brightness = min(current_brightness + brightness_step, 100)
            light.on(current_brightness)
            if port_c_light:
                port_c_light.on(current_brightness)
            print(">>> Light up:", current_brightness)

        # RIGHT MINUS: decrease light brightness.
        if Button.RIGHT_MINUS in new_presses:
            current_brightness = max(current_brightness - brightness_step, 0)
            if current_brightness == 0:
                light.off()
                if port_c_light:
                    port_c_light.off()
            else:
                light.on(current_brightness)
                if port_c_light:
                    port_c_light.on(current_brightness)
            print(">>> Light down:", current_brightness)

    # Remote light shows motor status.
    if current_speed > 0:
        remote.light.on(Color.GREEN)
    elif current_speed < 0:
        remote.light.on(Color.ORANGE)
    else:
        remote.light.on(Color.RED)

    previous_buttons = pressed
    wait(100)