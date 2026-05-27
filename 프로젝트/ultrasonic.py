from gpiozero import Device
from gpiozero.pins.lgpio import LGPIOFactory
from gpiozero import DistanceSensor
from time import sleep

Device.pin_factory = LGPIOFactory()

sensor = DistanceSensor(
    echo=26,
    trigger=16
)

while True:
    print(f"거리 : {sensor.distance*100:.2f} cm")
    sleep(0.5)