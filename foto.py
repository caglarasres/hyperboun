import cv2

cap = cv2.VideoCapture(0)

ret, frame = cap.read()
if ret:
    cv2.imwrite("test.jpg", frame)
else:
    print("Görüntü alınamadı!")

cap.release()
