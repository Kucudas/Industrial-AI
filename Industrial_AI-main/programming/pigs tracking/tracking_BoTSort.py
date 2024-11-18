import cv2
from ultralytics import YOLO

model = YOLO('runs/detect/finetune/weights/best.pt')

video_path = "datasets/video/video1.mp4"
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Error")
    exit()

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

output_path = 'runs/detect/tracking_result/original_test.mp4'
out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    results = model.track(
        frame, 
        persist=True,     
        tracker='botsort.yaml', 
        conf=0.5,    
        iou=0.4 
    )

    annotated_frame = results[0].plot()

    out.write(annotated_frame)

# 비디오 자원 해제
cap.release()
out.release()