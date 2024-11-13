import os
import cv2
import matplotlib.pyplot as plt


def load_data_from_file(file_path):
    with open(file_path, 'r') as file:
        data = file.read().strip()  # 파일의 내용을 읽고, 앞뒤 공백 제거
        data_list = data.split()  # 공백을 기준으로 데이터를 분리하여 리스트로 변환
        data_list = [float(x) for x in data_list]  # 리스트의 문자열을 실수(float)로 변환
    return data_list


# 이미지 경로 설정
image_path = r'dataset/images/train/livestock_pig_keypoints_000001.jpg'  # 여기에 이미지 파일 경로를 입력하세요.
image = cv2.imread(image_path)

# 주석 데이터 (cx, cy, w, h, 뒤에 keypoints (px, py))
ann_path = r'dataset/labels/train/livestock_pig_keypoints_000001.txt'
annotations = load_data_from_file(ann_path)

# 주석 데이터에서 keypoints(px, py) 추출
keypoints = annotations[5:]  # class id, cx, cy, w, h는 생략

# 이미지의 가로 세로 크기 얻기
height, width, _ = image.shape

# keypoints를 (px, py) 좌표로 변환
points = []
for i in range(0, len(keypoints), 3):  # 3씩 증가하여 z 값을 건너뜀
    px = keypoints[i] * width
    py = keypoints[i+1] * height
    points.append((int(px), int(py)))

# skeleton 정보를 바탕으로 연결
skeleton = [
    [1, 2], [1, 3], [1, 4], [4, 5], [5, 6], [4, 7], [7, 8], [4, 9],
    [9, 10], [10, 11], [9, 12], [12, 13], [9, 14]
]

# skeleton에 따라 keypoints 연결
for connection in skeleton:
    pt1 = points[connection[0] - 1]  # index는 0부터 시작하므로 -1
    pt2 = points[connection[1] - 1]
    cv2.line(image, pt1, pt2, (251, 237, 150), 2)  # #fbed96 색상으로 연결

# keypoints에 원 그리기
for point in points:
    cv2.circle(image, point, 1, (247, 112, 98), -1)

# 결과 저장 경로 설정
save_dir = 'openCV_result'
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# 결과 파일명 설정
output_image_path = os.path.join(save_dir, 'livestock_pig_keypoints_000001_result.jpg')

# 결과 이미지를 저장
cv2.imwrite(output_image_path, image)

# BGR을 RGB로 변환하여 Matplotlib로 표시
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# 이미지와 키포인트 시각화
plt.imshow(image_rgb)
plt.axis('off')  # 축을 숨김
plt.show()