 from gpiozero import Device, DistanceSensor, Servo
from gpiozero.pins.lgpio import LGPIOFactory
from time import sleep, time

Device.pin_factory = LGPIOFactory()

# 초음파 센서 US1
sensor = DistanceSensor(
    echo=26,       # GPIO26, Pin37
    trigger=16     # GPIO16, Pin36
)

# 서보모터
servo = Servo(12)  # GPIO12, Pin32

# 초기 차단기 닫힘 상태
servo.min()

# -----------------------------
# 설정값
# -----------------------------
DETECT_DISTANCE = 50     # 50cm 이하이면 차량 감지
MAX_CARS = 10            # 최대 입차 가능 차량 수

# -----------------------------
# 상태 변수
# -----------------------------
car_count = 0            # 차단기가 열린 횟수 = 입차 차량 수
detected = False         # 현재 차량이 감지된 상태인지 확인
lost_time = None         # 차량이 사라진 시간 기록

print("스마트 주차 차단기 테스트 시작")
print(f"최대 주차 가능 대수: {MAX_CARS}대")

while True:
    distance = sensor.distance * 100

    print(f"거리: {distance:.1f} cm / 입차 수: {car_count}/{MAX_CARS}")

    # 차량이 50cm 안에 감지된 경우
    if distance <= DETECT_DISTANCE:

        # 새 차량이 처음 감지된 순간만 처리
        if not detected:

            # 이미 만차인 경우
            if car_count >= MAX_CARS:
                print("만차 상태 → 차량 감지됨")
                print("차단기 열림 금지")
                servo.min()   # 차단기 닫힌 상태 유지

            # 만차가 아닌 경우
            else:
                car_count += 1
                print("차량 감지 → 차단기 열림")
                print(f"현재 입차 수: {car_count}/{MAX_CARS}")

                servo.max()   # 차단기 열림

                if car_count == MAX_CARS:
                    print("이번 차량 입차 후 만차 상태가 됩니다.")

            detected = True

        # 차량이 계속 감지 중이면 lost_time 초기화
        lost_time = None

    # 차량이 50cm 밖으로 사라진 경우
    else:

        # 이전에 차량이 감지된 상태였다면
        if detected:

            # 처음 사라진 순간 시간 기록
            if lost_time is None:
                lost_time = time()

            # 차량이 사라진 뒤 5초가 지나면 차단기 닫기
            elif time() - lost_time >= 5:

                print("차량 통과 후 5초 경과 → 차단기 닫힘")

                servo.min()   # 차단기 닫힘

                detected = False
                lost_time = None

    sleep(0.1)