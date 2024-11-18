from ultralytics import YOLO

model = YOLO('yolov10m.pt')

model.train(
    data='data.yaml',
    epochs=50,
    imgsz=640,
    batch=8,
    name='pig_v10m',
    device=0,
    optimizer='AdamW',
    lr0=0.001,  # 초기 학습률 증가
    weight_decay=0.001,
    augment=True,
    lrf=0.01,
    # patience=10, # 성능 개선이 없을 때 조기 중단
    cos_lr=True 
)

# 학습 후 검증
metrics = model.val()

print("Bounding Box mAP50:", metrics.box.map50)
print("Bounding Box mAP50-95:", metrics.box.map)