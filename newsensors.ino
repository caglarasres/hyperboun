#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <max6675.h>
#include <ArduinoJson.h>

// -------- MAX6675 (Arduino Mega SPI) --------
// Mega SPI: SCK=52, MISO(SO)=50, CS=53
const int PIN_SCK = 52;
const int PIN_SO  = 50;
const int PIN_CS  = 53;
MAX6675 tc(PIN_SCK, PIN_CS, PIN_SO);

// -------- MPU6050 (I2C) --------
// Mega I2C: SDA=20, SCL=21
Adafruit_MPU6050 mpu;

// -------- HC-SR04 --------
const int PIN_TRIG = 7;
const int PIN_ECHO = 6;
// ~30 ms timeout ≈ ~5 m (sesin gidiş-dönüş süresi)
const unsigned long ECHO_TIMEOUT_US = 30000UL;

void setup() {
  Serial.begin(9600);
  delay(300);

  // I2C başlat
  Wire.begin(); // Mega: SDA=20, SCL=21

  // MAX6675 güvenli başlangıç
  pinMode(PIN_CS, OUTPUT);
  digitalWrite(PIN_CS, HIGH);
  delay(250); // ilk ölçüm için gerekli ~200-250ms

  // HC-SR04 pinleri
  pinMode(PIN_TRIG, OUTPUT);
  pinMode(PIN_ECHO, INPUT);
  digitalWrite(PIN_TRIG, LOW);

  // MPU6050 başlat
  if (!mpu.begin(0x68)) { // AD0=GND→0x68, AD0=VCC→0x69
    Serial.println("{\"error\":\"MPU6050 not found\"}");
    while (1) delay(10);
  }
  mpu.setAccelerometerRange(MPU6050_RANGE_2_G);
  mpu.setGyroRange(MPU6050_RANGE_250_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
}

float readHCSR04_cm() {
  // 10 µs tetik
  digitalWrite(PIN_TRIG, LOW); delayMicroseconds(2);
  digitalWrite(PIN_TRIG, HIGH); delayMicroseconds(10);
  digitalWrite(PIN_TRIG, LOW);

  unsigned long dur = pulseIn(PIN_ECHO, HIGH, ECHO_TIMEOUT_US);
  if (dur == 0) return NAN; // timeout

  // Ses hızı ~343 m/s @ 20°C  → 0.0343 cm/µs; gidiş-dönüş → /2
  float cm = (dur * 0.0343f) / 2.0f;
  return cm;
}

void loop() {
  // --- MPU6050 ---
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  // --- MAX6675 ---
  double tC = tc.readCelsius(); // prob yok/tersse NaN olabilir

  // --- HC-SR04 ---
  float dist_cm = readHCSR04_cm();

  // --- JSON oluştur (tek satır) ---
  StaticJsonDocument<512> doc;
  doc["t_ms"] = millis();

  JsonObject imu = doc.createNestedObject("mpu6050");
  JsonObject accel = imu.createNestedObject("accel_g");
  const float g0 = 9.80665;
  accel["x"] = a.acceleration.x / g0;
  accel["y"] = a.acceleration.y / g0;
  accel["z"] = a.acceleration.z / g0;

  JsonObject gyro = imu.createNestedObject("gyro_dps");
  gyro["x"] = g.gyro.x * 57.29578;
  gyro["y"] = g.gyro.y * 57.29578;
  gyro["z"] = g.gyro.z * 57.29578;

  imu["temp_c"] = temp.temperature;

  // MAX6675: NaN ise null
  if (isnan(tC)) doc["max6675_c"] = nullptr;
  else           doc["max6675_c"] = tC;

  // HC-SR04: NaN ise null
  JsonObject us = doc.createNestedObject("hcsr04");
  if (isnan(dist_cm)) {
    us["distance_cm"] = nullptr;
    us["timeout"] = true;
  } else {
    us["distance_cm"] = dist_cm;
    us["timeout"] = false;
  }

  // Seri hatta tek satır JSON + newline
  serializeJson(doc, Serial);
  Serial.println();

  delay(200); // ~5 Hz
}
