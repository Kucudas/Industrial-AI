import os
import json

# 원본 JSON 파일 경로
input_dir = r""

# 변환된 JSON 파일 저장 디렉토리
output_dir = r"data conversion\coco_val\label"

# 디렉토리 내의 모든 JSON 파일을 순회
for file_name in os.listdir(input_dir):
    if file_name.endswith('.json'):
        # 원본 JSON 파일 경로
        input_file_path = os.path.join(input_dir, file_name)
        
        # 변환된 JSON 파일 경로
        output_file_name = file_name  # 파일 이름을 그대로 사용
        output_file_path = os.path.join(output_dir, output_file_name)
        
        # 원본 JSON 데이터 로드
        with open(input_file_path) as f:
            data = json.load(f)
        
        # 변환된 데이터 구조 생성
        converted_data = {
            "info": {
                "year": "2024",
                "version": "1",
                "description": "Converted to COCO format",
                "contributor": "Custom",
                "url": "",
                "date_created": "2024-09-03T00:00:00+00:00"
            },
            "licenses": [
                {
                    "id": 1,
                    "url": "https://creativecommons.org/publicdomain/zero/1.0/",
                    "name": "Public Domain"
                }
            ],
            "categories": [],
            "images": [],
            "annotations": []
        }

        # 카테고리 추가 - 원본 JSON의 모든 카테고리 정보 그대로 유지
        for cat in data['label_info']['categories']:
            converted_data['categories'].append({
                "id": cat['id'],
                "name": cat['name'],
                "supercategory": cat['supercategory'],
                "keypoints": cat["keypoints_name"],
                "skeleton": cat["skeleton"]
            })

        # 이미지 정보 추가 - 원본 JSON의 이미지를 그대로 가져옴
        image_info = data['label_info']['image']
        converted_data['images'].append({
            "id": 0,  # COCO 포맷에서 이미지 ID는 숫자로 되어 있어야 함
            "license": 1,
            "file_name": image_info['file_name'],
            "height": image_info['height'],
            "width": image_info['width'],
            "farm_name": image_info.get("farm_name", ""),  # 추가 필드: 농장 이름
            "farm_env": image_info.get("farm_env", ""),    # 추가 필드: 농장 환경
            "time": image_info.get("time", ""),            # 추가 필드: 촬영 시간
            "date_captured": "2024-09-03T00:00:00+00:00"
        })

        # annotation 정보 추가
        for idx, ann in enumerate(data['label_info']['annotations']):
            converted_data['annotations'].append({
                "id": idx,  # 고유 ID
                "image_id": 0,  # 이미지 ID는 0
                "category_id": ann['category_id'],
                "bbox": ann['bbox'],  # Bounding Box 정보 그대로
                "area": ann['bbox'][2] * ann['bbox'][3],  # Bounding Box의 면적 (width * height)
                "segmentation": ann.get("segmentation", []),  # segmentation 정보가 있으면 가져오고, 없으면 빈 리스트
                "iscrowd": ann.get("iscrowd", 0),  # crowd 정보가 있으면 가져오고, 없으면 0
                "keypoints": ann["keypoints"],  # keypoints 그대로
                "num_keypoints": len(ann["keypoints"]) // 3  # COCO 포맷에서는 3개씩 (x, y, visibility)
            })

        # 변환된 JSON 데이터 저장
        with open(output_file_path, 'w') as f:
            json.dump(converted_data, f, indent=4)

        print(f"Converted {file_name} and saved to {output_file_path}")