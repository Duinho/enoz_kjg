#pip install pandas openpyxl xlrd

import pandas as pd
import random
import calendar
from datetime import datetime
import os

from 이름생성기 import generate_name  # 이름 생성 모듈

# 만족도 점수 확률 분포
def generate_score():
    r = random.random()
    if r < 0.95:
        return 5
    elif r < 0.985:
        return 4
    else:
        return 3

# 랜덤 날짜/시간 생성
def random_datetime(year, month, exclude_days, include_days):
    while True:
        day = random.randint(1, calendar.monthrange(year, month)[1])
        weekday = datetime(year, month, day).weekday()
        # 조건: 평일만, 제외일은 건너뛰기, 포함일은 강제 허용
        if (day not in exclude_days and weekday < 5) or (day in include_days):
            break
    hour = random.randint(9, 16)      # 9시~16시
    minute = random.randint(0, 59)    # 0~59
    second = random.randint(0, 59)    # 0~59
    return datetime(year, month, day, hour, minute, second)

def process_file(input_file="체험존 방명록 양식.xlsx", output_file="체험존 방명록 결과.xlsx"):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, input_file)
    output_path = os.path.join(base_dir, output_file)

    df = pd.read_excel(input_path, header=None)

    # 대상년월
    yearmonth = str(df.iloc[0, 1])  # 예: 2509
    year = 2000 + int(yearmonth[:2])  # 2025
    month = int(yearmonth[2:])        # 9

    # 체험존 리스트 (2행, B열 이후)
    zones = []
    col = 1
    while col < df.shape[1] and not pd.isna(df.iloc[1, col]):
        zones.append((col, str(df.iloc[1, col]).strip()))
        col += 1

    # 결과 파일 작성
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for col_idx, zone_name in zones:
            # 연령대 가중치
            weights = {
                "10대": int(df.iloc[2, col_idx]),
                "20대": int(df.iloc[3, col_idx]),
                "30대": int(df.iloc[4, col_idx]),
                "40대": int(df.iloc[5, col_idx]),
                "50대": int(df.iloc[6, col_idx]),
                "60대": int(df.iloc[7, col_idx]),
                "70대 이상": int(df.iloc[8, col_idx]),
            }

            # 제외일, 추가일, 반복횟수
            exclude_days = []
            include_days = []
            if not pd.isna(df.iloc[9, col_idx]):
                exclude_days = [int(x) for x in str(df.iloc[9, col_idx]).split(",") if x.strip()]
            if not pd.isna(df.iloc[10, col_idx]):
                include_days = [int(x) for x in str(df.iloc[10, col_idx]).split(",") if x.strip()]
            repeat_count = int(df.iloc[11, col_idx])

            # 연령대 리스트 (가중치 반영)
            age_groups = list(weights.keys())
            age_weights = list(weights.values())

            records = []
            for _ in range(repeat_count):
                age_group = random.choices(age_groups, weights=age_weights, k=1)[0]
                gender = random.choice(["남자", "여자"])
                name = generate_name(age_group, gender)
                timestamp = random_datetime(year, month, exclude_days, include_days).strftime("%Y-%m-%d %H:%M:%S")

                # 만족도 점수 4문항
                scores = [generate_score() for _ in range(4)]

                # 개인정보 동의 + 기본정보 + 점수4개 + 자유기재(빈칸)
                records.append([
                    timestamp,
                    "네, 동의합니다.",  # 개인정보 동의
                    zone_name,          # Q1
                    name,               # Q2
                    gender,             # Q3
                    age_group           # Q4
                ] + scores + [""])      # Q5~Q8

            # DataFrame 생성 (11개 컬럼)
            result_df = pd.DataFrame(records, columns=[
                "타임스탬프",
                "위와 같이 개인정보를 수집·이용 및 제3자 제공에 동의하시는 경우 체크 부탁드립니다.",
                "1. 현재 방문하신 체험존은 어디인가요?",
                "2. 성명을 작성해주세요",
                "3. 성별을 체크해주세요",
                "4. 연령대를 체크해주세요",
                "1. 디지털 기기 체험 환경이 불편없이 준비되어 있다.(체험장비, 네트워크, 시설 접근성 등)",
                "2. 다음에 다른 체험존을 더 체험해보고 싶다.",
                "3. 디지털체험존을 다른 사람에게 소개하고 권유할 의향이 있다.",
                "4. 체험존 가이드가 체험 기기와 활용 방법에 대해 충분한 설명을 해주었다.",
                "5. 기타 남기고 싶으신 말씀이 있다면 자유롭게 적어주세요."
            ])

            # 시트에 작성
            result_df.to_excel(writer, sheet_name=zone_name, index=False)

    os.startfile(output_path)  # Windows 전용

if __name__ == "__main__":
    process_file()
