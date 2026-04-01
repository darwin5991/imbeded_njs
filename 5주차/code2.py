import RPi.GPIO as GPIO
import time

GPIO_PIN = 18  # 여기 고정

def led_control(gpio):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(gpio, GPIO.OUT)

    for _ in range(5):
        GPIO.output(gpio, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(gpio, GPIO.LOW)
        time.sleep(1)

    GPIO.cleanup()

led_control(GPIO_PIN)