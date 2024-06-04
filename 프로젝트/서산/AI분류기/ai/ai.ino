#include <Servo.h>
Servo servo;
#define dirPin 2
#define stepPin 3

int timer = 2000;
int servol = 60;
int servor = 120;
int steps = 10080;  // 1 step당 1.8도, 1바퀴에 200펄스

void setup() {
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);
  servo.attach(7);
  servo.write(90);
  Serial.begin(9600);
}

void loop() {
  if (Serial.available()) {
    char a = Serial.read();
    if (a == '1') {
      digitalWrite(dirPin, HIGH);
      for (int i = 0; i < steps; i++) {
        digitalWrite(stepPin, HIGH);
        delayMicroseconds(100);
        digitalWrite(stepPin, LOW);
        delayMicroseconds(100);
      }
      servo.write(servor);
      delay(timer);
      servo.write(90);
      delay(100);
      digitalWrite(dirPin, LOW);
      for (int i = 0; i < steps; i++) {
        digitalWrite(stepPin, HIGH);
        delayMicroseconds(100);
        digitalWrite(stepPin, LOW);
        delayMicroseconds(100);
      }
    }
    if (a == '2') {
      servo.write(servor);
      delay(timer);
      servo.write(90);
      delay(100);
    }
    if (a == '3') {
      servo.write(servol);
      delay(timer);
      servo.write(90);
      delay(100);
    }
    if (a == '4') {
      digitalWrite(dirPin, LOW);
      for (int i = 0; i < steps; i++) {
        digitalWrite(stepPin, HIGH);
        delayMicroseconds(100);
        digitalWrite(stepPin, LOW);
        delayMicroseconds(100);
      }
      servo.write(servol);
      delay(timer);
      servo.write(90);
      delay(100);
      digitalWrite(dirPin, HIGH);
      for (int i = 0; i < steps; i++) {
        digitalWrite(stepPin, HIGH);
        delayMicroseconds(100);
        digitalWrite(stepPin, LOW);
        delayMicroseconds(100);
      }
    }
  }
}