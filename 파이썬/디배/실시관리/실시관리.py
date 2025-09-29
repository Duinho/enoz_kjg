# pip install pandas openpyxl

import pandas as pd
import re
import os
from collections import defaultdict

def process_teachers(filename="실시관리.xlsx", sheet_name="실시관리"):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, filename)

    # 시트 읽기 (2행부터 컬럼명이므로 header=1)
    df = pd.read_excel(input_path, sheet_name=sheet_name, header=1)

    region_map = {
        "대전광역시": "대전",
        "세종특별자치시": "세종",
        "충청남도": "충남",
        "충청북도": "충북",
    }

    # (region, role, name) → {"추가": x, "불참": y}
    results = defaultdict(lambda: {"추가": 0, "불참": 0})
    dated_results = []

    for _, row in df.iterrows():
        region = row.get("관리지역")
        note = str(row.get("비고"))
        hours = row.get("총교육시간")
        edu_id = row.get("교육실시ID")  # B열

        if pd.isna(note) or not isinstance(note, str):
            continue
        if pd.isna(hours):
            continue

        region_short = region_map.get(region, str(region))

        # -------------------------------
        # 날짜 포함 패턴 (예: 9/13 추가 - 보조강사 김소연)
        # -------------------------------
        def handle_date_match(m):
            date, action, role, names = m.groups()
            for name in names.replace(" ", "").split(","):
                if name:
                    dated_results.append(
                        {
                            "교육실시ID": edu_id,
                            "지역": region_short,
                            "강사유형": role,
                            "이름": name,
                            "날짜": date,
                            "참여상태": action,
                        }
                    )
            return ""

        note_clean = re.sub(
            r"(\d{1,2}/\d{1,2})\s*(추가|불참)\s*-\s*(강사|보조강사)\s*([가-힣, ]+)",
            handle_date_match,
            note,
        )

        # -------------------------------
        # 일반 패턴 (합산 대상)
        # -------------------------------
        normal_matches = re.finditer(
            r"(추가|불참)\s*-\s*(강사|보조강사)\s*([가-힣, ]+)", note_clean
        )
        for m in normal_matches:
            action, role, names = m.groups()
            for name in names.split(","):
                name = name.strip()
                if not name:
                    continue
                if action == "추가":
                    results[(region_short, role, name)]["추가"] += hours
                else:
                    results[(region_short, role, name)]["불참"] += hours

    # -------------------------------
    # 합산 결과 DataFrame
    # -------------------------------
    df_results = pd.DataFrame(
        [
            (region, role, name, vals["추가"], vals["불참"], vals["추가"] - vals["불참"])
            for (region, role, name), vals in results.items()
        ],
        columns=["지역", "강사유형", "이름", "추가", "불참", "합산결과"],
    )
    df_results.insert(0, "NO.", range(1, len(df_results) + 1))

    # -------------------------------
    # 날짜별 결과 DataFrame
    # -------------------------------
    df_dated = pd.DataFrame(
        dated_results,
        columns=["교육실시ID", "지역", "강사유형", "이름", "날짜", "참여상태"]
    )
    df_dated.insert(0, "NO.", range(1, len(df_dated) + 1))

    # -------------------------------
    # 엑셀 저장
    # -------------------------------
    output_path = os.path.join(base_dir, "실시관리_결과.xlsx")
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df_results.to_excel(writer, sheet_name="합산 결과", index=False)
        df_dated.to_excel(writer, sheet_name="날짜별 결과", index=False)

    print(f"저장 완료: {output_path}")
    os.startfile(output_path)  # Windows 전용: 자동 실행


if __name__ == "__main__":
    process_teachers()
