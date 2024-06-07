#define dirPin 2
#define stepPin 3
#define a '\0'

void setup() {
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  a = Serial.read();
  if (a == '1') {
    digitalWrite(dirPin, HIGH);
    for (int i = 0; i < 480; i++) {
      digitalWrite(stepPin, HIGH);
      delayMicroseconds(50);
      digitalWrite(stepPin, LOW);
      delayMicroseconds(50);
    }
    if (a == '0') {
      digitalWrite(dirPin, LOW);
      for (int i = 0; i < 480; i++) {
        digitalWrite(stepPin, HIGH);
        delayMicroseconds(50);
        digitalWrite(stepPin, LOW);
        delayMicroseconds(50);
      }
    }
  }
