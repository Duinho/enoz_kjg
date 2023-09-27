int choice = 0;


#define OUT A4  // 숫자 표시 회로판의 A0, A1 핀에 연결
#define IN A5   // 숫자 표시 회로판의 A2, A3 핀에 연결


#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
#include <avr/power.h>
#endif

Adafruit_NeoPixel strip(16, 8, NEO_GRB + NEO_KHZ800);

char NEO_1 = "", NEO_2 = "", NEO_3 = "", NEO_4 = "";

int NEO_1C = 0, NEO_2C = 0, NEO_3C = 0, NEO_4C = 0;

int BUT_1 = A0, BUT_2 = A1, BUT_3 = A2, BUT_4 = A3;

int BUT_C = 0;

const char NEO_ARR[4][8] = {
  { 'X', 'R', 'G', 'B', 'O', 'R', 'G', 'O' },  // G
  { 'X', 'B', 'O', 'G', 'R', 'O', 'B', 'G' },  // O
  { 'X', 'O', 'R', 'O', 'B', 'G', 'R', 'B' },  // R
  { 'X', 'G', 'B', 'R', 'G', 'B', 'O', 'R' },  // B
};

void setup() {
#if defined(__AVR_ATtiny85__) && (F_CPU == 16000000)  // 네오픽셀 설정
  clock_prescale_set(clock_div_1);
#endif
  strip.begin();  // 네오픽셀 선언
  strip.clear();
  strip.show();
  Serial.begin(9600);
  pinMode(13, OUTPUT);
  pinMode(BUT_1, INPUT_PULLUP);
  pinMode(BUT_2, INPUT_PULLUP);
  pinMode(BUT_3, INPUT_PULLUP);
  pinMode(BUT_4, INPUT_PULLUP);
  BUT_C = 1;
}

void loop() {
  if (1) { //if (!digitalRead(IN)) {
    BUTTON_C();
    NEO_C();
  } else {
    RESET();
  }
}

void BUTTON_C() {
  if (BUT_C) {
    if (!digitalRead(BUT_1)) {
      NEO_1C++;
      if (NEO_1C == 8) NEO_1C = 0;
      for (int i = 0; i < 4; i++) {
        NEO_V(i, NEO_ARR[0][NEO_1C]);
      }
      strip.show();
      delay(200);
      while (!digitalRead(BUT_1)) delay(5);
    }
    if (!digitalRead(BUT_2)) {
      NEO_2C++;
      if (NEO_2C == 8) NEO_2C = 0;
      for (int i = 4; i < 8; i++) {
        NEO_V(i, NEO_ARR[1][NEO_2C]);
      }
      strip.show();
      delay(200);
      while (!digitalRead(BUT_2)) delay(5);
    }
    if (!digitalRead(BUT_3)) {
      NEO_3C++;
      if (NEO_3C == 8) NEO_3C = 0;
      for (int i = 8; i < 12; i++) {
        NEO_V(i, NEO_ARR[2][NEO_3C]);
      }
      strip.show();
      delay(200);
      while (!digitalRead(BUT_3)) delay(5);
    }
    if (!digitalRead(BUT_4)) {
      NEO_4C++;
      if (NEO_4C == 8) NEO_4C = 0;
      for (int i = 12; i < 16; i++) {
        NEO_V(i, NEO_ARR[3][NEO_4C]);
      }
      strip.show();
      delay(200);
      while (!digitalRead(BUT_4)) delay(5);
    }
  }
}

void NEO_C() {
  NEO_1 = NEO_ARR[0][NEO_1C], NEO_2 = NEO_ARR[1][NEO_2C], NEO_3 = NEO_ARR[2][NEO_3C], NEO_4 = NEO_ARR[3][NEO_4C];
  if (NEO_1 == 'G' && NEO_2 == 'O' && NEO_3 == 'R' && NEO_4 == 'B') {
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
  if (j == 'O') strip.setPixelColor(i, 250, 0, 30);
  if (j == 'X') strip.setPixelColor(i, 0, 0, 0);
}

void RESET() {
  NEO_1C = 0, NEO_2C = 0, NEO_3C = 0, NEO_4C = 0;
  for (int i = 0; i < 16; i++) NEO_V(i, 'X');
  strip.show();
  BUT_C = 1;
}
