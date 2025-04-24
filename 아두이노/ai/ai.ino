#include <Servo.h>
Servo servo;
#define dirPin 2
#define stepPin 3
#define a '\0'

int timer = 2000;
int servol = 60;
int servor = 120;
int steps = 400;  // 1 step당 1.8도, 1바퀴에 200펄스

void setup() {
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);
  servo.attach(7);
  servo.write(90);
  Serial.begin(9600);
}

void loop() {
  if (Serial.available()) {
    a = Serial.read();
    switch (a) {
      case '1':
        step(0);
        break;
      case '2':
        servo.write(servor);
        delay(timer);
        servo.write(90);
        break;
      case '3':
        servo.write(servol);
        delay(timer);
        servo.write(90);
      case '4':
        step(1);
        break;
      case 'q': // 테스트용
        digitalWrite(dirPin, HIGH);
        for (int i = 0; i < 4; i++) {
          digitalWrite(stepPin, HIGH);
          delayMicroseconds(50);
          digitalWrite(stepPin, LOW);
          delayMicroseconds(50);
        }
      case 'r': // 테스트용
        digitalWrite(dirPin, LOW);
        for (int i = 0; i < 800; i++) {
          digitalWrite(stepPin, HIGH);
          delayMicroseconds(50);
          digitalWrite(stepPin, LOW);
          delayMicroseconds(50);
        }
    }
  }
}

void step(int a) {
  digitalWrite(dirPin, a);
  for (int i = 0; i < steps; i++) {
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(50);
    digitalWrite(stepPin, LOW);
    delayMicroseconds(50);
  }
  if (a == 0) {
    servo.write(servor);
  } else {
    servo.write(servol);
  }
  delay(timer);
  servo.write(90);
  a = !a;
  digitalWrite(dirPin, a);
  for (int i = 0; i < steps; i++) {
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(50);
    digitalWrite(stepPin, LOW);
    delayMicroseconds(50);
  }
}
