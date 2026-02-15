from pybricks.hubs import EssentialHub
from pybricks.pupdevices import DCMotor, Motor, Remote, Light
from pybricks.parameters import Port, Button, Color
from pybricks.tools import wait

# -------------------------
# Config
# -------------------------
POLL_MS = 20

# Motor on Port A: steps 0..10 -> duty 0..100
MOTOR_MAX_STEP = 10
MOTOR_MAX_DUTY = 100
MOTOR_SLEW_PER_TICK = 3      # duty % change per tick (bigger = faster, smaller = smoother)

# Light on Port B: levels 0..10 -> brightness 0..100 (10% per level)
LIGHT_MAX_LEVEL = 10
LIGHT_SLEW_PER_TICK = 5      # brightness % change per tick

hub = EssentialHub()

# -------------------------
# Utilities
# -------------------------
def clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x

def step_to_duty(step):
    return int(step * MOTOR_MAX_DUTY / MOTOR_MAX_STEP)

def level_to_brightness(level):
    # 10-step brightness: 0..10 -> 0..100 in steps of 10
    return int(level * 10)

def connect_remote():
    while True:
        try:
            hub.light.on(Color.YELLOW)
            rc = Remote(timeout=5000)
            rc.light.on(Color.GREEN)
            print("Remote connected.")
            return rc
        except OSError:
            hub.light.on(Color.RED)
            print("Remote not found. Turn it on and try again...")
            wait(300)

def connect_motor_port_a():
    while True:
        try:
            m = DCMotor(Port.A)
            print("Motor on Port A: DCMotor")
            return m
        except OSError:
            pass

        try:
            m = Motor(Port.A)
            print("Motor on Port A: Motor")
            return m
        except OSError:
            hub.light.blink(Color.RED, [200, 200])
            print("No motor detected on Port A. Check cable/port.")
            wait(500)

def connect_light_port_b():
    while True:
        try:
            l = Light(Port.B)
            print("Light on Port B connected.")
            return l
        except OSError:
            hub.light.blink(Color.MAGENTA, [200, 200])
            print("No light detected on Port B. Check cable/port.")
            wait(500)

def set_hub_indicator(brightness_pct):
    # Hub light as "second light" that follows brightness
    if brightness_pct <= 0:
        hub.light.off()
    else:
        hub.light.on(Color.GREEN * (brightness_pct / 100))

# -------------------------
# Setup
# -------------------------
rc = connect_remote()
motor = connect_motor_port_a()
light = connect_light_port_b()

motor_target_step = 0           # 0..10
light_target_level = 0          # 0..10

motor_current_duty = 0          # 0..100
light_current_brightness = 0    # 0..100

last_motor_sent = None
last_light_sent = None

def apply_motor_duty(duty):
    global last_motor_sent
    duty = clamp(duty, -100, 100)
    if duty != last_motor_sent:
        motor.dc(duty)
        last_motor_sent = duty

def apply_light_brightness(brightness):
    global last_light_sent
    brightness = clamp(brightness, 0, 100)
    if brightness != last_light_sent:
        if brightness == 0:
            light.off()
        else:
            light.on(brightness)
        last_light_sent = brightness

# Prime edge detection
try:
    last_pressed = rc.buttons.pressed()
except OSError:
    last_pressed = set()

# -------------------------
# Main loop
# -------------------------
while True:
    try:
        pressed = rc.buttons.pressed()
    except OSError:
        print("Remote disconnected -> stopping motor + lights, reconnecting...")
        motor_target_step = 0
        light_target_level = 0
        motor_current_duty = 0
        light_current_brightness = 0
        apply_motor_duty(0)
        apply_light_brightness(0)
        hub.light.on(Color.RED)

        rc = connect_remote()
        last_pressed = rc.buttons.pressed()
        continue

    new_presses = pressed - last_pressed

    if new_presses:
        # LEFT side controls MOTOR (Port A)
        if Button.LEFT_PLUS in new_presses:
            motor_target_step = clamp(motor_target_step + 1, 0, MOTOR_MAX_STEP)
        if Button.LEFT_MINUS in new_presses:
            motor_target_step = clamp(motor_target_step - 1, 0, MOTOR_MAX_STEP)
        if Button.LEFT in new_presses:
            motor_target_step = 0  # smooth stop

        # RIGHT side controls LIGHT (Port B)
        if Button.RIGHT_PLUS in new_presses:
            light_target_level = clamp(light_target_level + 1, 0, LIGHT_MAX_LEVEL)
        if Button.RIGHT_MINUS in new_presses:
            light_target_level = clamp(light_target_level - 1, 0, LIGHT_MAX_LEVEL)
        if Button.RIGHT in new_presses:
            light_target_level = 0  # smooth off (light + hub indicator)

        # Optional: center stops both
        if Button.CENTER in new_presses:
            motor_target_step = 0
            light_target_level = 0

    last_pressed = pressed

    # Smooth motor ramp
    motor_target_duty = step_to_duty(motor_target_step)
    if motor_current_duty < motor_target_duty:
        motor_current_duty = min(motor_current_duty + MOTOR_SLEW_PER_TICK, motor_target_duty)
    elif motor_current_duty > motor_target_duty:
        motor_current_duty = max(motor_current_duty - MOTOR_SLEW_PER_TICK, motor_target_duty)
    apply_motor_duty(motor_current_duty)

    # Smooth light fade (10% steps as target)
    light_target_brightness = level_to_brightness(light_target_level)
    if light_current_brightness < light_target_brightness:
        light_current_brightness = min(light_current_brightness + LIGHT_SLEW_PER_TICK, light_target_brightness)
    elif light_current_brightness > light_target_brightness:
        light_current_brightness = max(light_current_brightness - LIGHT_SLEW_PER_TICK, light_target_brightness)

    apply_light_brightness(light_current_brightness)
    set_hub_indicator(light_current_brightness)

    wait(POLL_MS)
