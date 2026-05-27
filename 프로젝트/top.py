import time
from gpiozero import Device, DistanceSensor, Servo, DigitalInputDevice, LED
from gpiozero.pins.lgpio import LGPIOFactory
from time import sleep

Device.pin_factory = LGPIOFactory()

# -------------------------------------------------
# 핀 설정
# 실제 배선에 맞게 바꾸세요
# -------------------------------------------------
TRIGGER_PIN = 16
ECHO_PIN = 26
SERVO_PIN = 12

LIGHT_PINS = [5, 6, 13, 19, 20, 21, 22, 23]      # 8개 디지털 입력 (주차 공간)
LED_PINS = [24, 25, 8, 7, 1, 0, 27, 17, 18, 4, 14, 15]  # 12개 LED 출력 (경로 안내)

# -------------------------------------------------
# 장치 초기화
# -------------------------------------------------
distance_sensor = DistanceSensor(
    echo=ECHO_PIN,
    trigger=TRIGGER_PIN,
    max_distance=4
)

servo = Servo(SERVO_PIN)
light_inputs = [DigitalInputDevice(pin) for pin in LIGHT_PINS]
leds = [LED(pin) for pin in LED_PINS]

# 기본 상태
servo.value = -1.0  # 초기에는 닫힘 상태(-1.0)로 설정

# -------------------------------------------------
# 전역 상태 변수
# -------------------------------------------------
is_servo_open = False
servo_open_time = 0.0
is_guiding = False
target_spot = -1

# [중요] 각 주차 공간(0~7번)으로 갈 때 켜져야 하는 LED 인덱스(0~11) 매핑 테이블
# 실제 주차장과 LED 배선 모양에 맞게 배열 내용을 수정해서 사용하세요.
SPOT_TO_LEDS = {
    0: [0, 1, 2],       # 예: 0번 자리로 갈 땐 0, 1, 2번 LED 켬
    1: [0, 1, 3],
    2: [4, 5, 6],
    3: [4, 5, 7],
    4: [8, 9, 10],
    5: [8, 9, 11],
    6: [2, 6, 10],
    7: [3, 7, 11]
}

def read_light_bits():
    # 센서 종류에 따라 1이 빛 가림(차량 있음), 0이 빈자리일 수 있습니다.
    # 만약 반대라면 int(not sensor.value) 로 수정하세요.
    return [int(sensor.value) for sensor in light_inputs]

def set_led_pattern(pattern):
    for led, value in zip(leds, pattern):
        if value:
            led.on()
        else:
            led.off()

def decide_outputs(distance_cm, light_bits, current_time):
    global is_servo_open, servo_open_time, is_guiding, target_spot

    # 1. 차단기 자동 닫힘 처리 (3초 경과 확인)
    if is_servo_open and (current_time - servo_open_time >= 3.0):
        is_servo_open = False

    # 2. 주차 완료 감지 (안내 중인 칸에 조도 센서 반응)
    # light_bits[x] == 1 을 차량이 있는 상태로 간주
    if is_guiding and target_spot != -1:
        if light_bits[target_spot] == 1:
            is_guiding = False  # 안내 종료 (LED 꺼짐)
            target_spot = -1

    # 3. 새로운 차량 진입 감지
    # 초음파 20cm 이내 감지 & 현재 차단기가 닫혀있음 & 현재 안내 중인 차량이 없음
    if distance_cm <= 20.0 and not is_servo_open and not is_guiding:
        # 빈자리 찾기 (값이 0인 센서의 인덱스들)
        empty_spots = [i for i, state in enumerate(light_bits[:8]) if state == 0]

        if empty_spots: # 빈 자리가 하나라도 있다면
            target_spot = empty_spots[0] # 첫 번째 빈 공간을 타겟으로 지정
            is_guiding = True
            is_servo_open = True
            servo_open_time = current_time # 타이머 시작
        else:
            # 만차 상태: 작동 안 함
            pass

    # 4. 하드웨어 출력값 생성
    servo_value = 1.0 if is_servo_open else -1.0
    
    led_pattern = [0] * 12
    if is_guiding and target_spot != -1:
        # 안내 타겟에 매핑된 경로 LED만 1로 설정
        leds_to_turn_on = SPOT_TO_LEDS.get(target_spot, [])
        for led_idx in leds_to_turn_on:
            if led_idx < 12:
                led_pattern[led_idx] = 1

    return servo_value, led_pattern

try:
    print("스마트 주차장 시스템 시작...")
    while True:
        # 현재 시간 기록 (타이머용)
        current_time = time.time()
        
        # 센서 데이터 수집
        distance_cm = distance_sensor.distance * distance_sensor.max_distance * 100
        light_bits = read_light_bits()

        # 알고리즘 함수 호출
        servo_value, led_pattern = decide_outputs(distance_cm, light_bits, current_time)

        # 액추에이터 제어
        servo.value = servo_value
        set_led_pattern(led_pattern)

        # 현재 상태 출력 (디버깅용)
        guide_status = f"Guiding Spot: {target_spot}" if is_guiding else "Idle/Full"
        print(f"Dist: {distance_cm:.1f}cm | Spots: {light_bits} | Servo: {servo_value} | {guide_status}")
        
        sleep(0.1)

except KeyboardInterrupt:
    print("\n시스템 종료")

finally:
    # 안전 종료 처리
    servo.value = -1.0
    set_led_pattern([0] * 12)

    for sensor in light_inputs:
        sensor.close()

    for led in leds:
        led.close()

    distance_sensor.close()
    servo.close()