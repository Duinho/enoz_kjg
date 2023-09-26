int choice = 0;


#define OUT A4  // 숫자 표시 회로판의 A0, A1 핀에 연결
#define IN A5   // 숫자 표시 회로판의 A2, A3 핀에 연결


#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
#include <avr/power.h>
#endif


int BRIGHTNESS = 30;  // LED 밝기
Adafruit_NeoPixel strip(16, 8, NEO_GRB + NEO_KHZ800);

char NEO_1 = "", NEO_2 = "", NEO_3 = "", NEO_4 = "";

int NEO_1C = 0, NEO_2C = 0, NEO_3C = 0, NEO_4C = 0;

int BUT_1 = A0, BUT_2 = A1, BUT_3 = A2, BUT_4 = A3;

int BUT_C = 0;

const char NEO_ARR[4][8] = {
  { 'X', 'R', 'G', 'B', 'O', 'R', 'G', 'O' },  // B
  { 'X', 'B', 'O', 'G', 'R', 'O', 'B', 'G' },  // R
  { 'X', 'O', 'R', 'O', 'B', 'G', 'R', 'B' },  // G
  { 'X', 'G', 'B', 'R', 'G', 'B', 'O', 'R' },  // O
};

void setup() {
#if defined(__AVR_ATtiny85__) && (F_CPU == 16000000)  // 네오픽셀 설정
  clock_prescale_set(clock_div_1);
#endif
  strip.begin();  // 네오픽셀 선언
  strip.clear();
  strip.show();
  Serial.begin(9600);
}

void loop() {
  /*
    if (!digitalRead(IN)) {
      BUTTON_C();
      NEO_C();
    } else {
      RESET();
    }*/
  for (int j = 0; j < 8; j++) {
    for (int i = 0; i < 4; i++) {
      NEO_V(i, NEO_ARR[0][j]);
    }
    for (int i = 4; i < 8; i++) {
      NEO_V(i, NEO_ARR[1][j]);
    }
    for (int i = 8; i < 12; i++) {
      NEO_V(i, NEO_ARR[2][j]);
    }
    for (int i = 12; i < 16; i++) {
      NEO_V(i, NEO_ARR[3][j]);
    }
    strip.show();
    delay(1000);
  }
  //NEO_V(9, 'R');
}

void BUTTON_C() {
  if (BUT_C) {
    if (digitalRead(BUT_1)) {
      NEO_1C++;
      if (NEO_1C == 8) NEO_1C = 0;
      delay(200);
      for (int i = 0; i < 4; i++) {
        NEO_V(i, NEO_ARR[1][NEO_1C]);
      }
      while (!digitalRead(BUT_1)) delay(5);
    }
    if (digitalRead(BUT_2)) {
      NEO_2C++;
      if (NEO_2C == 8) NEO_2C = 0;
      delay(200);
      while (!digitalRead(BUT_2)) delay(5);
    }
    if (digitalRead(BUT_3)) {
      NEO_3C++;
      if (NEO_3C == 8) NEO_3C = 0;

      delay(200);
      while (!digitalRead(BUT_3)) delay(5);
    }
    if (digitalRead(BUT_4)) {
      NEO_4C++;
      if (NEO_4C == 8) NEO_4C = 0;
      delay(200);
      while (!digitalRead(BUT_4)) delay(5);
    }
  }
}

void NEO_C() {
  NEO_1 = NEO_ARR[0][NEO_1C], NEO_2 = NEO_ARR[1][NEO_2C], NEO_3 = NEO_ARR[2][NEO_3C], NEO_4 = NEO_ARR[3][NEO_4C];
  NEO_V(3, NEO_1);
  if (NEO_1 == 'B' && NEO_2 == 'R' && NEO_3 == 'G' && NEO_4 == 'O') {
    digitalWrite(OUT, HIGH);
    BUT_C = 0;
  } else {
    digitalWrite(OUT, LOW);
  }
}

void NEO_V(int i, char j) {
  if (j == 'R') strip.setPixelColor(i, 255, 0, 0);
  if (j == 'G') strip.setPixelColor(i, 0, 0, 255);
  if (j == 'B') strip.setPixelColor(i, 0, 255, 0);
  if (j == 'O') strip.setPixelColor(i, 255, 0, 39);
  if (j == 'X') strip.setPixelColor(i, 0, 0, 0);
}

void RESET() {
  NEO_1C = 0, NEO_2C = 0, NEO_3C = 0, NEO_4C = 0;
  for (int i = 0; i = 10; i++) NEO_V(i, 'X');
  strip.show();
  BUT_C = 1;
}
