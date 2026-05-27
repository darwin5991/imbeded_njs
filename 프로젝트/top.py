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

LIGHT_PINS = [5, 6, 13, 19, 20, 21, 22, 23]      # 8개 디지털 입력
LED_PINS = [24, 25, 8, 7, 1, 0, 27, 17, 18, 4, 14, 15]  # 12개 LED 출력

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
servo.value = 0

def read_light_bits():
    return [int(sensor.value) for sensor in light_inputs]

def set_led_pattern(pattern):
    for led, value in zip(leds, pattern):
        if value:
            led.on()
        else:
            led.off()

def decide_outputs(distance_cm, light_bits):
    """
    나중에 들어갈 알고리즘 자리.
    반환값:
      servo_value: -1.0 ~ 1.0
      led_pattern: 길이 12의 0/1 리스트
    """
    # 임시 예시:
    # 가까우면 서보 열고, 멀면 닫기
    servo_value = 1.0 if distance_cm <= 20 else -1.0

    # 임시 예시:
    # 조도 입력 8개를 참고해서 LED 12개를 단순 패턴으로 표시
    led_pattern = [0] * 12
    for i in range(min(len(light_bits), 8)):
        led_pattern[i] = light_bits[i]
    led_pattern[8:] = [1 if distance_cm <= 20 else 0] * 4

    return servo_value, led_pattern

try:
    print("시스템 시작")
    while True:
        distance_cm = distance_sensor.distance * distance_sensor.max_distance * 100
        light_bits = read_light_bits()

        servo_value, led_pattern = decide_outputs(distance_cm, light_bits)

        servo.value = servo_value
        set_led_pattern(led_pattern)

        print(f"distance={distance_cm:.1f}cm  lights={light_bits}  servo={servo_value}")
        sleep(0.1)

except KeyboardInterrupt:
    print("종료")

finally:
    servo.value = 0
    set_led_pattern([0] * 12)

    for sensor in light_inputs:
        sensor.close()

    for led in leds:
        led.close()

    distance_sensor.close()
    servo.close()