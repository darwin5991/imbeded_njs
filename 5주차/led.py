import RPi.GPIO as GPIO
import time
import sys

def led_control(gpio):
    GPIO.setmode(GPIO.BCM)   # BCM 모드 설정
    GPIO.setup(gpio, GPIO.OUT)

    for _ in range(5):
        GPIO.output(gpio, GPIO.HIGH)  # LED ON
        time.sleep(1)
        GPIO.output(gpio, GPIO.LOW)   # LED OFF
        time.sleep(1)

    GPIO.cleanup()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python led.py GPIO_NO")
        sys.exit(1)

    gpio_pin = int(sys.argv[1])
    led_control(gpio_pin)
