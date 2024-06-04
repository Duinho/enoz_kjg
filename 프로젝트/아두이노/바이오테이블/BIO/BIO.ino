/*
네오픽셀은 12개씩 4줄을 사용함.
편의를 위해 5줄을 사용했지만 1줄로 쭉 사용해도 됨. 단, 반응 속도가 느릴 수도 있고 고장이 자주 나므로 추천하지는 않음.

네오픽셀 +와 아두이노 vin에 외부 전력을 +를 연결 하고, 네오픽셀, 아두이노, 외부 전력의 gnd끼리도 연결 
네오픽셀 DI부분은 1번 스트립은 D8, 2번은 D9, 3번은 D10, 4번은 D11, 5번은 D12에 연결함.

최대한으로 네오픽셀이나 보드가 고장나지 않도록 전력 효율과 ON/OFF 동작을 최소화하기 위한 코드로 작성함.

A0 = 1번 버튼
A1 = 2번 버튼
A2 = 3번 버튼
A3 = 4번 버튼
A4 = 중앙 아두이노 A2 / A4
A5 = 중앙 아두이노 A3 / A5

*/

#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
#include <avr/power.h>
#endif


int BRIGHTNESS = 30;  // LED 밝기


//  네오픽셀 (개수, 연결한 핀, 모드 설정) 개수와 핀은 필요에 따라 수정해도 됨.
Adafruit_NeoPixel strip1(12, 8, NEO_GRBW + NEO_KHZ800);
Adafruit_NeoPixel strip2(12, 9, NEO_GRBW + NEO_KHZ800);
Adafruit_NeoPixel strip3(12, 10, NEO_GRBW + NEO_KHZ800);
Adafruit_NeoPixel strip4(12, 11, NEO_GRBW + NEO_KHZ800);


int qs = 0, ws = 0, es = 0, rs = 0;  // 네오픽셀의 색깔을 정하는 변수
int qc = 0, wc = 0, ec = 0, rc = 0;  // 버튼이 눌렸는지 확인하기 위한 변수
int q = A0, w = A1, e = A2, r = A3;  // 버튼
int OUT = A4, IN = A5;               // 와이어 통신을 위한 입출력 핀

void setup() {
#if defined(__AVR_ATtiny85__) && (F_CPU == 16000000)  // 네오픽셀 설정
  clock_prescale_set(clock_div_1);
#endif
  strip1.begin();  // 네오픽셀 선언
  strip2.begin();
  strip3.begin();
  strip4.begin();
  strip1.clear();  // 네오픽셀 초기화
  strip2.clear();
  strip3.clear();
  strip4.clear();
  strip1.show();  // 네오픽셀 출력 (아무것도 설정되지 않아 꺼짐)
  strip2.show();
  strip3.show();
  strip4.show();
  pinMode(q, INPUT_PULLUP);  // 아두이노 내부의 풀업 저항 사용
  pinMode(w, INPUT_PULLUP);
  pinMode(e, INPUT_PULLUP);
  pinMode(r, INPUT_PULLUP);
  pinMode(OUT, OUTPUT);  // 핀모드 선언
  pinMode(IN, INPUT);
  digitalWrite(OUT, 0);  // 정답을 맞추지 않았다고 LOW 신호 보내기
  preset();              // preset 함수 실행
}

void loop() {
  if (digitalRead(IN) == 1) {                // 중앙 아두이노에서 HIGH 신호가 오면
    qc = 2, qs = 0, ws = 0, es = 0, rs = 0;  // 네오픽셀 관련 변수 초기화하면서 동작을 멈춤
  } else {                                   // HIGH가 아니라면
    bio();                                   // bio 함수 실행
  }
}

void preset() {  // 버튼을 눌러도 변하지 않는 네오픽셀을 미리 세팅
  strip1.setPixelColor(0, BRIGHTNESS, 0, 0, 0);
  strip1.setPixelColor(1, BRIGHTNESS, 0, 0, 0);
  strip1.setPixelColor(2, BRIGHTNESS, 0, 0, 0);
  strip1.setPixelColor(3, 0, BRIGHTNESS, 0, 0);
  strip1.setPixelColor(4, 0, BRIGHTNESS, 0, 0);

  strip1.setPixelColor(5, 0, 0, BRIGHTNESS, 0);
  strip1.setPixelColor(6, 0, 0, BRIGHTNESS, 0);
  strip1.setPixelColor(7, BRIGHTNESS, BRIGHTNESS / 1.82, 0, 0);
  strip1.setPixelColor(8, BRIGHTNESS, BRIGHTNESS / 1.82, 0, 0);

  strip1.setPixelColor(9, 0, BRIGHTNESS, 0, 0);
  strip1.setPixelColor(10, 0, BRIGHTNESS, 0, 0);
  strip1.setPixelColor(11, BRIGHTNESS, 0, 0, 0);

  strip2.setPixelColor(0, 0, 0, BRIGHTNESS, 0);
  strip2.setPixelColor(1, BRIGHTNESS, BRIGHTNESS / 1.82, 0, 0);
  strip2.setPixelColor(2, BRIGHTNESS, BRIGHTNESS / 1.82, 0, 0);

  strip2.setPixelColor(3, 0, BRIGHTNESS, 0, 0);
  strip2.setPixelColor(4, 0, BRIGHTNESS, 0, 0);
  // 버튼 값에 따라 달라질 5~6번은 따로 코딩

  strip2.setPixelColor(7, 0, 0, BRIGHTNESS, 0);
  strip2.setPixelColor(8, 0, 0, BRIGHTNESS, 0);
  // 버튼 값에 따라 달라질 9~11번은 따로 코딩

  // 버튼 값에 따라 달라질 0~2번은 따로 코딩
  strip3.setPixelColor(3, BRIGHTNESS, 0, 0, 0);
  strip3.setPixelColor(4, BRIGHTNESS, 0, 0, 0);

  strip3.setPixelColor(5, BRIGHTNESS, BRIGHTNESS / 1.82, 0, 0);
  strip3.setPixelColor(6, BRIGHTNESS, BRIGHTNESS / 1.82, 0, 0);
  // 버튼 값에 따라 달라질 7~8번은 따로 코딩

  strip3.setPixelColor(9, BRIGHTNESS, 0, 0, 0);
  strip3.setPixelColor(10, BRIGHTNESS, 0, 0, 0);
  strip3.setPixelColor(11, 0, BRIGHTNESS, 0, 0);

  strip4.setPixelColor(0, BRIGHTNESS, BRIGHTNESS / 1.82, 0, 0);
  strip4.setPixelColor(1, BRIGHTNESS, BRIGHTNESS / 1.82, 0, 0);
  strip4.setPixelColor(2, 0, 0, BRIGHTNESS, 0);

  strip4.setPixelColor(3, BRIGHTNESS, 0, 0, 0);
  strip4.setPixelColor(4, BRIGHTNESS, 0, 0, 0);
  strip4.setPixelColor(5, 0, BRIGHTNESS, 0, 0);
  strip4.setPixelColor(6, 0, BRIGHTNESS, 0, 0);

  strip4.setPixelColor(7, 0, 0, BRIGHTNESS, 0);
  strip4.setPixelColor(8, 0, 0, BRIGHTNESS, 0);
  strip4.setPixelColor(9, BRIGHTNESS, BRIGHTNESS / 1.82, 0, 0);
  strip4.setPixelColor(10, BRIGHTNESS, BRIGHTNESS / 1.82, 0, 0);
  strip4.setPixelColor(11, BRIGHTNESS, BRIGHTNESS / 1.82, 0, 0);

  strip1.show();
  strip2.show();
  strip3.show();
  strip4.show();
}


/*
버튼이 눌려졌는지 확인하고, 누를 때마다 담당하는 변수를 바꾸기 위한 함수

예를 들어 A0에 연결된 1번 버튼을 누른다면 q의 디지털 값이 1이 됨
그러면 while문 조건에 충족되지 않아 qc가 1로 변하게 되고, 버튼을 땔 때까지 반복(다른 동작하지 않음)
버튼을 누르고 있지 않다면 반복이 종료되고, qc가 1이 되었으므로 qs에 1을 더하게 됨. qc가 5가된다면 1로 바꿈
*/

void button_check() {
  while (!digitalRead(q)) {  // q의 디지털 값이 1이 아니라면
    qc = 1;                  // qc를 1로 바꿈
  }
  while (!digitalRead(w)) {
    wc = 1;
  }
  while (!digitalRead(e)) {
    ec = 1;
  }
  while (!digitalRead(r)) {
    rc = 1;
  }

  if (qc == 1) {    // 만약 qc가 1이라면
    qs++;           // qs값에 1을 더함
    if (qs == 5) {  // 만약 qs가 5라면
      qs = 1;       // 1로 바꿈
    }
  }
  if (wc == 1) {
    ws++;
    if (ws == 5) {
      ws = 1;
    }
  }
  if (ec == 1) {
    es++;
    if (es == 5) {
      es = 1;
    }
  }
  if (rc == 1) {
    rs++;
    if (rs == 5) {
      rs = 1;
    }
  }
}

/*
네오픽셀을 button_check 함수로 받아온 변수 값에 따라 색깔 제어하기 위한 함수

예를 들어 A0에 연결된 1번 버튼을 눌렀고, qc와 qs가 1이된 상태로 함수가 실행된 상황이라면
먼저 button_check을 실행하여 버튼을 눌렀는지 확인함. (1번 버튼을 눌러 ac와 as가 1이 됐음.)
qc가 0이 아니라는 것은 버튼을 눌렀던 것이므로 저장된 변수에 따라 네오픽셀 값을 변경 하기 위한 코드를 실행
qs가 1이므로 case 1에 해당하는 코드 실행 qc를 0으로 초기화 하고, 네오픽셀을 설정된 값으로 킴
만약 정답이 맞다면 OUT 변수에 HIGH로 출력 정답이 아니라면 LOW로 출력
*/

void bio() {
  button_check();
  if (qc != 0 || wc != 0 || ec != 0 || rc != 0) {  // 변수들이 0이 아니라면 (4개의 버튼중 하나라도 눌렀다면)
    switch (qs) {                                  // 변수 값에 따른 코드 실행
      case 0:                                      // 불을 끔
        strip2.setPixelColor(5, 0, 0, 0, 0);
        strip2.setPixelColor(6, 0, 0, 0, 0);
        break;
      case 1:  // R
        strip2.setPixelColor(5, BRIGHTNESS, 0, 0, 0);
        strip2.setPixelColor(6, BRIGHTNESS, 0, 0, 0);
        break;
      case 2:  // G
        strip2.setPixelColor(5, 0, BRIGHTNESS, 0, 0);
        strip2.setPixelColor(6, 0, BRIGHTNESS, 0, 0);
        break;
      case 3:  // B
        strip2.setPixelColor(5, 0, 0, BRIGHTNESS, 0);
        strip2.setPixelColor(6, 0, 0, BRIGHTNESS, 0);
        break;
      case 4:  // O
        strip2.setPixelColor(5, BRIGHTNESS, BRIGHTNESS / 1.82, 0, 0);
        strip2.setPixelColor(6, BRIGHTNESS, BRIGHTNESS / 1.82, 0, 0);
        break;
    }
    switch (ws) {
      case 0:
        strip2.setPixelColor(9, 0, 0, 0, 0);
        strip2.setPixelColor(10, 0, 0, 0, 0);
        strip2.setPixelColor(11, 0, 0, 0, 0);
        break;
      case 1:
        strip2.setPixelColor(9, BRIGHTNESS, 0, 0, 0);
        strip2.setPixelColor(10, BRIGHTNESS, 0, 0, 0);
        strip2.setPixelColor(11, BRIGHTNESS, 0, 0, 0);
        break;
      case 2:
        strip2.setPixelColor(9, 0, BRIGHTNESS, 0, 0);
        strip2.setPixelColor(10, 0, BRIGHTNESS, 0, 0);
        strip2.setPixelColor(11, 0, BRIGHTNESS, 0, 0);
        break;
      case 3:
        strip2.setPixelColor(9, 0, 0, BRIGHTNESS, 0);
        strip2.setPixelColor(10, 0, 0, BRIGHTNESS, 0);
        strip2.setPixelColor(11, 0, 0, BRIGHTNESS, 0);
        break;
      case 4:
        strip2.setPixelColor(9, BRIGHTNESS, BRIGHTNESS / 1.82, 0, 0);
        strip2.setPixelColor(10, BRIGHTNESS, BRIGHTNESS / 1.82, 0, 0);
        strip2.setPixelColor(11, BRIGHTNESS, BRIGHTNESS / 1.82, 0, 0);
        break;
    }
    switch (es) {
      case 0:
        strip3.setPixelColor(0, 0, 0, 0, 0);
        strip3.setPixelColor(1, 0, 0, 0, 0);
        strip3.setPixelColor(2, 0, 0, 0, 0);
        break;
      case 1:
        strip3.setPixelColor(0, BRIGHTNESS, 0, 0, 0);
        strip3.setPixelColor(1, BRIGHTNESS, 0, 0, 0);
        strip3.setPixelColor(2, BRIGHTNESS, 0, 0, 0);
        break;
      case 2:
        strip3.setPixelColor(0, 0, BRIGHTNESS, 0, 0);
        strip3.setPixelColor(1, 0, BRIGHTNESS, 0, 0);
        strip3.setPixelColor(2, 0, BRIGHTNESS, 0, 0);
        break;
      case 3:
        strip3.setPixelColor(0, 0, 0, BRIGHTNESS, 0);
        strip3.setPixelColor(1, 0, 0, BRIGHTNESS, 0);
        strip3.setPixelColor(2, 0, 0, BRIGHTNESS, 0);
        break;
      case 4:
        strip3.setPixelColor(0, BRIGHTNESS, BRIGHTNESS / 1.82, 0, 0);
        strip3.setPixelColor(1, BRIGHTNESS, BRIGHTNESS / 1.82, 0, 0);
        strip3.setPixelColor(2, BRIGHTNESS, BRIGHTNESS / 1.82, 0, 0);
        break;
    }
    switch (rs) {
      case 0:
        strip3.setPixelColor(7, 0, 0, 0, 0);
        strip3.setPixelColor(8, 0, 0, 0, 0);
        break;
      case 1:
        strip3.setPixelColor(7, BRIGHTNESS, 0, 0, 0);
        strip3.setPixelColor(8, BRIGHTNESS, 0, 0, 0);
        break;
      case 2:
        strip3.setPixelColor(7, 0, BRIGHTNESS, 0, 0);
        strip3.setPixelColor(8, 0, BRIGHTNESS, 0, 0);
        break;
      case 3:
        strip3.setPixelColor(7, 0, 0, BRIGHTNESS, 0);
        strip3.setPixelColor(8, 0, 0, BRIGHTNESS, 0);
        break;
      case 4:
        strip3.setPixelColor(7, BRIGHTNESS, BRIGHTNESS / 1.82, 0, 0);
        strip3.setPixelColor(8, BRIGHTNESS, BRIGHTNESS / 1.82, 0, 0);
        break;
    }
    qc = 0, wc = 0, ec = 0, rc = 0;  // 버튼 확인 변수 초기화
    strip2.show();                   // 네오픽셀 출력
    strip3.show();

    if (qs == 1 && ws == 4 && es == 2 && rs == 3) {  // 정답이라면
      digitalWrite(OUT, 1);                          // HIGH 값 출력
    } else {
      digitalWrite(OUT, 0);
    }
  }
}