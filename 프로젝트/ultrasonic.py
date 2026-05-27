from gpiozero import Device, DistanceSensor, Servo
from gpiozero.pins.lgpio import LGPIOFactory
from time import sleep, time

# Raspberry Pi 5 backend 설정
Device.pin_factory = LGPIOFactory()

# 초음파 센서
sensor = DistanceSensor(
    echo=26,
    trigger=16,
    max_distance=4
)

# 서보모터 (GPIO18 = Pin12)
servo = Servo(18)

servo.min()   # 초기 위치(반대방향)

detected = False
lost_time = None

print("시스템 시작")

while True:

    distance = sensor.distance * 100

    print(f"거리: {distance:.1f} cm")

    # 50cm 이하 → 감지
    if distance <= 50:

        if not detected:
            print("물체 감지 → 서보 회전")

            servo.max()     # 정방향 회전
            detected = True

        lost_time = None

    # 50cm 초과
    else:

        if detected:

            if lost_time is None:
                lost_time = time()

            elif time() - lost_time >= 5:

                print("5초 경과 → 반대방향 복귀")

                servo.min()     # 반대방향 복귀
                detected = False
                lost_time = None

    sleep(0.1)