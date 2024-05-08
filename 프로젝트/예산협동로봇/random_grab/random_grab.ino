#define wlkatastatus "@01O103"
#define resetfile "@01$h"
#define file1 "@01O111position_1"
#define file2 "@01O111position_2"
#define file3 "@01O111position_3"
#define file4 "@01O111position_4"
#define file5 "@01O111position_5"

HardwareSerial* wlkata = &Serial1;

char sequence[] = { 'R', 'D', 'G', 'V' };

int mirobotStatus() {
  //Clear the serial port content first
  while (wlkata->available()) wlkata->readString();
  wlkata->println(wlkatastatus);
  delay(100);
  String strStatus = wlkata->readString();
  //0/1/2/3/4/5 0 Offline 1 Normal 2 Locked 3 Resetting 4 Busy 5 Running
  if (strStatus.indexOf("0") >= 0) return 0;
  if (strStatus.indexOf("1") >= 0) return 1;
  if (strStatus.indexOf("2") >= 0) return 2;
  if (strStatus.indexOf("3") >= 0) return 3;
  if (strStatus.indexOf("4") >= 0) return 4;
  if (strStatus.indexOf("5") >= 0) return 5;
}

void setup() {
  randomSeed(analogRead(0));
  Serial.begin(9600);
  delay(100);
  wlkata->begin(38400);
  delay(100);
  while (true) {
    if (mirobotStatus() == 1) break;
    if (mirobotStatus() == 2) break;
  }
  delay(1000);
  wlkata->println(resetfile);
  delay(1000);
}

void loop() {
  while (mirobotStatus() == 5)
    ;

  shuffleArray();

  for (int i = 0; i < 4; i++) {
    Serial.print(sequence[i]);
    switch (sequence[i]) {
      case 'R': wlkata->println(file1); break;
      case 'D': wlkata->println(file2); break;
      case 'G': wlkata->println(file3); break;
      case 'V': wlkata->println(file4); break;
    }
    delay(1000);
  }
  Serial.println();
}

void shuffleArray() {
  for (int i = 0; i < 4; i++) {
    int j = random(i, 4);
    char temp = sequence[i];
    sequence[i] = sequence[j];
    sequence[j] = temp;
  }
}
