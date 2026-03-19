# Technic Hub 42160 — RC car with battery status light
#
# What this program does:
#   - Controls a 4-wheeled RC car via a Powered Up remote.
#   - LEFT stick  (+/-): drive forward / backward (full power).
#   - RIGHT stick (+/-): steer left / right (full lock).
#   - CENTER (green) button: stop the program and turn off the hub light.
#
# Battery status light (checked every 5 seconds):
#   - GREEN  → battery voltage is OK (≥ 7200 mV, i.e. not discharging low).
#   - YELLOW → battery is low (< 7200 mV / discharging); shown for up to 1 minute.
#   - OFF    → after 1 minute of yellow warning the light turns off but the hub
#              keeps running — it does NOT shut down automatically.
#
# Motors:
#   - Port A: rear drive motor
#   - Port B: front drive motor
#   - Port D: steering motor

from pybricks.hubs import TechnicHub
from pybricks.parameters import Button, Color, Direction, Port
from pybricks.pupdevices import Motor, Remote
from pybricks.robotics import Car
from pybricks.tools import wait

# --- Tuning constants ---
BATTERY_LOW_MV = 7200        # Voltage threshold for "low" (millivolts). Fully charged ≈ 8400 mV
CHECK_INTERVAL_MS = 5000     # How often to check battery (ms)
LOW_BATTERY_WARN_MS = 60000  # How long to show yellow before turning light off (ms)

hub = TechnicHub()

# Connect motors and remote
steering = Motor(Port.D, Direction.CLOCKWISE)
front = Motor(Port.B, Direction.CLOCKWISE)
rear = Motor(Port.A, Direction.CLOCKWISE)
car = Car(steering, [front, rear])
remote = Remote(timeout=None)

low_battery_timer = 0
last_check = 0

while True:
    pressed = remote.buttons.pressed()

    # CENTER (green) button → quit
    if Button.CENTER in pressed:
        hub.light.off()
        break

    # Battery check (every CHECK_INTERVAL_MS)
    last_check += 50
    if last_check >= CHECK_INTERVAL_MS:
        last_check = 0
        voltage = hub.battery.voltage()

        if voltage >= BATTERY_LOW_MV:
            hub.light.on(Color.GREEN)
            low_battery_timer = 0
        else:
            low_battery_timer += CHECK_INTERVAL_MS
            if low_battery_timer <= LOW_BATTERY_WARN_MS:
                hub.light.on(Color.YELLOW)
            else:
                hub.light.off()  # 1 min yellow elapsed → light off, hub keeps running

    # Drive control — left: forward/backward, right: steering
    car.drive_power(
        100 if Button.LEFT_PLUS in pressed
        else (-100 if Button.LEFT_MINUS in pressed else 0)
    )
    car.steer(
        100 if Button.RIGHT_PLUS in pressed
        else (-100 if Button.RIGHT_MINUS in pressed else 0)
    )

    wait(50)
