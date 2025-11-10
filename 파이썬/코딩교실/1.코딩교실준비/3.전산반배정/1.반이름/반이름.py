# 라이브러리 설치를 위해 터미널에 아래의 pip 명령어 입력
#  pip install pandas openpyxl

import os
import pandas as pd
from openpyxl import load_workbook

# 지금 코드 파일이 있는 위치를 저장 (스크립트 파일의 디렉토리)
폴더경로 = os.path.dirname(os.path.abspath(__file__))

# 엑셀 파일 경로 설정
excel_file_path = os.path.join(폴더경로, '출석부아이디.xlsx')

if os.path.exists(excel_file_path):    
    try:
        xls = pd.ExcelFile(excel_file_path)        
        전체현황_df = pd.read_excel(xls, '전체현황', header=None)  # 전체현황 시트를 전체현황_df에 저장
        def 처리_및_저장(sheet_name):
            현재시트_df = pd.read_excel(xls, sheet_name, header=None)

            # F부터 K까지와 G부터 L까지 비교 (F = 6번째 열, G = 7번째 열 ...)
            for index, row in 현재시트_df.iterrows():
                # 전체현황 시트의 F-K 값이 현재시트의 G-L 값과 일치하는지 확인 (열 번호 사용)
                match = 전체현황_df[
                    (전체현황_df.iloc[:, 3] == row.iloc[5]) & 
                    #(전체현황_df.iloc[:, 5] == row.iloc[6]) &  # F열과 G열 비교
                    #(전체현황_df.iloc[:, 6] == row.iloc[7]) &  # G열과 H열 비교
                    (전체현황_df.iloc[:, 7] == row.iloc[8]) &  # H열과 I열 비교
                    #(전체현황_df.iloc[:, 8] == row.iloc[9]) &  # I열과 J열 비교
                    #(전체현황_df.iloc[:, 9] == row.iloc[10]) & # J열과 K열 비교
                    (전체현황_df.iloc[:, 10] == row.iloc[11]) # K열과 L열 비교
                ]

                # 일치하는 행이 있을 경우 현재시트의 E값을 전체현황 E값으로 변경
                if not match.empty:
                    현재시트_df.at[index, 4] = match.iloc[0, 4]  # E열(5번째 열)을 업데이트

            # 기존 출석부아이디_결과.xlsx 파일이 있으면 열기, 없으면 새로 생성
            modified_excel_file_path = os.path.join(폴더경로, '출석부아이디_결과.xlsx')
            if os.path.exists(modified_excel_file_path):
                # 기존 파일에 시트 추가하기
                with pd.ExcelWriter(modified_excel_file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                    현재시트_df.to_excel(writer, sheet_name=sheet_name, index=False, header=False)
            else:
                # 새로운 파일로 저장
                with pd.ExcelWriter(modified_excel_file_path, engine='openpyxl') as writer:
                    현재시트_df.to_excel(writer, sheet_name=sheet_name, index=False, header=False)

        # '출석부(월수)' 처리 및 저장
        처리_및_저장('출석부(월수)')

        # '출석부(화목)' 처리 및 저장
        처리_및_저장('출석부(화목)')

    except Exception as e:
        print(f"엑셀 파일 처리 중 오류가 발생했습니다: {e}")
else:
    print(f"'{excel_file_path}' 파일을 찾을 수 없습니다.")