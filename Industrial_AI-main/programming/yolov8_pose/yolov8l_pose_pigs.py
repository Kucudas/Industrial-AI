from ultralytics import YOLO

# 사전 학습된 YOLOv8 포즈 모델 로드
model = YOLO('yolov8l-pose.pt')  # YOLOv8m-pose 모델 사용

model.train(
    data='pose_data.yaml',
    epochs=300,           # Epochs를 150으로 증가하여 추가적인 학습 진행
    imgsz=640,            # 이미지 크기
    batch=32,              # 배치 크기
    name='pig_pose_model_l',  # 새로운 학습 세션 이름
    device=0,             # GPU 사용
    optimizer='AdamW',    # AdamW 옵티마이저 사용
    lr0=0.0001,           # 초기 학습률
    weight_decay=0.001,   # Weight Decay
    augment=True          # 데이터 증강 활성화
)

# 학습 후 검증
metrics = model.val()

print("Bounding Box mAP50:", metrics.box.map50)
print("Bounding Box mAP50-95:", metrics.box.map)
print("Pose mAP50:", metrics.pose.map50)
print("Pose mAP50-95:", metrics.pose.map)