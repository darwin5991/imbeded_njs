from gpiozero import DigitalInputDevice
from time import sleep

# 라즈베리파이 GPIO 4번 핀(BCM 기준)을 디지털 입력으로 설정
# (NOT 게이트의 출력 핀을 GPIO 4번에 연결했다고 가정)
sensor_in = DigitalInputDevice(4)

print("조도 센서 감지 시작... (종료하려면 Ctrl+C 입력)")

try:
    while True:
        # value 속성은 핀의 전압 상태에 따라 1 (High) 또는 0 (Low)을 반환합니다.
        current_state = sensor_in.value
        
        if current_state == 1:
            print(f"입력: {current_state} (High) -> 센서가 가려짐 (어두움)")
        else:
            print(f"입력: {current_state} (Low)  -> 센서가 열려있음 (밝음)")
            
        # 0.5초마다 한 번씩 상태를 샘플링합니다.
        sleep(0.5)

except KeyboardInterrupt:
    print("\n프로그램을 안전하게 종료합니다.")