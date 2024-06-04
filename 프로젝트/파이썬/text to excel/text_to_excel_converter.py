import pandas as pd
import os

def convert_text_to_excel(input_file_name, output_file_name):
    # 파일을 열고 각 줄을 읽습니다.
    with open(input_file_name, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # 각 줄을 '	' 기호로 분리하여 리스트로 만듭니다. 불필요한 공백과 줄바꿈은 제거합니다.
    data = [line.strip().split('	') for line in lines if line.strip()]

    # 데이터의 구조를 확인하기 위해 각 줄의 내용과 열 수를 출력합니다.
    for i, row in enumerate(data):
        print(f'Row {i}: {row} -> Columns: {len(row)}')

    # 첫 번째 행은 제목이므로 무시하고, 두 번째 행을 열 이름으로 사용합니다.
    if len(data) > 1:
        df = pd.DataFrame(data[2:], columns=data[1])  # 두 번째 행을 열 이름으로 사용하고 데이터는 그 다음 행부터 시작
        # 생성된 데이터프레임을 엑셀 파일로 저장합니다.
        df.to_excel(output_file_name, index=False)
    else:
        print("No data to process.")

# 예시 사용 방법
convert_text_to_excel('11111.txt', 'output2.xlsx')
