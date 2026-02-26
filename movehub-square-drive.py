# pybricks-micropython

from pybricks.hubs import MoveHub
from pybricks.parameters import Direction, Port, Color
from pybricks.pupdevices import ColorDistanceSensor, Motor
from pybricks.robotics import DriveBase

# --- Setup ---
hub = MoveHub()
sensor = ColorDistanceSensor(Port.C)
left = Motor(Port.A, Direction.COUNTERCLOCKWISE)
right = Motor(Port.B, Direction.CLOCKWISE)
robot = DriveBase(left, right, 43, 112)

# Faster motion (tune to your surface to avoid slip).
robot.settings(
    straight_speed=300,         # mm/s
    straight_acceleration=700,  # mm/s^2
    turn_rate=180,              # deg/s
    turn_acceleration=360       # deg/s^2
)

# --- Behavior controls ---
SIDE_MM  = 250   # side length for the square
STEP_MM  = 15    # step size so we can check often for white
CLEAR_MM = 40    # move forward after the 180° spin to clear the white area

# Direction of 90° corner turns: +1 = left (CCW), -1 = right (CW)
turn_dir = +1

def hard_stop_hold():
    """Stop the drivebase and actively hold motors (no Stop arg)."""
    robot.stop()     # DriveBase.stop() takes no arguments on your version
    left.hold()      # Actively hold each motor
    right.hold()

def handle_white_and_reverse():
    """On white: stop, rotate 180°, move off the patch, flip turn direction."""
    global turn_dir
    hard_stop_hold()
    robot.turn(180)
    robot.straight(CLEAR_MM)
    turn_dir *= -1

def see_white_by_color():
    """Return True iff the sensor confidently reads white."""
    c = sensor.color()  # may be None if no color is recognized
    return c == Color.WHITE

def drive_side_with_white_handling():
    """
    Drive ~SIDE_MM in STEP_MM chunks, checking for white before and after each step.
    Returns True if a white event was handled; False otherwise.
    """
    traveled = 0
    while traveled < SIDE_MM:
        if see_white_by_color():
            handle_white_and_reverse()
            return True

        step = min(STEP_MM, SIDE_MM - traveled)
        robot.straight(step)
        traveled += step

        if see_white_by_color():
            handle_white_and_reverse()
            return True

    return False

# --- Main: drive a square; reverse behavior on white ---
for _ in range(4):
    _white_triggered = drive_side_with_white_handling()
    robot.turn(180 * turn_dir)

# Ensure motors are stopped and held at the end.
hard_stop_hold()
