import cv2
from ultralytics import YOLO

CONFIDENCE_THRESHOLD = 0.2 # 인식하는 유사치 비율
GREEN = (0, 255, 0)        
WHITE = (255, 255, 255)

class_list = ['clam', 'crab', 'octopus', 'oyster']   # 바지락, 꽃게, 낙지, 굴

model = YOLO('C:/Users/Admin/Desktop/runs/detect/train5/weights/best.pt')   # 인공지능 모델 경로

cap = cv2.VideoCapture(0)                   # 카메라 기능 켜기q
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640 )      # 카메라 권장 너비 640 / 1920
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480 )     # 카메라 권장 높이 480 / 1080

while True:
    ret, frame = cap.read()
    if not ret:
        break  # 카메라 에러 시 바로 종료

    detection = model(frame)[0]

    clam_detected = False    # 대상 인식 여부를 추적하기 위한 변수
    crab_detected = False
    octopus_detected = False
    oyster_detected = False

    for data in detection.boxes.data.tolist():
        confidence = float(data[4])
        if confidence < CONFIDENCE_THRESHOLD:    # 유사치 비율이 0.2보다 낮다면 아래 코드를 넘김
            continue

        xmin, ymin, xmax, ymax = int(data[0]), int(data[1]), int(data[2]), int(data[3])     # 인식되는 부분에 네모 박스를 침
        label = int(data[5])

        if class_list[label] == 'clam':
            clam_detected = True  
        if class_list[label] == 'crab':
            crab_detected = True  
        if class_list[label] == 'octopus':
            octopus_detected = True  
        if class_list[label] == 'oyster':
            oyster_detected = True  

        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), GREEN, 2)
        cv2.putText(frame, class_list[label] + ' ' + str(round(confidence * 100)) + '%', (xmin, ymin), cv2.FONT_ITALIC, 1, WHITE, 2)

    if clam_detected:
        print("clam detected!")  # 대상이 인식되면 메시지 출력
    if crab_detected:
        print("crab detected!")     
    if octopus_detected:
        print("octopus detected!")  
    if oyster_detected:
        print("oyster detected!")  
    cv2.imshow('frame', frame)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()