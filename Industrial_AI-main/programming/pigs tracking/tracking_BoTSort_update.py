import cv2
import pandas as pd
import numpy as np
import json
from datetime import datetime
from ultralytics import YOLO
from scipy.spatial.distance import euclidean

# YOLO 모델 로드
model = YOLO('runs/detect/finetune/weights/best.pt')

# 비디오 설정
video_path = "datasets/video/test1.mp4"
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Error1")
    exit()

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

output_path = 'runs/detect/tracking_result/tracking result.mp4'
out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

# 1. 영상 초반 10초 동안 돼지 개체 수 파악
pig_counts = []
frame_count = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret or frame_count >= fps * 10:  # 10초 동안 검출
        break

    results = model.predict(frame, conf=0.5)
    pig_counts.append(len(results[0].boxes.data))
    frame_count += 1

cap.release()  # 검출 완료 후 비디오 종료

total_pigs = int(np.median(pig_counts))  # 돼지 개체 수를 중앙값으로 결정
print(f"총 돼지 개체 수: {total_pigs}")

# 비디오 재오픈
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("Error2")
    exit()

# ID 관리 변수 초기화
track_data = []
id_pool = set(range(1, total_pigs + 1))  # 사용 가능한 ID
id_mapping = {}  # ReID를 위한 ID 매핑 (track_id -> assigned_id)
id_last_seen = {i: None for i in id_pool}  # 각 ID의 마지막 프레임 기록
missing_ids = set()  # 사라진 돼지 ID 추적

# 2. 객체 추적 및 보완
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    results = model.track(
        frame, 
        persist=True,     
        tracker='botSORT.yaml', 
        conf=0.5,    
        iou=0.4 
    )

    current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
    active_ids = set()  # 현재 프레임에서 활성화된 ID

    for track in results[0].boxes.data:
        track_id, x1, y1, x2, y2, conf = int(track[4]), track[0], track[1], track[2], track[3], track[5]
        x_center = (x1 + x2) / 2
        y_center = (y1 + y2) / 2

        # ID 매핑
        if track_id not in id_mapping:
            if missing_ids:
                # 사라진 ID 중 하나를 재사용
                new_id = missing_ids.pop()
            elif id_pool:
                # 새 ID를 부여
                new_id = id_pool.pop()
            else:
                continue  # ID가 없으면 무시
            id_mapping[track_id] = new_id

        mapped_id = id_mapping[track_id]
        active_ids.add(mapped_id)
        id_last_seen[mapped_id] = current_frame  # 마지막으로 본 프레임 기록

        # 추적 데이터 저장
        track_data.append({
            'frame': int(current_frame),
            'id': int(mapped_id), 
            'x_center': float(x_center), 
            'y_center': float(y_center), 
        })

        # 바운딩 박스와 ID, Class, Confidence 표시
        cv2.rectangle(
            frame,
            (int(x1), int(y1)),
            (int(x2), int(y2)),
            (255, 0, 0),  # 파란색 BBox
            3  # 바운딩 박스 두께
        )
        cv2.putText(
            frame,
            f'pigs id: {mapped_id} {conf:.2f}',
            (int(x1), int(y1) - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,  # 글자 크기
            (255, 0, 0),  # 파란색 글자
            2,  # 글자 두께
            cv2.LINE_AA,
        )

    # 3. 사라진 돼지 ID 추적
    missing_ids.clear()  # 새로 사라진 ID를 업데이트
    for _id in id_pool.union(set(id_last_seen.keys())):
        if _id not in active_ids:
            # 앵글 밖으로 나간 돼지로 간주
            if id_last_seen[_id] is not None and current_frame - id_last_seen[_id] > 1:
                missing_ids.add(_id)

    # 사용 가능한 ID 재확인
    id_pool = id_pool.union(missing_ids) - active_ids

    out.write(frame)

cap.release()
out.release()

# 4. JSON 파일로 좌표 데이터 저장
current_date = datetime.now().strftime("%Y-%m-%d")
json_file_name = f"{current_date}_pigs_tracking_result.json"

with open(json_file_name, 'w') as json_file:
    json.dump(track_data, json_file, indent=4)

# 5. 활동량 분석: 좌표 이동 기반으로 시간 및 거리 계산
print("이동 데이터 분석 중...")
df = pd.DataFrame(track_data)

# ID별 이동 거리와 시간 계산 (실시간 출력 포함)
print("이동 데이터 분석 중...")
activity_data = []
activity_summary = {pig_id: {'total_distance': 0, 'active_time': 0, 'average_speed': 0, 'active_frame_count': 0} for pig_id in range(1, total_pigs + 1)}

for pig_id in range(1, total_pigs + 1):
    pig_data = df[df['id'] == pig_id].sort_values(by='frame')
    for i in range(1, len(pig_data)):
        prev = pig_data.iloc[i - 1]
        curr = pig_data.iloc[i]

        # 이전 및 현재 중심 좌표
        prev_center = (prev['x_center'], prev['y_center'])
        curr_center = (curr['x_center'], curr['y_center'])

        # 이동 거리 계산
        dist = euclidean(prev_center, curr_center)

        # BBox 크기 변화 계산
        prev_bbox_size = abs(prev['x_center'] - prev['y_center'])
        curr_bbox_size = abs(curr['x_center'] - curr['y_center'])
        bbox_change = abs(curr_bbox_size - prev_bbox_size)

        # 조건: 유효한 이동 거리 및 BBox 크기 변화 필터링 (완화된 조건 적용)
        if dist > 3:  # 이동 거리 조건 완화
            time_diff = (curr['frame'] - prev['frame']) / fps
            activity_summary[pig_id]['total_distance'] += dist
            activity_summary[pig_id]['active_time'] += time_diff
            activity_summary[pig_id]['active_frame_count'] += 1

            # 실시간 평균 속도 계산
            speed = dist / time_diff if time_diff > 0 else 0
            activity_summary[pig_id]['average_speed'] += speed

    # 평균 속도 계산
    total_active_frames = activity_summary[pig_id]['active_frame_count']
    if total_active_frames > 0:
        activity_summary[pig_id]['average_speed'] /= total_active_frames

# 실시간 결과 출력
for pig_id, data in activity_summary.items():
    print(f"ID: {pig_id} | Distance: {data['total_distance']:.2f} | Active Time: {data['active_time']:.2f} | Avg Speed: {data['average_speed']:.2f}")

# 최종 데이터 정리 및 저장
activity_data = [
    {
        'id': pig_id,
        'total_distance': data['total_distance'],
        'active_time': data['active_time'],
        'average_speed': data['average_speed']
    }
    for pig_id, data in activity_summary.items()
]

# 결과 저장
activity_df = pd.DataFrame(activity_data)
activity_df.to_csv('pig_activity_analysis_filtered.csv', index=False)