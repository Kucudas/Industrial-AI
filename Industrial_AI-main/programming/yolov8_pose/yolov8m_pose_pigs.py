from ultralytics import YOLO
from torch.optim.lr_scheduler import CosineAnnealingLR

# 사전 학습된 YOLOv8 포즈 모델 로드
model = YOLO('yolov8m-pose.pt')  # YOLOv8m-pose 모델 사용

# Mixed Precision Training을 사용하기 위해 'amp=True' 추가
model.train(
    data='pose_data.yaml',
    epochs=300,           # Epochs 300 유지
    imgsz=640,            # 이미지 크기
    batch=32,             # 배치 크기 32로 설정
    name='pig_pose_m',     # 학습 세션 이름
    device=0,             # GPU 사용
    lr0=0.0001,           # 초기 학습률
    weight_decay=0.001,   # Weight Decay
    augment=True,         # 데이터 증강 활성화
    workers=8,            # 데이터 로딩 최적화 (num_workers=8)
    amp=True              # Mixed Precision Training 활성화
)

# 학습률 스케줄러 적용 (CosineAnnealingLR)
scheduler = CosineAnnealingLR(model.optimizer, T_max=300, eta_min=1e-6)

# 학습 후 검증
metrics = model.val()  # no arguments needed, dataset and settings remembered
metrics.box.map  # map50-95
metrics.box.map50  # map50
metrics.box.map75  # map75
metrics.box.maps  # a list contains map50-95 of each category

print("Bounding Box mAP50:", metrics.box.map50)
print("Bounding Box mAP50-95:", metrics.box.map)
print("Pose mAP50:", metrics.pose.map50)
print("Pose mAP50-95:", metrics.pose.map)