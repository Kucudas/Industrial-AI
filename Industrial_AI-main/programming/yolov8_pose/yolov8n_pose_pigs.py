from ultralytics import YOLO

# 사전 학습된 YOLOv8 포즈 모델 로드
model = YOLO('yolov8n-pose.pt')

# 학습 실행
model.train(
    data='pose_data.yaml',
    epochs=100,
    imgsz=640, # 이미지 크기
    batch=32,
    name='pig_pose_model', # 학습 세션 이름
    device=0 # GPU
)
