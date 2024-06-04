//2023/08/28 김재균 수정

// A0, A1은 컬러 코드 회로판에서 색코드가 다 맞춰지면 받는 색깔이 다 맞춰졌다는 신호
// A2, A3은 일정 시간이 지.난 후 컬러 코드  판으로 색깔을 초기화 하라고 보내는 신호

#define SET_INPUT_1 A0  // A0, A1은 컬러 코드가 세팅 되었다는 신호를 받는 입력 핀
#define SET_INPUT_2 A1  // 컬러 코드 회로판의 A4 핀과 연결
#define OUT_1 A2        // A2,A3는 컬러 코드를 리셋하라는 신호를 보내는 출력핀
#define OUT_2 A3        // 컬러 코드 회로판의 A5번 핀과 연결

// D7, D8, D12, D13은 숫자 표시 회로에서 각 수를 제어하는 신호를 출력하는 핀
// HIGH 이면 릴레이를 OFF, LOW 이면 릴레이를 ON(연결된 숫자 LED도 ON) 시킴
// 2113과 1142  두수를 표시하는 각 회로판의 정확한 제어는 약간 다름

// 공통된 제어는 ----표시 제어는 7번 핀으로 하고 있음

const int D13 = 13;
const int D12 = 12;
const int D8 = 8;
const int D7 = 7;
int set1 = 0, set2 = 0;
int cnt = 0, sc = 0;


void setup() {
  Serial.begin(9600);
  pinMode(SET_INPUT_1, INPUT);  // 정답값 받아오는 핀
  pinMode(SET_INPUT_2, INPUT);
  pinMode(OUT_1, OUTPUT);  // 초기화 명령 핀
  pinMode(OUT_2, OUTPUT);
  pinMode(D13, OUTPUT);  // LED 제어
  pinMode(D12, OUTPUT);
  pinMode(D8, OUTPUT);
  pinMode(D7, OUTPUT);
  print_();  // ---- 출력
}


void loop() {
  d(10000);                   // 딜레이 함수
  if (sc) print_num();        // 정답이라면 숫자 출력
  set1 = 0, set2 = 0;         // set 초기화
  digitalWrite(OUT_1, HIGH);  // 보드들 초기화 명령
  digitalWrite(OUT_2, HIGH);
  delay(500);
  if (sc) delay(9500);  // 정답이라면 10초 지속
  sc = 0;               // 정답을 변수를 초기화 하고
  cnt = 1;              // 초기화 명령을 위한 변수

  if (cnt) {                   // ---- 코드 실행
    print_();                  // 함수 출력
    digitalWrite(OUT_1, LOW);  // 보드들 초기화 취소
    digitalWrite(OUT_2, LOW);
    cnt = 0;  // 한 번만 실행하도록
    delay(3000);
  }
}


void print_num() {
  //1142 또는 2113 수를 표시하는 함수
  digitalWrite(D13, LOW);  // 2자 표시
  digitalWrite(D12, LOW);  // 가운데 11 표시
  digitalWrite(D8, LOW);   // 3자 표시
  digitalWrite(D7, HIGH);  // 11의 초기 - 표시 지우기
}


void print_() {
  // 초기에 ---- 로 초기화 된 상태를 표시
  digitalWrite(D13, HIGH);  // 2자 끄기
  digitalWrite(D12, HIGH);  // 가운데 11 끄기
  digitalWrite(D8, HIGH);   // 3자 끄기
  digitalWrite(D7, LOW);    // - 표시
}

void d(int i) {                       // 상황에 따라 딜레이를 실행시키는 함수
  for (int j = 0; j < i; j++) {       // i 값 만큼 반복하기
    set1 = digitalRead(SET_INPUT_1);  // 정답 값 받아오기
    set2 = digitalRead(SET_INPUT_2);
    delay(1);                   // 1ms만큼 지연
    if (!set1 && !set2) j = 0;  // 1번과 2번 둘다 정답이 아니라면 시간이 흐르지 않음(하나라도 정답이면 흐름)
    if (set1 && set2) {         // 둘다 정답이라면
      sc = 1;                   // 정답을 알리고
      j = 1000000;              // for문을 빠져나감
    }
  }
}
