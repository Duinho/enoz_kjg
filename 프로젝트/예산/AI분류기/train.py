from ultralytics import YOLO

# 모델을 로드하세요.
model = YOLO('yolov8n.yaml')  # YAML에서 새 모델 구축

# 모델을 훈련합니다.
results = model.train(data='C:/Users/enoz00/Desktop/seosanAI.v2i.yolov8/data.yaml', epochs=100, imgsz=640, batch_size=16)
