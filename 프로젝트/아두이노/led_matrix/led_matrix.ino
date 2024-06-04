#include <RGBmatrixPanel.h>

// Most of the signal pins are configurable, but the CLK pin has some
// special constraints. On 8-bit AVR boards it must be on PORTB...
// Pin 11 works on the Arduino Mega. On 32-bit SAMD boards it must be
// on the same PORT as the RGB data pins (D2-D7)...
// Pin 8 works on the Adafruit Metro M0 or Arduino Zero,
// Pin A4 works on the Adafruit Metro M4 (if using the Adafruit RGB
// Matrix Shield, cut trace between CLK pads and run a wire to A4).

#define CLK  11
//#define CLK A4 // USE THIS ON METRO M4 (not M0)
//#define CLK 11 // USE THIS ON ARDUINO MEGA
#define OE   9
#define LAT 10
#define A   A0
#define B   A1
#define C   A2
#define D   A3

RGBmatrixPanel matrix(A, B, C, D, CLK, LAT, OE, false, 64);

void setup() {
  matrix.begin();
  matrix.setTextSize(2);     // size 1 == 8 pixels high
  matrix.setTextWrap(false); // Don't wrap at end of line - will do ourselves

  for (int i = 73; i >= 0; i = i - 5) { // -40은 텍스트가 완전히 화면을 벗어나도록
    matrix.fillScreen(0); // 화면을 지우기 위해 모든 픽셀을 꺼줍니다.
    matrix.setCursor(i, 8); // 텍스트 위치 설정
    matrix.print(F("CLEAR"));
    matrix.swapBuffers(true); // 화면에 텍스트 표시
    delay(500);
  }

}

void loop() {
  matrix.setCursor(3, 8); // 텍스트 위치 설정
  matrix.setTextColor(matrix.Color333(7, 0, 0));
  matrix.print(F("C"));
  matrix.setTextColor(matrix.Color333(0, 7, 0));
  matrix.print(F("L"));
  matrix.setTextColor(matrix.Color333(7, 2, 0));
  matrix.print(F("E"));
  matrix.setTextColor(matrix.Color333(0, 0, 7));
  matrix.print(F("A"));
  matrix.setTextColor(matrix.Color333(7, 7, 7));
  matrix.print(F("R"));
  delay(300);
  
  matrix.setCursor(3, 8);
  matrix.setTextColor(matrix.Color333(7, 7, 7));
  matrix.print(F("C"));
  matrix.setTextColor(matrix.Color333(7, 0, 0));
  matrix.print(F("L"));
  matrix.setTextColor(matrix.Color333(0, 7, 0));
  matrix.print(F("E"));
  matrix.setTextColor(matrix.Color333(7, 2, 0));
  matrix.print(F("A"));
  matrix.setTextColor(matrix.Color333(0, 0, 7));
  matrix.print(F("R"));
  delay(300);
  
  matrix.setCursor(3, 8);
  matrix.setTextColor(matrix.Color333(0, 0, 7));
  matrix.print(F("C"));
  matrix.setTextColor(matrix.Color333(7, 7, 7));
  matrix.print(F("L"));
  matrix.setTextColor(matrix.Color333(7, 0, 0));
  matrix.print(F("E"));
  matrix.setTextColor(matrix.Color333(0, 7, 0));
  matrix.print(F("A"));
  matrix.setTextColor(matrix.Color333(7, 2, 0));
  matrix.print(F("R"));
  delay(300);
  
  matrix.setCursor(3, 8);
  matrix.setTextColor(matrix.Color333(7, 2, 0));
  matrix.print(F("C"));
  matrix.setTextColor(matrix.Color333(0, 0, 7));
  matrix.print(F("L"));
  matrix.setTextColor(matrix.Color333(7, 7, 7));
  matrix.print(F("E"));
  matrix.setTextColor(matrix.Color333(7, 0, 0));
  matrix.print(F("A"));
  matrix.setTextColor(matrix.Color333(0, 7, 0));
  matrix.print(F("R"));
  delay(300);
  
  matrix.setCursor(3, 8);
  matrix.setTextColor(matrix.Color333(0, 7, 0));
  matrix.print(F("C"));
  matrix.setTextColor(matrix.Color333(7, 2, 0));
  matrix.print(F("L"));
  matrix.setTextColor(matrix.Color333(0, 0, 7));
  matrix.print(F("E"));
  matrix.setTextColor(matrix.Color333(7, 7, 7));
  matrix.print(F("A"));
  matrix.setTextColor(matrix.Color333(7, 0, 0));
  matrix.print(F("R"));
  delay(300);
}
