import asyncio
import openpyxl
import os
from docx import Document
from docx.shared import RGBColor
import win32com.client as win32


result = 0

async def 엑셀(반):
    global result
    # 엑셀 파일 경로 설정 (이 부분은 변경하지 않음)
    desktop_path = os.path.dirname(os.path.abspath(__file__))
    excel_file = os.path.join(desktop_path, '가라추가.xlsx')

    # 엑셀 파일 열기 (이 부분은 변경하지 않음)
    wb = openpyxl.load_workbook(excel_file)
    sheet = wb.active

    column_name = chr(64 + 반)
    column_values = []
    for cell in sheet[column_name]:
        value = cell.value
        column_values.append(value + "[출]")

    result = ", " + ", ".join(column_values)

    print(f"반 {반}의 결과: {result}")

    wb.close()

async def 파일_탐색_및_수정():
    global result
    # 코드가 있는 폴더 경로 설정
    현재_폴더 = os.path.dirname(os.path.abspath(__file__))

    for 반 in range(1, 4):
        폴더_경로 = os.path.join(현재_폴더, str(반))

        if os.path.exists(폴더_경로):
            await 엑셀(반)
            await 워드_수정(폴더_경로, result)  # result 값을 전달


async def 워드_수정(폴더_경로, result):
    print('워드 수정 입장')
    for 파일명 in os.listdir(폴더_경로):
        if 파일명.endswith(".docx"):  # .docx 파일인 경우에만 처리
            워드_파일_경로 = os.path.join(폴더_경로, 파일명)
            print(f'{파일명} 워드 찾기')

            doc = Document(워드_파일_경로)

            # 워드 파일 내 "출결현황" 칸 오른쪽에 result 값을 추가
            for table in doc.tables:
                for row in table.rows:
                    for i, cell in enumerate(row.cells):
                        if cell.text == "출결현황" and i + 1 < len(row.cells):
                            next_cell = row.cells[i + 1]  # 다음 셀 선택
                            next_cell.text = next_cell.text + result  # 다음 셀에 result 추가
                        if "[결]" in cell.text:
                            cell.text = cell.text.replace("[결]", "[출]")
                        if "[-]" in cell.text:
                            cell.text = cell.text.replace("[-]", "[출]")
                        if "[출]" in cell.text:
                            for paragraph in cell.paragraphs:
                                # 원래 단락의 텍스트를 저장
                                original_text = paragraph.text
                                # 원래 단락의 텍스트를 지웁니다
                                paragraph.clear()
                                # "[출]" 문자열을 찾아 파란색으로 바꿉니다
                                index = 0
                                while index < len(original_text):
                                    start_index = original_text.find("[출]", index)
                                    if start_index != -1:
                                        # "[출]" 문자열 전의 텍스트를 추가
                                        paragraph.add_run(original_text[index:start_index])
                                        # 파란색 "[출]" 문자열을 추가
                                        run = paragraph.add_run("[출]")
                                        run.font.color.rgb = RGBColor(0x00, 0x00, 0xFF)
                                        index = start_index + len("[출]")
                                    else:
                                        # 남은 텍스트를 추가
                                        paragraph.add_run(original_text[index:])
                                        break

            # 수정한 워드 파일 저장
            doc.save(워드_파일_경로)




async def 변환_및_파일_수정():
    # 코드가 있는 폴더 경로 설정
    현재_폴더 = os.path.dirname(os.path.abspath(__file__))

    for 반 in range(1, 4):
        폴더_경로 = os.path.join(현재_폴더, str(반))

        if os.path.exists(폴더_경로):
            await 엑셀(반)
            
            # .doc 파일을 .docx로 변환
            for 파일명 in os.listdir(폴더_경로):
                if 파일명.endswith(".doc"):
                    원본_파일_경로 = os.path.join(폴더_경로, 파일명)
                    변환된_파일_경로 = os.path.join(폴더_경로, 파일명 + "x")

                    # .doc를 .docx로 변환
                    word = win32.gencache.EnsureDispatch("Word.Application")
                    doc = word.Documents.Open(원본_파일_경로)
                    doc.SaveAs(변환된_파일_경로, FileFormat=16)
                    doc.Close()
                    
                    # 원본 .doc 파일 삭제
                    os.remove(원본_파일_경로)

            await 워드_수정(폴더_경로, result)  # result 값을 전달

async def 동작():
    await 변환_및_파일_수정()

asyncio.run(동작())