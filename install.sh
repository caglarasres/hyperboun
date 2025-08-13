#!/bin/bash
# install.sh - Raspberry Pi üzerinde Hyperloop Control Panel projesi kurulumu

echo "🚀 Raspberry Pi kurulumu başlıyor..."

# 1️⃣ Sistemi güncelle
echo "📦 Sistem güncelleniyor..."
sudo apt update && sudo apt upgrade -y

# 2️⃣ Gerekli paketler
echo "📦 Gerekli paketler yükleniyor..."
sudo apt install -y python3-pip python3-venv python3-pigpio python3-opencv libatlas-base-dev pigpio

# 3️⃣ pigpio servisini başlat
echo "⚡ pigpio servisi başlatılıyor..."
sudo systemctl enable pigpiod
sudo systemctl start pigpiod

# 4️⃣ Kamera modülü etkin mi kontrol et (sadece Raspberry Pi OS)
if command -v raspi-config &> /dev/null; then
    echo "📷 Kamera modülü ve I2C arayüzü aktif ediliyor..."
    sudo raspi-config nonint do_camera 0
    sudo raspi-config nonint do_i2c 0
fi

# 5️⃣ Python sanal ortam oluştur
echo "🐍 Sanal ortam oluşturuluyor..."
python3 -m venv venv
source venv/bin/activate

# 6️⃣ Python bağımlılıkları
echo "📦 Python bağımlılıkları yükleniyor..."
pip install --upgrade pip
pip install flask pigpio pyserial opencv-python numpy picamera[array]

# 7️⃣ Kullanıcıya seri port hatırlatması
echo "🔌 Lütfen Arduino veya sensörlerin bağlı olduğu seri portu kontrol edin."
echo "   Mevcut portlar:"
ls /dev/ttyUSB* 2>/dev/null || echo "   (Hiçbir USB seri cihaz bağlı değil)"

# 8️⃣ Projeyi başlat
echo "🚦 Proje başlatılıyor..."
python app.py

# Script sonu
