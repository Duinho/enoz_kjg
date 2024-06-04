/* 
네오픽셀은 12개씩 5줄을 사용함. 
편의를 위해 5줄을 사용했지만 1줄로 쭉 사용해도 됨. 단, 반응 속도가 느릴 수도 있고 고장이 자주 나므로 추천하지는 않음.

네오픽셀 +와 아두이노 vin에 외부 전력을 +를 연결 함.
네오픽셀, 아두이노, 외부 전력의 gnd끼리 연결 
네오픽셀 DI부분은 1번 스트립은 D8, 2번은 D9, 3번은 D10, 4번은 D11, 5번은 D12에 연결함.

숫자를 해당하는 네오픽셀끼리 거리를 두기 위해 중간을 절단한 후 배선하여 사용하거나 빈 공간도 네오픽셀로 쭉 연결한 후 필요한 부분만 사용해도 됨.
절단하여 사용할 시 DI와 DO 사이 동판 부분을 잘라야하며, 이전 네오픽셀의 DO부분을 DI부분에 연결하여 사용하면 됨.

A2 - 1번 아두이노의 A4
A3 - 1번 아두이노의 A5
A4 - 2번 아두이노의 A4
A5 - 2번 아두이노의 A5
*/

#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
#include <avr/power.h>
#endif


int BRIGHTNESS = 30;  // LED 밝기

// 네오픽셀 (개수, 연결한 핀, 모드 설정) 개수와 핀은 필요에 따라 수정해도 됨.
Adafruit_NeoPixel strip1(12, 8, NEO_GRBW + NEO_KHZ800);
Adafruit_NeoPixel strip2(12, 9, NEO_GRBW + NEO_KHZ800);
Adafruit_NeoPixel strip3(12, 10, NEO_GRBW + NEO_KHZ800);
Adafruit_NeoPixel strip4(12, 11, NEO_GRBW + NEO_KHZ800);
Adafruit_NeoPixel strip5(12, 12, NEO_GRBW + NEO_KHZ800);


int IN1 = A2, OUT1 = A3, IN2 = A4, OUT2 = A5;  // 와이어 통신을 위한 핀

void setup() {
#if defined(__AVR_ATtiny85__) && (F_CPU == 16000000)  // 네오픽셀 설정
  clock_prescale_set(clock_div_1);
#endif
  strip1.begin();  // 네오픽셀 선언
  strip2.begin();
  strip3.begin();
  strip4.begin();
  strip5.begin();
  strip1.show();  // 네오픽셀 출력 (아무것도 설정되지 않아 꺼짐)
  strip2.show();
  strip3.show();
  strip4.show();
  strip5.show();
  pinMode(OUT, OUTPUT);  // 핀모드 선언
  pinMode(IN1, INPUT);
  pinMode(IN2, INPUT);
  int c = 2;  // 전력 효율을 위한 한 번만 키도록 설정할 때 확인을 위한 변수
}

void loop() {
  if (digitalRead(IN1) == 1 && digitalRead(IN2)) {  // 둘 다에게 정답 신호가 온다면
    if (c != 1) {                                   // c 값이 1이 아니면
      segment(1);                                   // 네오픽셀 1번 동작 출력
      c = 1;                                        // c 값을 1로 바꾸어 반복 x
      digitalWrite(OUT1, HIGH);                     // 정답이라고 신호 보내기
      digitalWrite(OUT2, HIGH);
      delay(5000);  // 5초간 지연 (시간을 바꾸면 됨)
    }
  } else {
    if (c != 0) {  // c 값이 0이 아니면(정답을 맞추지 않은 평상시라면)
      segment(0);  // 네오픽셀 0번 동작 출력
      c = 0;       // c 값을 0로 바꾸어 반복 x
    }
  }
  digitalWrite(OUT1, LOW);  // 정답이 아니라고 신호 보내기
  digitalWrite(OUT2, LOW);
}


// 숫자 출력에 필요한 네오픽셀 값을 설정하는 함수. i 값에 0을 입력하면 ----를 1을 입력하면 1142를 2를 입력하면 2113을 출력함.
void segment(int i) {
  strip1.clear();  // 네오픽셀 초기화
  strip2.clear();
  strip3.clear();
  strip4.clear();
  strip5.clear();
  switch (i) {
    case 0:  // 0을 입력 받으면 ---- 를 출력
      for (int k = 0; k < 12; k++) {
        strip3.setPixelColor(k, 0, 0, 0, BRIGHTNESS);
      }
      break;
    case 1:  // 0을 입력 받으면 1142를 출력
      strip1.setPixelColor(2, 0, 0, 0, BRIGHTNESS);
      strip1.setPixelColor(5, 0, 0, 0, BRIGHTNESS);
      strip1.setPixelColor(6, 0, 0, 0, BRIGHTNESS);
      strip1.setPixelColor(8, 0, 0, 0, BRIGHTNESS);
      strip1.setPixelColor(9, 0, 0, 0, BRIGHTNESS);
      strip1.setPixelColor(10, 0, 0, 0, BRIGHTNESS);
      strip1.setPixelColor(11, 0, 0, 0, BRIGHTNESS);

      strip2.setPixelColor(2, 0, 0, 0, BRIGHTNESS);
      strip2.setPixelColor(5, 0, 0, 0, BRIGHTNESS);
      strip2.setPixelColor(6, 0, 0, 0, BRIGHTNESS);
      strip2.setPixelColor(8, 0, 0, 0, BRIGHTNESS);
      strip2.setPixelColor(11, 0, 0, 0, BRIGHTNESS);

      strip3.setPixelColor(2, 0, 0, 0, BRIGHTNESS);
      strip3.setPixelColor(5, 0, 0, 0, BRIGHTNESS);
      strip3.setPixelColor(6, 0, 0, 0, BRIGHTNESS);
      strip3.setPixelColor(7, 0, 0, 0, BRIGHTNESS);
      strip3.setPixelColor(8, 0, 0, 0, BRIGHTNESS);
      strip3.setPixelColor(9, 0, 0, 0, BRIGHTNESS);
      strip3.setPixelColor(10, 0, 0, 0, BRIGHTNESS);
      strip3.setPixelColor(11, 0, 0, 0, BRIGHTNESS);

      strip4.setPixelColor(2, 0, 0, 0, BRIGHTNESS);
      strip4.setPixelColor(5, 0, 0, 0, BRIGHTNESS);
      strip4.setPixelColor(8, 0, 0, 0, BRIGHTNESS);
      strip4.setPixelColor(9, 0, 0, 0, BRIGHTNESS);

      strip5.setPixelColor(2, 0, 0, 0, BRIGHTNESS);
      strip5.setPixelColor(5, 0, 0, 0, BRIGHTNESS);
      strip5.setPixelColor(8, 0, 0, 0, BRIGHTNESS);
      strip5.setPixelColor(9, 0, 0, 0, BRIGHTNESS);
      strip5.setPixelColor(10, 0, 0, 0, BRIGHTNESS);
      strip5.setPixelColor(11, 0, 0, 0, BRIGHTNESS);
      break;

    case 2:  // 0을 입력 받으면 2113를 출력
      strip1.setPixelColor(0, 0, 0, 0, BRIGHTNESS);
      strip1.setPixelColor(1, 0, 0, 0, BRIGHTNESS);
      strip1.setPixelColor(2, 0, 0, 0, BRIGHTNESS);
      strip1.setPixelColor(5, 0, 0, 0, BRIGHTNESS);
      strip1.setPixelColor(8, 0, 0, 0, BRIGHTNESS);
      strip1.setPixelColor(9, 0, 0, 0, BRIGHTNESS);
      strip1.setPixelColor(10, 0, 0, 0, BRIGHTNESS);
      strip1.setPixelColor(11, 0, 0, 0, BRIGHTNESS);

      strip2.setPixelColor(2, 0, 0, 0, BRIGHTNESS);
      strip2.setPixelColor(5, 0, 0, 0, BRIGHTNESS);
      strip2.setPixelColor(8, 0, 0, 0, BRIGHTNESS);
      strip2.setPixelColor(11, 0, 0, 0, BRIGHTNESS);

      strip3.setPixelColor(0, 0, 0, 0, BRIGHTNESS);
      strip3.setPixelColor(1, 0, 0, 0, BRIGHTNESS);
      strip3.setPixelColor(2, 0, 0, 0, BRIGHTNESS);
      strip3.setPixelColor(5, 0, 0, 0, BRIGHTNESS);
      strip3.setPixelColor(8, 0, 0, 0, BRIGHTNESS);
      strip3.setPixelColor(9, 0, 0, 0, BRIGHTNESS);
      strip3.setPixelColor(10, 0, 0, 0, BRIGHTNESS);
      strip3.setPixelColor(11, 0, 0, 0, BRIGHTNESS);

      strip4.setPixelColor(0, 0, 0, 0, BRIGHTNESS);
      strip4.setPixelColor(5, 0, 0, 0, BRIGHTNESS);
      strip4.setPixelColor(8, 0, 0, 0, BRIGHTNESS);
      strip4.setPixelColor(11, 0, 0, 0, BRIGHTNESS);

      strip5.setPixelColor(0, 0, 0, 0, BRIGHTNESS);
      strip5.setPixelColor(1, 0, 0, 0, BRIGHTNESS);
      strip5.setPixelColor(2, 0, 0, 0, BRIGHTNESS);
      strip5.setPixelColor(5, 0, 0, 0, BRIGHTNESS);
      strip5.setPixelColor(8, 0, 0, 0, BRIGHTNESS);
      strip5.setPixelColor(9, 0, 0, 0, BRIGHTNESS);
      strip5.setPixelColor(10, 0, 0, 0, BRIGHTNESS);
      strip5.setPixelColor(11, 0, 0, 0, BRIGHTNESS);
      break;
  }
  strip1.show();  // 설정된 네오픽셀 값 출력
  strip2.show();
  strip3.show();
  strip4.show();
  strip5.show();
}