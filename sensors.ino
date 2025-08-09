#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <max6675.h>
#include <ArduinoJson.h>

// -------- MAX6675 (Arduino Mega SPI) --------
const int PIN_SCK = 52;   // SCK
const int PIN_SO  = 50;   // MISO (SO/DO)
const int PIN_CS  = 53;   // CS
MAX6675 tc(PIN_SCK, PIN_CS, PIN_SO);

// -------- MPU6050 --------
Adafruit_MPU6050 mpu;

// -------- ACS724 --------
const int PIN_ACS = A0;       // ACS724 analog çıkışı
const float ACS_SENS_V_PER_A = 0.2; // Volt/A  (örn: 10A versiyon ~0.2 V/A)
const float ADC_REF_V = 5.0;  // Mega ADC referansı
const int   ADC_MAX   = 1023; // 10-bit ADC
float v_zero = 2.5;           // 0A ofseti (kalibrasyonda belirlenecek)

void calibrateACS724() {
  long acc = 0;
  const int samples = 500;
  for (int i = 0; i < samples; i++) {
    acc += analogRead(PIN_ACS);
    delay(2);
  }
  float adc_avg = (float)acc / samples;
  v_zero = (adc_avg * ADC_REF_V) / ADC_MAX;
}

void setup() {
  Serial.begin(9600);
  delay(300);
  Wire.begin(); // Mega: SDA=20, SCL=21

  // MAX6675 güvenli başlangıç
  pinMode(PIN_CS, OUTPUT);
  digitalWrite(PIN_CS, HIGH);
  delay(250); // MAX6675 ilk ölçüm için gerekli ~200-250ms

  // MPU6050 başlat
  if (!mpu.begin(0x68)) {  // AD0=GND → 0x68, AD0=VCC → 0x69 deneyebilirsiniz
    Serial.println("{\"error\":\"MPU6050 not found\"}");
    while (1) delay(10);
  }
  mpu.setAccelerometerRange(MPU6050_RANGE_2_G);
  mpu.setGyroRange(MPU6050_RANGE_250_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

  // ACS724 sıfır akım kalibrasyonu (üzerinden akım geçmiyorken!)
  calibrateACS724();
}

void loop() {
  // --- MPU6050 ---
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  // --- MAX6675 ---
  double tC = tc.readCelsius();  // prob yok/tersse NaN dönebilir

  // --- ACS724 ---
  float vout = (analogRead(PIN_ACS) * ADC_REF_V) / ADC_MAX;
  float currentA = (vout - v_zero) / ACS_SENS_V_PER_A;

  // --- JSON oluştur (tek satır) ---
  StaticJsonDocument<512> doc;  // güvenli boyut
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

  // MAX6675: NaN ise null yaz
  if (isnan(tC)) doc["max6675_c"] = nullptr;
  else           doc["max6675_c"] = tC;

  JsonObject acs = doc.createNestedObject("acs724");
  acs["amps"]  = currentA;
  acs["vout"]  = vout;
  acs["vzero"] = v_zero;

  // Seri hatta tek satır JSON + newline
  serializeJson(doc, Serial);
  Serial.println();

  delay(200); // ~5 Hz
}
