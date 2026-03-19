from pybricks.parameters import Color

hub = None
hub_name = None

try:
    from pybricks.hubs import TechnicHub
    hub = TechnicHub()
    hub_name = "TechnicHub"
except Exception as e:
    print("Skip TechnicHub:", e)

if hub is None:
    try:
        from pybricks.hubs import MoveHub
        hub = MoveHub()
        hub_name = "MoveHub"
    except Exception as e:
        print("Skip MoveHub:", e)

if hub is None:
    try:
        from pybricks.hubs import EssentialHub
        hub = EssentialHub()
        hub_name = "EssentialHub"
    except Exception as e:
        print("Skip EssentialHub:", e)

if hub is None:
    try:
        from pybricks.hubs import CityHub
        hub = CityHub()
        hub_name = "CityHub"
    except Exception as e:
        print("Skip CityHub:", e)

if hub is None:
    print("No hub detected")
else:
    try:
        voltage = hub.battery.voltage()
        print(hub_name, "battery:", voltage, "mV")
        color = Color.GREEN if voltage > 7000 else (Color.ORANGE if voltage > 6000 else Color.RED)
        if hasattr(hub, "light"):
            hub.light.on(color)
        else:
            print("No status light on this hub")
    except Exception as e:
        print("Battery read error:", e)
