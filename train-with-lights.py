from pybricks.hubs import EssentialHub
from pybricks.pupdevices import DCMotor, Remote, Light
from pybricks.parameters import Port, Button, Color
from pybricks.tools import wait

# Initialize the hub.
hub = EssentialHub()

# ── Port detection ────────────────────────────────────────────────────────────
# Hub Logo light pulses YELLOW during the check.
hub.light.blink(Color.YELLOW, [200, 200])
print("Checking ports...")

def try_motor(port):
    try:
        m = DCMotor(port)
        print("Motor found on", port)
        return m
    except Exception:
        print("No motor on", port)
        return None

def try_light(port):
    try:
        l = Light(port)
        l.off()
        print("Light found on", port)
        return l
    except Exception:
        print("No light on", port)
        return None

# Port A: train motor (required).
train_motor = try_motor(Port.A)
if train_motor is None:
    # Logo light turns RED — motor missing, cannot run.
    hub.light.on(Color.RED)
    print("ERROR: No motor on Port A. Plug in the train motor and restart.")
    wait(5000)
    hub.system.shutdown()

# Port B: front light (optional).
front_light = try_light(Port.B)

# Essential Hub only has ports A and B — no Port C.
rear_light = None

print("Port check complete.")

# ── Wait for remote ───────────────────────────────────────────────────────────
# IMPORTANT: Press the green button on the remote BEFORE running this script!
hub.light.blink(Color.YELLOW, [500, 500])
remote = Remote(timeout=10000)

# Connected — Logo light turns GREEN briefly.
hub.light.on(Color.GREEN)
print("Remote connected!")
wait(1000)

# ── State ─────────────────────────────────────────────────────────────────────
SPEED_STEP = 10
BRIGHTNESS_STEP = 10

current_speed = 0
current_brightness = 0
previous_buttons = set()


def set_lights(brightness):
    """Apply brightness to all connected lights."""
    if front_light:
        if brightness == 0:
            front_light.off()
        else:
            front_light.on(brightness)
    if rear_light:
        if brightness == 0:
            rear_light.off()
        else:
            rear_light.on(brightness)


def update_logo_light(speed):
    """Hub Logo light mirrors motor direction.
    GREEN  = forward
    ORANGE = reverse
    RED    = stopped
    """
    if speed > 0:
        hub.light.on(Color.GREEN)
    elif speed < 0:
        hub.light.on(Color.ORANGE)
    else:
        hub.light.on(Color.RED)


# ── Main loop ─────────────────────────────────────────────────────────────────
while True:
    pressed = remote.buttons.pressed()
    new_presses = pressed - previous_buttons

    if new_presses:
        print("Buttons:", new_presses,
              "| Speed:", current_speed,
              "| Brightness:", current_brightness)

    # Any red / center button → full stop.
    if Button.CENTER in new_presses or Button.LEFT in new_presses or Button.RIGHT in new_presses:
        current_speed = 0
        current_brightness = 0
        train_motor.stop()
        set_lights(0)
        print("STOP — everything off.")

    else:
        # LEFT PLUS: speed up.
        if Button.LEFT_PLUS in new_presses:
            current_speed = min(current_speed + SPEED_STEP, 100)
            train_motor.dc(current_speed)
            print("Speed up:", current_speed)

        # LEFT MINUS: slow down / reverse.
        if Button.LEFT_MINUS in new_presses:
            current_speed = max(current_speed - SPEED_STEP, -100)
            if current_speed == 0:
                train_motor.stop()
            else:
                train_motor.dc(current_speed)
            print("Speed down:", current_speed)

        # RIGHT PLUS: brighter lights.
        if Button.RIGHT_PLUS in new_presses:
            current_brightness = min(current_brightness + BRIGHTNESS_STEP, 100)
            set_lights(current_brightness)
            print("Light up:", current_brightness)

        # RIGHT MINUS: dimmer lights.
        if Button.RIGHT_MINUS in new_presses:
            current_brightness = max(current_brightness - BRIGHTNESS_STEP, 0)
            set_lights(current_brightness)
            print("Light down:", current_brightness)

    # Remote light shows speed direction; hub Logo light mirrors it too.
    update_logo_light(current_speed)
    if current_speed > 0:
        remote.light.on(Color.GREEN)
    elif current_speed < 0:
        remote.light.on(Color.ORANGE)
    else:
        remote.light.on(Color.RED)

    previous_buttons = pressed
    wait(100)
