import cv2
import time

cap = cv2.VideoCapture(0)
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('kayit.avi', fourcc, 20.0, (640, 480))

if not cap.isOpened():
    print("Kamera açılamadı!")
    exit()

start_time = time.time()
duration = 10  # saniye cinsinden süre

while True:
    ret, frame = cap.read()
    if not ret:
        print("Görüntü alınamadı, kayıt sonlanıyor.")
        break

    out.write(frame)

    if time.time() - start_time > duration:
        print("Belirlenen süre doldu, kayıt bitiyor.")
        break

cap.release()
out.release()
