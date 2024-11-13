import cv2
import os

# 현재 스크립트가 실행되는 디렉터리의 경로
current_dir = os.path.dirname(os.path.abspath(__file__))

# 이미지 파일 경로
image_path = r'data_conversion\train\images'

# 라벨 파일 경로
label_path = r'data_conversion\train\labels'

# 결과 이미지 저장 폴더 경로
output_dir = r'data_conversion\image'

# 경로가 정확한지 확인
print(f"Image path: {image_path}")
print(f"Label path: {label_path}")
print(f"Does the image exist? {os.path.exists(image_path)}")
print(f"Does the label file exist? {os.path.exists(label_path)}")

# 이미지 로드
image = cv2.imread(image_path)

# 이미지 로드 확인
if image is None:
    print(f"Error: Unable to load image at {image_path}. Please check the file path.")
else:
    print(f"Image loaded successfully from {image_path}")

# 나머지 코드 실행은 이미지가 제대로 로드된 경우에만 진행
if image is not None:
    # 결과 이미지를 저장할 폴더가 존재하지 않으면 생성
    os.makedirs(output_dir, exist_ok=True)

    # 클래스 색상 (필요에 따라 색상 변경 가능)
    COLOR = (0, 255, 0)  # 초록색

    # 키포인트 연결 순서 (skeleton)
    skeleton = [
        (0, 1), (0, 2), (0, 3), (3, 4), (4, 5), (3, 6), (6, 7), (3, 8),
        (8, 9), (9, 10), (8, 11), (11, 12), (8, 13)
    ]

    # 라벨 파일 읽기
    with open(label_path, 'r') as file:
        label_data = file.readline().strip().split()

    # 바운딩 박스 및 키포인트 좌표 가져오기
    class_index = int(label_data[0])
    x, y, width, height = map(int, label_data[1:5])

    # 키포인트 추출
    keypoints = []
    for i in range(5, len(label_data), 3):
        px = int(label_data[i])
        py = int(label_data[i + 1])
        visibility = int(label_data[i + 2])
        keypoints.append((px, py, visibility))

    # 바운딩 박스 그리기
    cv2.rectangle(image, (x, y), (x + width, y + height), COLOR, 2)

    # 키포인트 찍기 및 선 연결
    for i, (px, py, visibility) in enumerate(keypoints):
        if visibility > 0:  # 보이는 키포인트만 표시
            cv2.circle(image, (px, py), 5, COLOR, -1)

    # 키포인트 연결하기 (skeleton)
    for i, j in skeleton:
        if keypoints[i][2] > 0 and keypoints[j][2] > 0:  # 두 키포인트 모두 보일 때만 선 연결
            cv2.line(image, (keypoints[i][0], keypoints[i][1]), (keypoints[j][0], keypoints[j][1]), COLOR, 2)

    # 결과 이미지 파일 경로
    output_filepath = os.path.join(output_dir, 'text_livestock_pig_keypoints_000001.jpg')

    # 결과 이미지 저장
    cv2.imwrite(output_filepath, image)

    # 결과 이미지 보기 (선택사항)
    cv2.imshow('Keypoints Visualization', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()