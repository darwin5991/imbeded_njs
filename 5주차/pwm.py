import RPi.GPIO as GPIO 
import time 
import sys 
 
def led_pwm_control(gpio_pin): 
    GPIO.setmode(GPIO.BCM) 
    GPIO.setup(gpio_pin, GPIO.OUT) 
 
    pwm = GPIO.PWM(gpio_pin, 1000)  # 1kHz 주파수 PWM 생성 
    pwm.start(0)                     # 듀티 사이클 0%로 시작 
 
    try: 
        for i in range(10000): 
            duty = i % 256                       # 0~255 반복 
            pwm.ChangeDutyCycle(duty * 100 / 255) # → 0~100% 
            time.sleep(0.005) 
    finally: 
        pwm.ChangeDutyCycle(0) 
        pwm.stop() 
        GPIO.cleanup() 
 
if __name__ == "__main__": 
    if len(sys.argv) < 2: 
        print(f"Usage: {sys.argv[0]} GPIO_NO") 
        sys.exit(1) 
    led_pwm_control(int(sys.argv[1])) 