from time import sleep

sensor = DistanceSensor(
    echo=26,      # Pin37
    trigger=16,   # Pin36
    max_distance=4
)

print("HC-SR04 측정 시작")

while True:
    distance = sensor.distance * 100

    print(f"거리 : {distance:.2f} cm")

    sleep(0.5)