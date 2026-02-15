from pybricks.hubs import EssentialHub
from pybricks.pupdevices import DCMotor, Motor, Remote, Light
from pybricks.parameters import Port, Button, Color
from pybricks.tools import wait, StopWatch

# -------------------------
# Config
# -------------------------
POLL_MS = 20

# Motor on Port A: steps -10..+10 -> duty -100..+100
MOTOR_MAX_STEP = 10
MOTOR_MIN_STEP = -MOTOR_MAX_STEP
MOTOR_MAX_DUTY = 100
MOTOR_SLEW_PER_TICK = 3  # duty % per tick (bigger = faster, smaller = smoother)

# Light on Port B: levels 0..10 -> brightness 0..100 in steps of 10
LIGHT_MAX_LEVEL = 10
LIGHT_SLEW_PER_TICK = 5  # brightness % per tick

# Logging
LOG_BUTTONS = True
LOG_STATE_CHANGES = True
LOG_RAMP_CHANGES = True

hub = EssentialHub()
watch = StopWatch()

def log(*args):
    print(f"[{watch.time():>6}ms]", *args)

# -------------------------
# Utilities
# -------------------------
def clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x

def step_to_duty(step):
    # -10..+10 -> -100..+100
    return int(step * MOTOR_MAX_DUTY / MOTOR_MAX_STEP)

def level_to_brightness(level):
    # 10-step brightness: 0..10 -> 0..100 by 10
    return int(level * 10)

def set_hub_indicator(brightness_pct):
    # Hub status LED mirrors brightness (as a "second light")
    if brightness_pct <= 0:
        hub.light.off()
    else:
        hub.light.on(Color.GREEN * (brightness_pct / 100))

# -------------------------
# Connectors
# -------------------------
def connect_remote():
    while True:
        try:
            hub.light.on(Color.YELLOW)
            rc = Remote(timeout=5000)
            rc.light.on(Color.GREEN)
            log("Remote connected.")
            return rc
        except OSError:
            hub.light.on(Color.RED)
            log("Remote not found. Turn it on and try again...")
            wait(300)

def connect_motor_port_a():
    """
    Try Motor(Port.A) FIRST (smart motor), then DCMotor(Port.A) (train motor).
    """
    while True:
        try:
            m = Motor(Port.A)
            log("Motor on Port A connected as Motor (smart motor).")
            return m
        except OSError as e:
            log("Motor(Port.A) not available:", repr(e))

        try:
            m = DCMotor(Port.A)
            log("Motor on Port A connected as DCMotor (train motor).")
            return m
        except OSError as e:
            log("DCMotor(Port.A) not available:", repr(e))

        hub.light.blink(Color.RED, [200, 200])
        log("No motor detected on Port A. Check cable/port.")
        wait(500)

def connect_light_port_b():
    while True:
        try:
            l = Light(Port.B)
            log("Light on Port B connected.")
            return l
        except OSError as e:
            hub.light.blink(Color.MAGENTA, [200, 200])
            log("No light detected on Port B:", repr(e))
            wait(500)

# -------------------------
# Setup
# -------------------------
rc = connect_remote()
motor = connect_motor_port_a()
light = connect_light_port_b()

# Targets
motor_target_step = 0          # -10..+10
light_target_level = 0         # 0..10

# Current ramped outputs
motor_current_duty = 0         # -100..+100
light_current_brightness = 0   # 0..100

# Last sent values (avoid redundant commands)
last_motor_sent = None
last_light_sent = None

# For logging state changes
last_logged_motor_step = None
last_logged_light_level = None
last_logged_motor_duty = None
last_logged_light_brightness = None

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

# Prime edge detection (COPY the set)
try:
    last_pressed = set(rc.buttons.pressed())
except OSError:
    last_pressed = set()

log("System info:", hub.system.info())
log("Ready. Controls:")
log("  Motor (Port A): LEFT + / LEFT - (steps -10..+10), LEFT red = smooth stop")
log("  Light (Port B): RIGHT + / RIGHT - (levels 0..10), RIGHT red = smooth off")
log("  CENTER (green) stops both (optional)")

# -------------------------
# Main loop
# -------------------------
while True:
    # Read remote (auto-reconnect)
    try:
        pressed = set(rc.buttons.pressed())  # COPY each time
    except OSError:
        log("Remote disconnected -> stopping motor + lights, reconnecting...")
        motor_target_step = 0
        light_target_level = 0
        motor_current_duty = 0
        light_current_brightness = 0
        apply_motor_duty(0)
        apply_light_brightness(0)
        hub.light.on(Color.RED)

        rc = connect_remote()
        last_pressed = set(rc.buttons.pressed())
        continue

    new_presses = pressed - last_pressed

    if LOG_BUTTONS and (new_presses or pressed):
        if new_presses:
            log("Buttons pressed:", pressed, "| new:", new_presses)

    if new_presses:
        # --- MOTOR (Port A) on LEFT side ---
        if Button.LEFT_PLUS in new_presses:
            motor_target_step = clamp(motor_target_step + 1, MOTOR_MIN_STEP, MOTOR_MAX_STEP)
            log("Motor step++ ->", motor_target_step)

        if Button.LEFT_MINUS in new_presses:
            motor_target_step = clamp(motor_target_step - 1, MOTOR_MIN_STEP, MOTOR_MAX_STEP)
            log("Motor step-- ->", motor_target_step)

        if Button.LEFT in new_presses:
            motor_target_step = 0
            log("Motor STOP requested (LEFT red)")

        # --- LIGHT (Port B) on RIGHT side ---
        if Button.RIGHT_PLUS in new_presses:
            light_target_level = clamp(light_target_level + 1, 0, LIGHT_MAX_LEVEL)
            log("Light level++ ->", light_target_level)

        if Button.RIGHT_MINUS in new_presses:
            light_target_level = clamp(light_target_level - 1, 0, LIGHT_MAX_LEVEL)
            log("Light level-- ->", light_target_level)

        if Button.RIGHT in new_presses:
            light_target_level = 0
            log("Light OFF requested (RIGHT red)")

        # Optional: center stops both
        if Button.CENTER in new_presses:
            motor_target_step = 0
            light_target_level = 0
            log("STOP BOTH requested (CENTER)")

    last_pressed = pressed

    # Log target changes
    if LOG_STATE_CHANGES:
        if motor_target_step != last_logged_motor_step:
            log("Motor target step =", motor_target_step, "-> target duty =", step_to_duty(motor_target_step))
            last_logged_motor_step = motor_target_step

        if light_target_level != last_logged_light_level:
            log("Light target level =", light_target_level, "-> target brightness =", level_to_brightness(light_target_level))
            last_logged_light_level = light_target_level

    # --- Smooth motor ramp (supports negative duty) ---
    motor_target_duty = step_to_duty(motor_target_step)  # -100..+100
    if motor_current_duty < motor_target_duty:
        motor_current_duty = min(motor_current_duty + MOTOR_SLEW_PER_TICK, motor_target_duty)
    elif motor_current_duty > motor_target_duty:
        motor_current_duty = max(motor_current_duty - MOTOR_SLEW_PER_TICK, motor_target_duty)

    apply_motor_duty(motor_current_duty)

    if LOG_RAMP_CHANGES and motor_current_duty != last_logged_motor_duty:
        log("Motor applied duty =", motor_current_duty)
        last_logged_motor_duty = motor_current_duty

    # --- Smooth light fade ---
    light_target_brightness = level_to_brightness(light_target_level)  # 0..100
    if light_current_brightness < light_target_brightness:
        light_current_brightness = min(light_current_brightness + LIGHT_SLEW_PER_TICK, light_target_brightness)
    elif light_current_brightness > light_target_brightness:
        light_current_brightness = max(light_current_brightness - LIGHT_SLEW_PER_TICK, light_target_brightness)

    apply_light_brightness(light_current_brightness)
    set_hub_indicator(light_current_brightness)

    if LOG_RAMP_CHANGES and light_current_brightness != last_logged_light_brightness:
        log("Light applied brightness =", light_current_brightness)
        last_logged_light_brightness = light_current_brightness

    wait(POLL_MS)
