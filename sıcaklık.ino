#include "max6675.h"

int thermoDO = 50;
int thermoCS = 48;
int thermoCLK = 52;

MAX6675 thermocouple(thermoCLK, thermoCS, thermoDO);

void setup() {
  Serial.begin(9600);
  delay(500);
}

void loop() {
  float temp = thermocouple.readCelsius();
  Serial.println(temp);
  delay(1000);
}
