#!/usr/bin/python3
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np

def detect_red_yellow_objects(image):
    """Kırmızı ve sarı nesneleri algıla ve kutucuk içine al"""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Kırmızı renk aralıkları (HSV)
    red_lower1 = np.array([0, 50, 50])
    red_upper1 = np.array([10, 255, 255])
    red_lower2 = np.array([170, 50, 50])
    red_upper2 = np.array([180, 255, 255])
    
    # Sarı renk aralığı (HSV)
    yellow_lower = np.array([20, 50, 50])
    yellow_upper = np.array([30, 255, 255])
    
    # Kırmızı maskeler oluştur
    red_mask1 = cv2.inRange(hsv, red_lower1, red_upper1)
    red_mask2 = cv2.inRange(hsv, red_lower2, red_upper2)
    red_mask = cv2.bitwise_or(red_mask1, red_mask2)
    
    # Sarı maske oluştur
    yellow_mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
    
    # Gürültüyü azalt
    kernel = np.ones((5, 5), np.uint8)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel)
    yellow_mask = cv2.morphologyEx(yellow_mask, cv2.MORPH_OPEN, kernel)
    yellow_mask = cv2.morphologyEx(yellow_mask, cv2.MORPH_CLOSE, kernel)
    
    detected_objects = 0
    
    # Kırmızı nesneleri bul ve çiz
    red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in red_contours:
        area = cv2.contourArea(contour)
        if area > 300:  # Minimum alan kontrolü
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)  # Kırmızı kutucuk
            cv2.putText(image, "KIRMIZI", (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            detected_objects += 1
            print(f"Kırmızı nesne bulundu: x={x}, y={y}, w={w}, h={h}")
    
    # Sarı nesneleri bul ve çiz
    yellow_contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in yellow_contours:
        area = cv2.contourArea(contour)
        if area > 300:  # Minimum alan kontrolü
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 255), 2)  # Sarı kutucuk
            cv2.putText(image, "SARI", (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            detected_objects += 1
            print(f"Sarı nesne bulundu: x={x}, y={y}, w={w}, h={h}")
    
    return detected_objects

def main():
    # Kamerayı başlat
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 32
    rawCapture = PiRGBArray(camera, (640, 480))
    
    # Kameranın ısınmasını bekle
    time.sleep(0.1)
    
    print("=== Kırmızı ve Sarı Nesne Algılama Başlatıldı ===")
    print("Çıkmak için 'q' tuşuna basın")
    print("=" * 50)
    
    try:
        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
            image = frame.array.copy()
            
            # Kırmızı ve sarı nesneleri algıla
            detected_count = detect_red_yellow_objects(image)
            
            # Durum bilgilerini göster
            cv2.putText(image, f"Algılanan Nesne: {detected_count}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(image, "Kırmızı/Sarı Nesne Algılama", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(image, "Çıkış için 'q' tuşuna basın", 
                       (10, image.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Görüntüyü göster
            cv2.imshow('Kırmızı/Sarı Nesne Algılama', image)
            
            # Buffer'ı temizle
            rawCapture.truncate(0)
            rawCapture.seek(0)
            
            # Çıkış kontrolü
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                print("Çıkış yapılıyor...")
                break
                
    except KeyboardInterrupt:
        print("\nProgram kullanıcı tarafından durduruldu")
        
    finally:
        # Kaynakları temizle
        cv2.destroyAllWindows()
        camera.close()
        print("Program sonlandırıldı")

if __name__ == '__main__':
    main()
