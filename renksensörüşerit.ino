// TCS3200 ile sadece KIRMIZI şerit algılama
// Pinler
const int S0 = 4;
const int S1 = 5;
const int S2 = 6;
const int S3 = 7;
const int OUT_PIN = 8;
// (OE'yi GND'ye bağlayabilirsin; istersen aktif kullanmak için alttaki satırı aç)
// const int OE = 9;

const int LED_PIN = 13; // Kırmızı algılanınca yak

// Eşik ve oranlar (ayarlanabilir)
float redDominanceThresh = 0.55;   // r/(r+g+b) > 0.55 ise kırmızı baskın say
float redOverOthersRatio = 1.30;   // r > 1.3*max(g,b)
float baselineBoost = 1.10;        // r > 1.10 * r_baseline

// Kalibrasyon için zemin (kırmızı olmayan) ortalamaları
float baseR = 0, baseG = 0, baseB = 0;

unsigned long readPeriodOnce() {
  // Bir tam periyot: LOW + HIGH
  unsigned long lowT  = pulseIn(OUT_PIN, LOW, 25000UL);   // 25ms timeout
  unsigned long highT = pulseIn(OUT_PIN, HIGH, 25000UL);
  if (lowT == 0 || highT == 0) return 0;
  return lowT + highT; // mikro-saniye
}

float readFrequency() {
  // Gürültüyü azaltmak için birkaç örnek al
  const int N = 5;
  unsigned long sumPeriod = 0;
  int ok = 0;
  for (int i = 0; i < N; i++) {
    unsigned long T = readPeriodOnce();
    if (T > 0) { sumPeriod += T; ok++; }
  }
  if (ok == 0) return 0.0;
  float avgT = (float)sumPeriod / ok; // us
  return 1000000.0f / avgT; // Hz
}

float readColor(char channel) {
  // S2/S3 ile filtre seçimi
  // R: L,L  G: H,H  B: L,H  (TCS3200 için yaygın eşleştirme)
  switch (channel) {
    case 'R': digitalWrite(S2, LOW);  digitalWrite(S3, LOW);  break;
    case 'G': digitalWrite(S2, HIGH); digitalWrite(S3, HIGH); break;
    case 'B': digitalWrite(S2, LOW);  digitalWrite(S3, HIGH); break;
  }
  delayMicroseconds(200); // filtre otursun
  return readFrequency();
}

void calibrateBaseline(int samples = 40) {
  // Kırmızı ŞERİT YOKKEN sensörü zemine bakacak şekilde tut!
  float sumR = 0, sumG = 0, sumB = 0;
  for (int i = 0; i < samples; i++) {
    float r = readColor('R');
    float g = readColor('G');
    float b = readColor('B');
    sumR += r; sumG += g; sumB += b;
    delay(10);
  }
  baseR = sumR / samples;
  baseG = sumG / samples;
  baseB = sumB / samples;
}

bool isRedStripe(float r, float g, float b) {
  float total = r + g + b;
  if (total <= 0) return false;

  float rDom = r / total;
  float maxGB = max(g, b);

  bool condDominance = (rDom > redDominanceThresh);
  bool condOverOthers = (r > redOverOthersRatio * maxGB);
  bool condAboveBase = (r > baselineBoost * baseR);

  // Üçünden en az ikisi sağlansın (daha güvenli)
  int score = 0;
  if (condDominance)  score++;
  if (condOverOthers) score++;
  if (condAboveBase)  score++;

  return score >= 2;
}

void setup() {
  pinMode(S0, OUTPUT);
  pinMode(S1, OUTPUT);
  pinMode(S2, OUTPUT);
  pinMode(S3, OUTPUT);
  pinMode(OUT_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);
  // pinMode(OE, OUTPUT); digitalWrite(OE, LOW); // aktif

  Serial.begin(115200);
  delay(300);

  // Frekans ölçekleme: S0=H, S1=L -> %20 (sık doygunluk yaşamamak için iyi)
  digitalWrite(S0, HIGH);
  digitalWrite(S1, LOW);

  Serial.println("Kalibrasyon basliyor: Lutfen kirmizi serit GORUNMEYECEK!");
  delay(500);
  calibrateBaseline();
  Serial.print("Baseline R/G/B: ");
  Serial.print(baseR, 1); Serial.print(" / ");
  Serial.print(baseG, 1); Serial.print(" / ");
  Serial.println(baseB, 1);
  Serial.println("Algilama basliyor...");
}

void loop() {
  float r = readColor('R');
  float g = readColor('G');
  float b = readColor('B');

  bool red = isRedStripe(r, g, b);

  if (red) {
    digitalWrite(LED_PIN, HIGH);
    Serial.print("RED_STRIPE ");
  } else {
    digitalWrite(LED_PIN, LOW);
    Serial.print("NO_RED ");
  }

  // Debug çıktısı (istersen kapat)
  float total = r + g + b + 1e-6; // 0 bölmeyi önle
  Serial.print("R:"); Serial.print(r, 1);
  Serial.print(" G:"); Serial.print(g, 1);
  Serial.print(" B:"); Serial.print(b, 1);
  Serial.print(" r%:");
  Serial.println(r / total, 3);

  delay(50); // örnekleme hızı
}
