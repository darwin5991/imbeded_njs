import time
from gpiozero import Device, DistanceSensor, Servo, LED, DigitalInputDevice
# [수정] 하드웨어 PWM을 위한 pigpio 팩토리 임포트
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep, time

# [수정] 핀 팩토리를 PiGPIOFactory로 변경 (소프트웨어 덜덜거림 차단)
Device.pin_factory = PiGPIOFactory()

# =============================
# HC-SR04 초음파 센서
# =============================
ultrasonic = DistanceSensor(
    echo=26,       # GPIO26, Pin37
    trigger=16     # GPIO16, Pin36
)

# =============================
# SG90 서보모터
# =============================
# [수정] SG90 서보모터의 표준 펄스 폭 한계값(0.5ms ~ 2.5ms)을 정확하게 지정
servo = Servo(12, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)  # GPIO12, Pin32
servo.min()        # 차단기 닫힘

# =============================
# LED 12개 = 4행 x 3열 길
# 시작점: GPIO17(Pin11), 가운데
# =============================
LED_PINS = [
    [4, 17, 18],
    [27, 22, 23],
    [24, 25, 5],
    [6, 13, 19]
]

leds = [[LED(pin) for pin in row] for row in LED_PINS]

# =============================
# 조도센서 8개
# value == 1 : 차량 있음
# value == 0 : 빈자리
# =============================
LIGHT_SENSOR_PINS = [
    14, 15, 20, 21,   # L1~L4
    10, 9, 11, 8      # R1~R4
]

light_sensors = [DigitalInputDevice(pin) for pin in LIGHT_SENSOR_PINS]

# =============================
# 주차칸 정보
# =============================
PARKING_SPOTS = [
    {"name": "L1", "row": 0, "side": "left",  "sensor_index": 0},
    {"name": "L2", "row": 1, "side": "left",  "sensor_index": 1},
    {"name": "L3", "row": 2, "side": "left",  "sensor_index": 2},
    {"name": "L4", "row": 3, "side": "left",  "sensor_index": 3},

    {"name": "R1", "row": 0, "side": "right", "sensor_index": 4},
    {"name": "R2", "row": 1, "side": "right", "sensor_index": 5},
    {"name": "R3", "row": 2, "side": "right", "sensor_index": 6},
    {"name": "R4", "row": 3, "side": "right", "sensor_index": 7},
]

DETECT_DISTANCE = 50

car_detected = False
gate_open_time = None
guided_spot = None


def all_led_off():
    for row in leds:
        for led in row:
            led.off()


def show_path(target_row, side):
    all_led_off()

    start_col = 1  # GPIO17(Pin11), 가운데 시작

    for r in range(0, target_row + 1):
        leds[r][start_col].on()

    if side == "left":
        leds[target_row][0].on()
    elif side == "right":
        leds[target_row][2].on()


def find_empty_spot():
    for spot in PARKING_SPOTS:
        idx = spot["sensor_index"]

        if light_sensors[idx].value == 0:
            return spot

    return None


print("스마트 주차 시스템 시작")
print("초음파 감지 → 차단기 열림 → 5초 후 닫힘")
print("LED는 안내 주차칸 조도센서가 감지되면 꺼짐")

try:
    while True:
        distance = ultrasonic.distance * 100
        print(f"\n거리: {distance:.1f} cm")

        # 1. 초음파로 차량 감지
        if distance <= DETECT_DISTANCE and not car_detected:
            print("차량 감지됨")

            empty_spot = find_empty_spot()

            # 2. 만차 상태
            if empty_spot is None:
                print("만차 상태 → 차단기 열림 금지")
                servo.min()
                all_led_off()
                guided_spot = None

            # 3. 빈자리 안내
            else:
                guided_spot = empty_spot

                print(f"안내 주차칸: {guided_spot['name']}")
                print("차단기 열림")
                print("LED 길 안내 시작")

                servo.max()
                gate_open_time = time()

                show_path(guided_spot["row"], guided_spot["side"])

            car_detected = True

        # 4. 차단기는 열린 뒤 5초 지나면 닫힘
        if gate_open_time is not None:
            if time() - gate_open_time >= 5:
                print("5초 경과 → 차단기 닫힘")
                servo.min()
                gate_open_time = None

        # 5. 안내한 주차칸에 차가 주차됐인지 조도센서로 확인
        if guided_spot is not None:
            idx = guided_spot["sensor_index"]
            sensor_value = light_sensors[idx].value

            print(
                f"{guided_spot['name']} 주차 여부 확인 중... "
                f"조도센서 값: {sensor_value}"
            )

            if sensor_value == 1:
                print(f"{guided_spot['name']} 조도센서 감지됨")
                print("차량이 안내된 주차칸에 주차 완료")
                print("LED 길 안내 종료")

                all_led_off()
                guided_spot = None

        # 6. 초음파 범위 밖으로 나가면 다음 차량 감지 가능
        if distance > DETECT_DISTANCE:
            car_detected = False

        sleep(0.5)

except KeyboardInterrupt:
    print("\n프로그램 종료")
    servo.min()
    all_led_off()