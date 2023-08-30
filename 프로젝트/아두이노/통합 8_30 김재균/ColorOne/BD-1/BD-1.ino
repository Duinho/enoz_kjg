// 2023년 8월 28일 김재균 수정

#define OUT_WIRE A4  // 숫자 표시 회로판의 A0, A1 핀에 연결
#define INPUT_1 A5   // 숫자 표시 회로판의 A2, A3 핀에 연결

const int BTN[4] = { A2, A0, A3, A1 };  // 버튼과 연결되는 아두이노 핀
const int RGB_LED[4][3] = {
  { 2, 3, 4 },
  { 5, 6, 7 },
  { 8, 9, 10 },
  { 11, 12, 13 },
};


int count[4] = { 0, 0, 0, 0 };  // 네 개의 버튼의 눌린 회수 표시,
int pass[4] = { 0, 0, 0, 0 };   // 각 버튼이눌린 회수 기록, 7번 눌리면 다시 처음으로 동작 반복
int choice = 3;                 // 컬러 회로 보드 번호 설정
int btn_c = 0;                  // 정답을 맞추면 더이상 버튼 제어가 되지 않도록 하는 변수 0이면 버튼 제어가능 1이면 버튼제어 불가능

void setup() {
  Serial.begin(9600);
  pinMode(OUT_WIRE, OUTPUT);                                  // 컬러 코드가 맞는지 상태 출력할 핀 설정
  pinMode(INPUT_1, INPUT);                                    // 숫자 표시 회로로부터 컬러코드 리셋신호를 받을 핀 설정
  for (int i = 0; i < 4; i++) pinMode(BTN[i], INPUT_PULLUP);  // 버튼 신호 입력핀 설정, PULLUP은 아두이노 내부 저항 사용 설정
  for (int i = 0; i < 4; i++) {
    for (int j = 0; j < 3; j++) pinMode(RGB_LED[i][j], OUTPUT);  // RGB LED 신호 출력핀 설정
  }
  for (int i = 0; i < 4; i++) {
    for (int j = 0; j < 3; j++) digitalWrite(RGB_LED[i][j], HIGH);  // 컬러 코드 RGB 신호 초기 설정
  }
  digitalWrite(OUT_WIRE, LOW);  // 컬러 코드 초기화 신호(컬러 코드가 맞춰지지 않은 상태) 출력
}


void loop() {
  if (digitalRead(INPUT_1)) {  // 리셋 신호가 들어오면
    reset();                   // 리셋
  } else {                     // 리셋 신호가 아니라면
    read_btn();                // 버튼 값 읽기
    // read_serial();              // 버튼 연결 없이 디버깅 할 때 사용
  }
}


void read_btn() {  // 버튼 값을 읽습니다.
  if (!btn_c) {    // 버튼 제어 변수가 0이면
    for (int i = 0; i < 4; i++) {
      if (!digitalRead(BTN[i])) {  // 버튼이 눌렸을 때 GND와 연결되어 LOW 신호로 입력
        count[i]++;
        if (count[i] >= 7) count[i] = 0;  // 버튼이 7회 눌린 이후로는 처음과 같이 동작함, 카운트 초기화
        select_led(i, count[i]);
        check_complete();                       // 네 버튼의 색이 다 맞춰졌는지 확인
        delay(200);                             // 버튼 오류 방지 딜레이
        while (!digitalRead(BTN[i])) delay(5);  // 누르고 있으면 코드가 넘어가지 않고 멈춤
      }
    }
    Serial.print(pass[0]);
    Serial.print(pass[1]);
    Serial.print(pass[2]);
    Serial.println(pass[3]);
  }
}


void reset() {                     // 리셋
  digitalWrite(OUT_WIRE, LOW);     // 전광판으로 신호를 보냄 OFF
  while (digitalRead(INPUT_1)) {}  //리셋 신호가 끝날 때까지 대기
  for (int i = 0; i < 4; i++) {
    for (int j = 0; j < 3; j++) digitalWrite(RGB_LED[i][j], HIGH);
  }
  for (int i = 0; i < 4; i++) count[i] = 0;
  for (int i = 0; i < 4; i++) pass[i] = 0;
  btn_c = 0;  // 버튼 제어가 가능하게 바꿈
}


void check_complete() {
  if (pass[0] && pass[1] && pass[2] && pass[3]) {  // 네개의 버튼의 색이 모두 맞으면
    digitalWrite(OUT_WIRE, HIGH);                  // 전광판으로 신호를 보냄 ON
    btn_c = 1;                                     // 버튼 제어 불가능하게 바꿈
  } else {
    digitalWrite(OUT_WIRE, LOW);
  }
}



void read_serial() {  // 버튼이 연결되어 있지 않을 때 테스트를 위한 코드 a, b. c, d 키를 누를 때 마다 해당 위치의 LED의 RGB 컬러  켜지는 지 확인 할 것
  if (Serial.available()) {
    char data = Serial.read();
    if (data == 'a') Serial.println(data);
    if (data == 'a') {
      count[0]++;
      if (count[0] >= 7) count[0] = 0;
      select_led(0, (count[0] % 3));
      Serial.print("COUNT[0] : ");
      Serial.println(count[0]);
    } else if (data == 'b') {
      count[1]++;
      if (count[1] >= 7) count[1] = 0;
      select_led(1, (count[1] % 3));
      Serial.print("COUNT[1] : ");
      Serial.println(count[1]);
    } else if (data == 'c') {
      count[2]++;
      if (count[2] >= 7) count[2] = 0;
      select_led(2, (count[2] % 3));
      Serial.print("COUNT[2] : ");
      Serial.println(count[2]);
    } else if (data == 'd') {
      count[3]++;
      if (count[3] >= 7) count[3] = 0;
      select_led(3, (count[3] % 3));
      Serial.print("COUNT[3] : ");
      Serial.println(count[3]);
    }
    check_complete();
  }
}



void select_led(int order, int num) {
  // led 출력:order는 버튼 순서, num은 그 버튼이 눌린 회수 pass[] 는 각 버튼에 연결된 컬러 코드가 맞는지 체크, 맞으면 1, 다르면 0
  // RGB[order][num]에서 order는 버튼 순서 또는 LED 순서를 나타냄, num은 해당 LED의 컬러 R G B를 나타냄
  for (int j = 0; j < 3; j++) digitalWrite(RGB_LED[order][j], HIGH);  // 누른 버튼에 해당하는 LED 컬러를 일단 초기화
  if (choice == 1) {
    if (num == 1) {
      digitalWrite(RGB_LED[order][0], LOW);  // B-2, R-1, G-3, R-0
      if (order == 0) pass[0] = 0;
      if (order == 1) pass[1] = 0;
      if (order == 2) pass[2] = 1;
      if (order == 3) pass[3] = 0;
    } else if (num == 2) {
      digitalWrite(RGB_LED[order][1], LOW);
      if (order == 0) pass[0] = 1;
      if (order == 1) pass[1] = 1;
      if (order == 2) pass[2] = 0;
      if (order == 3) pass[3] = 1;
    } else if (num == 3) {
      digitalWrite(RGB_LED[order][0], LOW);
      if (order == 0) pass[0] = 0;
      if (order == 1) pass[1] = 0;
      if (order == 2) pass[2] = 1;
      if (order == 3) pass[3] = 0;
    } else if (num == 4) {
      digitalWrite(RGB_LED[order][2], LOW);
      if (order == 0) pass[0] = 0;
      if (order == 1) pass[1] = 0;
      if (order == 2) pass[2] = 0;
      if (order == 3) pass[3] = 0;
    } else if (num == 5) {
      digitalWrite(RGB_LED[order][1], LOW);
      if (order == 0) pass[0] = 1;
      if (order == 1) pass[1] = 1;
      if (order == 2) pass[2] = 0;
      if (order == 3) pass[3] = 1;
    } else if (num == 6) {
      digitalWrite(RGB_LED[order][2], LOW);
      if (order == 0) pass[0] = 0;
      if (order == 1) pass[1] = 0;
      if (order == 2) pass[2] = 0;
      if (order == 3) pass[3] = 0;
    } else if (num == 7) {
      digitalWrite(RGB_LED[order][0], LOW);
      digitalWrite(RGB_LED[order][1], LOW);
      digitalWrite(RGB_LED[order][2], LOW);
    }
  }
  if (choice == 2) {
    if (num == 1) {
      digitalWrite(RGB_LED[order][0], LOW);
      if (order == 0) pass[0] = 0;
      if (order == 1) pass[1] = 0;
      if (order == 2) pass[2] = 0;
      if (order == 3) pass[3] = 0;
    } else if (num == 2) {
      digitalWrite(RGB_LED[order][1], LOW);
      if (order == 0) pass[0] = 1;
      if (order == 1) pass[1] = 1;
      if (order == 2) pass[2] = 0;
      if (order == 3) pass[3] = 0;
    } else if (num == 3) {
      digitalWrite(RGB_LED[order][0], LOW);
      if (order == 0) pass[0] = 0;
      if (order == 1) pass[1] = 0;
      if (order == 2) pass[2] = 0;
      if (order == 3) pass[3] = 0;
    } else if (num == 4) {
      digitalWrite(RGB_LED[order][2], LOW);
      if (order == 0) pass[0] = 0;
      if (order == 1) pass[1] = 0;
      if (order == 2) pass[2] = 1;
      if (order == 3) pass[3] = 1;
    } else if (num == 5) {
      digitalWrite(RGB_LED[order][1], LOW);
      if (order == 0) pass[0] = 1;
      if (order == 1) pass[1] = 1;
      if (order == 2) pass[2] = 0;
      if (order == 3) pass[3] = 0;
    } else if (num == 6) {
      digitalWrite(RGB_LED[order][2], LOW);
      if (order == 0) pass[0] = 0;
      if (order == 1) pass[1] = 0;
      if (order == 2) pass[2] = 1;
      if (order == 3) pass[3] = 1;
    } else if (num == 7) {
      digitalWrite(RGB_LED[order][0], LOW);
      digitalWrite(RGB_LED[order][1], LOW);
      digitalWrite(RGB_LED[order][2], LOW);
    }
  }
  if (choice == 3) {
    if (num == 1) {
      digitalWrite(RGB_LED[order][0], LOW);
      if (order == 2) pass[2] = 0;
      if (order == 1) pass[1] = 0;
      if (order == 3) pass[3] = 0;
      if (order == 0) pass[0] = 1;
    } else if (num == 2) {
      digitalWrite(RGB_LED[order][1], LOW);
      if (order == 2) pass[2] = 0;
      if (order == 1) pass[1] = 1;
      if (order == 3) pass[3] = 0;
      if (order == 0) pass[0] = 0;
    } else if (num == 3) {
      digitalWrite(RGB_LED[order][0], LOW);
      if (order == 2) pass[2] = 0;
      if (order == 1) pass[1] = 0;
      if (order == 3) pass[3] = 0;
      if (order == 0) pass[0] = 1;
    } else if (num == 4) {
      digitalWrite(RGB_LED[order][2], LOW);
      if (order == 2) pass[2] = 1;
      if (order == 1) pass[1] = 0;
      if (order == 3) pass[3] = 1;
      if (order == 0) pass[0] = 0;
    } else if (num == 5) {
      digitalWrite(RGB_LED[order][1], LOW);
      if (order == 2) pass[2] = 0;
      if (order == 1) pass[1] = 1;
      if (order == 3) pass[3] = 0;
      if (order == 0) pass[0] = 0;
    } else if (num == 6) {
      digitalWrite(RGB_LED[order][2], LOW);
      if (order == 2) pass[2] = 1;
      if (order == 1) pass[1] = 0;
      if (order == 3) pass[3] = 1;
      if (order == 0) pass[0] = 0;
    } else if (num == 7) {
      digitalWrite(RGB_LED[order][0], LOW);
      digitalWrite(RGB_LED[order][1], LOW);
      digitalWrite(RGB_LED[order][2], LOW);
    }
  }
  if (choice == 4) {
    if (num == 1) {
      digitalWrite(RGB_LED[order][0], LOW);  // B-2, R-1, G-3, R-0
      if (order == 3) pass[1] = 0;
      if (order == 0) pass[2] = 0;
      if (order == 2) pass[3] = 0;
      if (order == 1) pass[0] = 0;
    } else if (num == 2) {
      Serial.print("num =");
      Serial.println(num);
      digitalWrite(RGB_LED[order][1], LOW);
      if (order == 3) pass[1] = 0;
      if (order == 0) pass[2] = 0;
      if (order == 2) pass[3] = 1;
      if (order == 1) pass[0] = 1;
    } else if (num == 3) {
      Serial.print("num =");
      Serial.println(num);
      digitalWrite(RGB_LED[order][0], LOW);
      if (order == 3) pass[1] = 0;
      if (order == 0) pass[2] = 0;
      if (order == 2) pass[3] = 1;
      if (order == 1) pass[0] = 0;
    } else if (num == 4) {
      digitalWrite(RGB_LED[order][2], LOW);
      if (order == 3) pass[1] = 1;
      if (order == 0) pass[2] = 1;
      if (order == 2) pass[3] = 0;
      if (order == 1) pass[0] = 0;
    } else if (num == 5) {
      digitalWrite(RGB_LED[order][1], LOW);
      if (order == 3) pass[1] = 0;
      if (order == 0) pass[2] = 0;
      if (order == 2) pass[3] = 1;
      if (order == 1) pass[0] = 1;
    } else if (num == 6) {
      digitalWrite(RGB_LED[order][2], LOW);
      if (order == 3) pass[1] = 1;
      if (order == 0) pass[2] = 1;
      if (order == 2) pass[3] = 0;
      if (order == 1) pass[0] = 0;
    } else if (num == 7) {
      digitalWrite(RGB_LED[order][0], LOW);
      digitalWrite(RGB_LED[order][1], LOW);
      digitalWrite(RGB_LED[order][2], LOW);
    }
  }
}
