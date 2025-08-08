#!/usr/bin/python3
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np

def detect_red_yellow_objects(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    red_lower1 = np.array([0, 50, 50])
    red_upper1 = np.array([10, 255, 255])
    red_lower2 = np.array([170, 50, 50])
    red_upper2 = np.array([180, 255, 255])
    yellow_lower = np.array([20, 50, 50])
    yellow_upper = np.array([30, 255, 255])

    red_mask1 = cv2.inRange(hsv, red_lower1, red_upper1)
    red_mask2 = cv2.inRange(hsv, red_lower2, red_upper2)
    red_mask = cv2.bitwise_or(red_mask1, red_mask2)
    yellow_mask = cv2.inRange(hsv, yellow_lower, yellow_upper)

    kernel = np.ones((5, 5), np.uint8)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel)
    yellow_mask = cv2.morphologyEx(yellow_mask, cv2.MORPH_OPEN, kernel)
    yellow_mask = cv2.morphologyEx(yellow_mask, cv2.MORPH_CLOSE, kernel)

    detected_objects = 0

    red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in red_contours:
        area = cv2.contourArea(contour)
        if area > 300:
            detected_objects += 1

    yellow_contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in yellow_contours:
        area = cv2.contourArea(contour)
        if area > 300:
            detected_objects += 1

    return detected_objects

def main():
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 24
    rawCapture = PiRGBArray(camera, size=(640, 480))
    time.sleep(0.1)  # Kamera ısınması için

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('video_kayit.avi', fourcc, 24, (640, 480))

    print("Kayıt başladı, durdurmak için CTRL+C")

    try:
        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
            image = frame.array

            # Nesne algılama (isteğe bağlı, çıktı verilebilir)
            count = detect_red_yellow_objects(image)
            print(f"Algılanan nesne sayısı: {count}")

            # Video kaydet
            out.write(image)

            rawCapture.truncate(0)

    except KeyboardInterrupt:
        print("\nKayıt durduruldu.")

    finally:
        out.release()
        camera.close()
        print("Program sonlandırıldı.")

if __name__ == "__main__":
    main()
