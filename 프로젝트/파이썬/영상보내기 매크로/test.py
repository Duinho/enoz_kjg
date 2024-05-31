
# 테스트
date_string = '2024년 5월 31일 수요일'
if '월' in date_string or '수' in date_string:
    sheet_name = '출석부(월/수)'
elif '화' in date_string or '목' in date_string:
    sheet_name = '출석부(화/목)'
print(sheet_name)  # 출력: 출석부(월/수)
