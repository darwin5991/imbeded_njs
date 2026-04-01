import RPi.GPIO as GPIO
import time
import sys


def led_control(gpio_pin, blink_count, interval_ms):
    interval_sec = interval_ms / 1000.0

    GPIO.setmode(GPIO.BCM)      # BCM 번호 체계 사용
    GPIO.setup(gpio_pin, GPIO.OUT)

    try:
        for _ in range(blink_count):
            GPIO.output(gpio_pin, GPIO.HIGH)  # LED ON
            time.sleep(interval_sec)
            GPIO.output(gpio_pin, GPIO.LOW)   # LED OFF
            time.sleep(interval_sec)
    finally:
        GPIO.cleanup()


def parse_args():
    if len(sys.argv) != 4:
        print("Usage: python3 led2.py GPIO_NO BLINK_COUNT INTERVAL_MS")
        print("Example: python3 led2.py 18 10 300")
        sys.exit(1)

    try:
        gpio_pin = int(sys.argv[1])
        blink_count = int(sys.argv[2])
        interval_ms = int(sys.argv[3])
    except ValueError:
        print("Error: All arguments must be integers.")
        sys.exit(1)

    if gpio_pin < 0:
        print("Error: GPIO_NO must be >= 0.")
        sys.exit(1)
    if blink_count <= 0:
        print("Error: BLINK_COUNT must be > 0.")
        sys.exit(1)
    if interval_ms <= 0:
        print("Error: INTERVAL_MS must be > 0.")
        sys.exit(1)

    return gpio_pin, blink_count, interval_ms


if __name__ == "__main__":
    gpio, count, ms = parse_args()
    led_control(gpio, count, ms)