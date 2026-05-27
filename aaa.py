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
servo.min()        # 차단기 닫힘 상태

# =============================
# LED 12개 = 4행 x 3열 길
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

# =============================
# 설정값
# =============================
DETECT_DISTANCE = 50   # 50cm 이하 차량 감지
detected = False
lost_time = None


# =============================
# LED 전체 끄기
# =============================
def all_led_off():
    for row in leds:
        for led in row:
            led.off()


# =============================
# LED 길 안내
# =============================
def show_path(target_row, side):
    all_led_off()

    center_col = 1

    # 입구가 아래쪽 가운데라고 가정
    for r in range(3, target_row - 1, -1):
        leds[r][center_col].on()

    # 왼쪽 주차칸 안내
    if side == "left":
        leds[target_row][0].on()

    # 오른쪽 주차칸 안내
    elif side == "right":
        leds[target_row][2].on()


# =============================
# 빈 주차칸 찾기
# =============================
def find_empty_spot():
    for i, sensor in enumerate(light_sensors):

        # value == 0 이면 빈자리
        if sensor.value == 0:
            return PARKING_SPOTS[i]

    # 전부 value == 1 이면 만차
    return None


# =============================
# 주차칸 상태 출력
# =============================
def print_parking_status():
    print("주차칸 상태")

    for i, sensor in enumerate(light_sensors):
        spot = PARKING_SPOTS[i]

        if sensor.value == 1:
            print(f"{spot['name']} : 차량 있음")
        else:
            print(f"{spot['name']} : 빈자리")


# =============================
# 메인 코드
# =============================
print("스마트 주차 차단기 시스템 시작")
print("초음파 감지 → 조도센서 확인 → 서보모터 차단기 → LED 길 안내")

try:
    while True:
        distance = ultrasonic.distance * 100

        print(f"\n거리: {distance:.1f} cm")

        # 차량 감지
        if distance <= DETECT_DISTANCE:

            if not detected:
                print("차량 감지됨")

                print_parking_status()

                empty_spot = find_empty_spot()

                # 만차
                if empty_spot is None:
                    print("만차 상태")
                    print("차단기 열림 금지")
                    servo.min()
                    all_led_off()

                # 빈자리 있음
                else:
                    print(f"안내할 빈 주차칸: {empty_spot['name']}")
                    print("차단기 열림")
                    print("LED 길 안내 시작")

                    servo.max()
                    show_path(empty_spot["row"], empty_spot["side"])

                detected = True

            lost_time = None

        # 차량이 초음파 범위 밖으로 나간 경우
        else:
            if detected:

                if lost_time is None:
                    lost_time = time()

                elif time() - lost_time >= 5:
                    print("차량 통과 후 5초 경과")
                    print("차단기 닫힘")
                    print("LED 꺼짐")

                    servo.min()
                    all_led_off()

                    detected = False
                    lost_time = None

        sleep(0.5)

except KeyboardInterrupt:
    print("\n프로그램 종료")
    servo.min()
    all_led_off()