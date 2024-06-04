#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
#include <avr/power.h>
#endif

#define NUMPIXELS 8
Adafruit_NeoPixel pixels0(NUMPIXELS, 0, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel pixels1(NUMPIXELS, 1, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel pixels2(NUMPIXELS, 2, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel pixels3(NUMPIXELS, 3, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel pixels4(NUMPIXELS, 4, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel pixels5(NUMPIXELS, 5, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel pixels6(NUMPIXELS, 6, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel pixels7(NUMPIXELS, 7, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel pixels8(NUMPIXELS, 8, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel pixels9(NUMPIXELS, 9, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel pixels10(NUMPIXELS, 10, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel pixels11(NUMPIXELS, 11, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel pixels12(NUMPIXELS, 12, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel pixels13(NUMPIXELS, 13, NEO_GRB + NEO_KHZ800);


void setup() {
  neo_set();
}

void loop() {
  neo_c(1000);
}

void neo_set() {
#if defined(__AVR_ATtiny85__) && (F_CPU == 16000000)
  clock_prescale_set(clock_div_1);
#endif

  pixels0.begin();
  pixels1.begin();
  pixels2.begin();
  pixels3.begin();
  pixels4.begin();
  pixels5.begin();
  pixels6.begin();
  pixels7.begin();
  pixels8.begin();
  pixels9.begin();
  pixels10.begin();
  pixels11.begin();
  pixels12.begin();
  pixels13.begin();

  pixels0.clear();
  pixels1.clear();
  pixels2.clear();
  pixels3.clear();
  pixels4.clear();
  pixels5.clear();
  pixels6.clear();
  pixels7.clear();
  pixels8.clear();
  pixels9.clear();
  pixels10.clear();
  pixels11.clear();
  pixels12.clear();
  pixels13.clear();
}

void neo_c(int d) {
  for (int i = 0; i < 8; i++) {
    pixels7.setPixelColor(i, 50, 50, 0);
    pixels8.setPixelColor(i, 50, 50, 0);
    pixels9.setPixelColor(i, 50, 50, 0);
    pixels10.setPixelColor(i, 50, 50, 0);
    delay(10);
  }

  for (int i = 0; i < 8; i++) {
    pixels11.setPixelColor(i, 50, 50, 50);
    pixels12.setPixelColor(i, 50, 50, 50);
    pixels13.setPixelColor(i, 50, 50, 50);
    delay(10);
  }

  for (int i = 0; i < 8; i++) {
    pixels0.setPixelColor(i, 50, 0, 10);
    pixels1.setPixelColor(i, 50, 0, 10);
    pixels2.setPixelColor(i, 50, 0, 10);
    pixels3.setPixelColor(i, 50, 0, 10);
    delay(10);
  }

  for (int i = 0; i < 8; i++) {
    pixels4.setPixelColor(i, 50, 6, 0);
    pixels5.setPixelColor(i, 50, 6, 0);
    pixels6.setPixelColor(i, 50, 6, 0);
    delay(10);
  }
  pixels0.show();
  pixels1.show();
  pixels2.show();
  pixels3.show();
  pixels4.show();
  pixels5.show();
  pixels6.show();
  pixels7.show();
  pixels8.show();
  pixels9.show();
  pixels10.show();
  pixels11.show();
  pixels12.show();
  pixels13.show();
  delay(d);


  for (int i = 0; i < 8; i++) {
    pixels7.setPixelColor(i, 50, 50, 50);
    pixels8.setPixelColor(i, 50, 50, 50);
    pixels9.setPixelColor(i, 50, 50, 50);
    pixels10.setPixelColor(i, 50, 50, 50);
    delay(10);
  }

  for (int i = 0; i < 8; i++) {
    pixels11.setPixelColor(i, 50, 0, 10);
    pixels12.setPixelColor(i, 50, 0, 10);
    pixels13.setPixelColor(i, 50, 0, 10);
    delay(10);
  }

  for (int i = 0; i < 8; i++) {
    pixels0.setPixelColor(i, 50, 6, 0);
    pixels1.setPixelColor(i, 50, 6, 0);
    pixels2.setPixelColor(i, 50, 6, 0);
    pixels3.setPixelColor(i, 50, 6, 0);
    delay(10);
  }

  for (int i = 0; i < 8; i++) {
    pixels4.setPixelColor(i, 50, 50, 0);
    pixels5.setPixelColor(i, 50, 50, 0);
    pixels6.setPixelColor(i, 50, 50, 0);
    delay(10);
  }

  pixels0.show();
  pixels1.show();
  pixels2.show();
  pixels3.show();
  pixels4.show();
  pixels5.show();
  pixels6.show();
  pixels7.show();
  pixels8.show();
  pixels9.show();
  pixels10.show();
  pixels11.show();
  pixels12.show();
  pixels13.show();
  delay(d);

  for (int i = 0; i < 8; i++) {
    pixels7.setPixelColor(i, 50, 0, 10);
    pixels8.setPixelColor(i, 50, 0, 10);
    pixels9.setPixelColor(i, 50, 0, 10);
    pixels10.setPixelColor(i, 50, 0, 10);
    delay(10);
  }

  for (int i = 0; i < 8; i++) {
    pixels11.setPixelColor(i, 50, 6, 0);
    pixels12.setPixelColor(i, 50, 6, 0);
    pixels13.setPixelColor(i, 50, 6, 0);
    delay(10);
  }

  for (int i = 0; i < 8; i++) {
    pixels0.setPixelColor(i, 50, 50, 0);
    pixels1.setPixelColor(i, 50, 50, 0);
    pixels2.setPixelColor(i, 50, 50, 0);
    pixels3.setPixelColor(i, 50, 50, 0);
    delay(10);
  }

  for (int i = 0; i < 8; i++) {
    pixels4.setPixelColor(i, 50, 50, 50);
    pixels5.setPixelColor(i, 50, 50, 50);
    pixels6.setPixelColor(i, 50, 50, 50);
    delay(10);
  }

  pixels0.show();
  pixels1.show();
  pixels2.show();
  pixels3.show();
  pixels4.show();
  pixels5.show();
  pixels6.show();
  pixels7.show();
  pixels8.show();
  pixels9.show();
  pixels10.show();
  pixels11.show();
  pixels12.show();
  pixels13.show();
  delay(d);

  for (int i = 0; i < 8; i++) {
    pixels7.setPixelColor(i, 50, 6, 0);
    pixels8.setPixelColor(i, 50, 6, 0);
    pixels9.setPixelColor(i, 50, 6, 0);
    pixels10.setPixelColor(i, 50, 6, 0);
    delay(10);
  }

  for (int i = 0; i < 8; i++) {
    pixels11.setPixelColor(i, 50, 50, 0);
    pixels12.setPixelColor(i, 50, 50, 0);
    pixels13.setPixelColor(i, 50, 50, 0);
    delay(10);
  }

  for (int i = 0; i < 8; i++) {
    pixels0.setPixelColor(i, 50, 50, 50);
    pixels1.setPixelColor(i, 50, 50, 50);
    pixels2.setPixelColor(i, 50, 50, 50);
    pixels3.setPixelColor(i, 50, 50, 50);
    delay(10);
  }

  for (int i = 0; i < 8; i++) {
    pixels4.setPixelColor(i, 50, 0, 10);
    pixels5.setPixelColor(i, 50, 0, 10);
    pixels6.setPixelColor(i, 50, 0, 10);
    delay(10);
  }

  pixels0.show();
  pixels1.show();
  pixels2.show();
  pixels3.show();
  pixels4.show();
  pixels5.show();
  pixels6.show();
  pixels7.show();
  pixels8.show();
  pixels9.show();
  pixels10.show();
  pixels11.show();
  pixels12.show();
  pixels13.show();
  delay(d);
}