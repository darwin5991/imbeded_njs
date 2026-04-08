from picamera2 import Picamera2
import cv2

picam2 = Picamera2()

preview_config = picam2.create_preview_configuration(
    main={"format": "XRGB8888", "size": (640, 480)}
)

picam2.configure(preview_config)
picam2.start()

img_no = 0

while True:

    image = picam2.capture_array()
    v_image = cv2.flip(image, 0)   # 상하 반전

    cv2.imshow("CAM Preview", v_image)

    key = cv2.waitKey(30) & 0xFF

    if key == 27:   # ESC 키
        break
    elif key == 115:   # s 키
        img_no += 1
        filename = "test" + str(img_no) + ".jpg"
        print(filename)
        cv2.imwrite(filename, v_image)

cv2.destroyAllWindows()
picam2.stop()
