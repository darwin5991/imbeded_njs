from gpiozero import Device, DistanceSensor, Servo, LED, DigitalInputDevice
from gpiozero.pins.lgpio import LGPIOFactory
from time import sleep, time

Device.pin_factory = LGPIOFactory()

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
servo = Servo(12)  # GPIO12, Pin32
servo.min()        # 차단기 닫힘

# =============================
# LED 12개 = 4행 x 3열 길
# 입구 시작점: GPIO17(Pin11), 0행 1열
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
# value == 1 : 가려짐 / 차량 있음
# value == 0 : 밝음 / 빈자리
# =============================
LIGHT_SENSOR_PINS = [
    14, 15, 20, 21,   # 왼쪽 주차칸 L1~L4
    10, 9, 11, 8      # 오른쪽 주차칸 R1~R4
]

light_sensors = [
    DigitalInputDevice(pin) for pin in LIGHT_SENSOR_PINS
]

# =============================
# 주차칸 정보
# row는 LED 행 번호와 대응
# =============================
PARKING_SPOTS = [
    {"name": "L1", "row": 0, "side": "left"},
    {"name": "L2", "row": 1, "side": "left"},
    {"name": "L3", "row": 2, "side": "left"},
    {"name": "L4", "row": 3, "side": "left"},

    {"name": "R1", "row": 0, "side": "right"},
    {"name": "R2", "row": 1, "side": "right"},
    {"name": "R3", "row": 2, "side": "right"},
    {"name": "R4", "row": 3, "side": "right"},
]

DETECT_DISTANCE = 50
detected = False
lost_time = None


def all_led_off():
    for row in leds:
        for led in row:
            led.off()


def show_path(target_row, side):
    all_led_off()

    START_ROW = 0
    START_COL = 1   # GPIO17(Pin11), 가운데 시작

    # Pin11 가운데에서 목표 행까지 세로로 켜기
    for r in range(START_ROW, target_row + 1):
        leds[r][START_COL].on()

    # 목표 행에서 왼쪽/오른쪽 주차칸 방향 LED 켜기
    if side == "left":
        leds[target_row][0].on()
    elif side == "right":
        leds[target_row][2].on()


def find_empty_spot():
    for i, sensor in enumerate(light_sensors):
        if sensor.value == 0:   # 빈자리
            return PARKING_SPOTS[i]
    return None                 # 만차


def print_parking_status():
    print("주차칸 상태")
    for i, sensor in enumerate(light_sensors):
        spot = PARKING_SPOTS[i]
        if sensor.value == 1:
            print(f"{spot['name']} : 차량 있음")
        else:
            print(f"{spot['name']} : 빈자리")


print("스마트 주차 차단기 시스템 시작")
print("입구 시작 LED: GPIO17(Pin11)")

try:
    while True:
        distance = ultrasonic.distance * 100
        print(f"\n거리: {distance:.1f} cm")

        if distance <= DETECT_DISTANCE:
            if not detected:
                print("차량 감지됨")

                print_parking_status()
                empty_spot = find_empty_spot()

                if empty_spot is None:
                    print("만차 상태 → 차단기 열림 금지")
                    servo.min()
                    all_led_off()

                else:
                    print(f"안내할 빈 주차칸: {empty_spot['name']}")
                    print("차단기 열림 + LED 길 안내")

                    servo.max()
                    show_path(empty_spot["row"], empty_spot["side"])

                detected = True

            lost_time = None

        else:
            if detected:
                if lost_time is None:
                    lost_time = time()

                elif time() - lost_time >= 5:
                    print("차량 통과 후 5초 경과 → 차단기 닫힘")
                    servo.min()
                    all_led_off()

                    detected = False
                    lost_time = None

        sleep(0.5)

except KeyboardInterrupt:
    print("\n프로그램 종료")
    servo.min()
    all_led_off()