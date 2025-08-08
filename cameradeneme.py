import cv2

cap = cv2.VideoCapture(0)  # /dev/video0

# Video codec ve dosya ayarları
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('kayit.avi', fourcc, 20.0, (640, 480))

if not cap.isOpened():
    print("Kamera açılamadı!")
    exit()

print("Video kaydı başladı, durdurmak için Ctrl+C")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Görüntü alınamadı, kayıt sonlanıyor.")
            break
        out.write(frame)
except KeyboardInterrupt:
    print("\nKayıt durduruldu.")

cap.release()
out.release()
