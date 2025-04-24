#include <Adafruit_CircuitPlayground.h>

float X, Y, Z;
#define MOVE_THRESHOLD 3

void setup() {
  Serial.begin(9600);
  CircuitPlayground.begin();
}

void loop() {
  X = CircuitPlayground.motionX();
  Y = CircuitPlayground.motionY();
  Z = CircuitPlayground.motionZ();

  Serial.print(X);
  Serial.print("      ");
  Serial.print(Y);
  Serial.print("      ");
  Serial.println(Z);
  delay(500);
}
