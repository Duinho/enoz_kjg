from datetime import datetime, timedelta
import pytz

# 한국 시간대 설정
kst = pytz.timezone('Asia/Seoul')
now = datetime.now(kst)
yesterday = now - timedelta(1)
month = yesterday.month  # 월 (앞에 0을 제거한 형태)
day = yesterday.day  # 일
weekday_dict = {
    'Monday': '월',
    'Tuesday': '화',
    'Wednesday': '수',
    'Thursday': '목',
    'Friday': '금',
    'Saturday': '토',
    'Sunday': '일'
}
weekday_eng = yesterday.strftime('%A')
weekday_kor = weekday_dict[weekday_eng]
formatted_date = f"{month}/{day}"

print(f"어제 날짜: {formatted_date}({weekday_kor})")
if weekday_kor == '월' or weekday_kor == '수' :
    요일 = '월수'
elif weekday_kor == '화' or weekday_kor == '목' :
    요일 = '화목'
print(요일)