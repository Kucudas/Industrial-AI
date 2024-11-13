import os
import cv2
import json

# 경로 설정
image_path = r'data_conversion\coco_data\image'
label_path = r'data_conversion\coco\label'
output_dir = r'data_conversion\cvImage'

# 이미지 파일과 라벨 파일 목록 가져오기 (확장자 .jpg와 .json)
image_files = sorted([f for f in os.listdir(image_path) if f.endswith('.jpg')])
label_files = sorted([f for f in os.listdir(label_path) if f.endswith('.json')])

# 이미지와 라벨 파일 갯수가 일치하는지 확인
if len(image_files) != len(label_files):
    print("Error: 이미지 파일과 라벨 파일의 개수가 일치하지 않습니다.")
else:

    # 파일들을 반복 처리
    for image_file, label_file in zip(image_files, label_files):
        # 확장자를 제외한 파일명 추출 (이미지와 라벨 파일이 같은 이름이어야 함)
        filename_image = os.path.splitext(image_file)[0]
        filename_label = os.path.splitext(label_file)[0]

        # 이미지 파일명과 라벨 파일명이 같은지 확인
        if filename_image != filename_label:
            print(f"Error: 파일명 불일치 {filename_image} != {filename_label}")
            continue

        # 파일 경로 설정
        image_filepath = os.path.join(image_path, image_file)
        label_filepath = os.path.join(label_path, label_file)
        output_filepath = os.path.join(output_dir, filename_image + '_keypoints.jpg')

        # 이미지 불러오기
        image = cv2.imread(image_filepath)

        # 라벨 파일에서 좌표 및 스켈레톤 정보를 불러오기
        with open(label_filepath, 'r') as f:
            label_data = json.load(f)

        # annotations 정보 가져오기
        annotations = label_data['annotations'][0]
        keypoints = annotations['keypoints']
        category_id = annotations['category_id']

        # 카테고리에서 스켈레톤 정보 가져오기
        category_info = next(cat for cat in label_data['categories'] if cat['id'] == category_id)
        skeleton = category_info['skeleton']

        # 키포인트를 2개씩 읽어서 (X, Y) 좌표 리스트로 변환
        keypoints_xy = [(keypoints[i], keypoints[i + 1]) for i in range(0, len(keypoints), 3)]
        
        # 모든 키포인트를 시각화 (가시성 무시)
        for point in keypoints_xy:
            cv2.circle(image, point, 5, (255, 255, 0), -1)  # 하늘색 점 그리기

        # 스켈레톤 연결 그리기
        for connection in skeleton:
            start_idx, end_idx = connection
            start_point = keypoints_xy[start_idx - 1]  # 인덱스는 1부터 시작하므로 -1
            end_point = keypoints_xy[end_idx - 1]
            cv2.line(image, start_point, end_point, (255, 255, 0), 2)  # 하늘색 선 그리기

        # 결과 이미지 저장
        cv2.imwrite(output_filepath, image)

        print(f"Keypoints visualized and saved at: {output_filepath}")