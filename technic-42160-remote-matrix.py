from pybricks.hubs import TechnicHub
from pybricks.parameters import Button, Color, Direction, Port
from pybricks.pupdevices import ColorLightMatrix, Motor, Remote
from pybricks.robotics import Car
from pybricks.tools import wait

hub = TechnicHub()
steering = Motor(Port.D, Direction.CLOCKWISE)
front = Motor(Port.B, Direction.CLOCKWISE)
rear = Motor(Port.A, Direction.CLOCKWISE)
car = Car(steering, [front, rear])
matrix = ColorLightMatrix(Port.C)
remote = Remote(timeout=None)

blink = False
green_on = False
white_on = False
prev_pressed = set()
warning_active = False
warning_ticks = 0
pre_warning_green = None
pre_warning_white = None
WARNING_TICKS = 1200  # 60 seconds at 50ms per tick
WARNING_VOLTAGE = 6800

while True:
    pressed = remote.buttons.pressed()
    new_presses = pressed - prev_pressed
    car.steer(100 if Button.LEFT_PLUS in pressed else -100 if Button.LEFT_MINUS in pressed else 0)
    car.drive_power(100 if Button.RIGHT_PLUS in pressed else -100 if Button.RIGHT_MINUS in pressed else 0)

    # Button toggles (ignored during warning)
    if not warning_active:
        if Button.LEFT in new_presses:
            green_on = not green_on
        elif Button.RIGHT in new_presses:
            white_on = not white_on

    # Trigger low battery warning
    voltage = hub.battery.voltage()
    if not warning_active and voltage < WARNING_VOLTAGE:
        warning_active = True
        warning_ticks = 0
        pre_warning_green = green_on
        pre_warning_white = white_on

    # Handle warning display
    if warning_active:
        warning_ticks += 1
        if warning_ticks >= WARNING_TICKS:
            warning_active = False
            green_on = pre_warning_green
            white_on = pre_warning_white
        else:
            if pre_warning_green or pre_warning_white:
                matrix.on([Color.YELLOW] + [Color.NONE] * 8)
            else:
                matrix.on(Color.YELLOW)
    else:
        if white_on:
            matrix.on(Color.WHITE)
        elif green_on:
            blink = not blink
            matrix.on(Color.GREEN if voltage > 7500 else Color.YELLOW if voltage > 6500 else Color.RED) if blink else matrix.off()
        else:
            matrix.off()

    prev_pressed = pressed
    wait(50)

# daca se descarca bateria, pe alb sa apara 1 minuta si pe verde 1 minuta si verdele sa nu se mai aprinda, dupa 1 minuta lumina alba se aprinde inapoi