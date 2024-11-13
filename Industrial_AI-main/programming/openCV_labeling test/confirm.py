import cv2
import numpy as np
import os

# 두 이미지 파일 경로
image1_path = r'data_conversion\json_livestock_pig_keypoints_000001.jpg'
image2_path = r'data_conversion\text_livestock_pig_keypoints_000001.jpg'

# 결과 이미지를 저장할 폴더 경로
output_dir = r'data_conversion\image'

# 이미지 로드
image1 = cv2.imread(image1_path)
image2 = cv2.imread(image2_path)

# 이미지 크기 확인 (두 이미지가 동일한 크기여야 함)
if image1.shape != image2.shape:
    print("Images have different sizes and cannot be compared directly.")
else:
    # 두 이미지를 흑백으로 변환
    gray_image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    gray_image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

    # 두 이미지를 비교하여 차이점 계산
    difference = cv2.absdiff(gray_image1, gray_image2)

    # 수치적 차이 계산 (차이의 총합)
    sum_difference = np.sum(difference)
    print(f"Total difference (sum of absolute differences): {sum_difference}")

    # 차이점이 있는 부분을 강조
    _, thresh = cv2.threshold(difference, 30, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 강조된 차이점을 원으로 표시
    for contour in contours:
        (x, y), radius = cv2.minEnclosingCircle(contour)
        center = (int(x), int(y))
        radius = int(radius)
        cv2.circle(image1, center, radius, (0, 255, 0), 2)  # 차이점 강조

    # 결과 파일 경로 설정
    output_filepath1 = os.path.join(output_dir, 'highlighted_difference_image1.jpg')
    output_diff_path = os.path.join(output_dir, 'highlighted_difference.jpg')

    # 차이점 시각화
    cv2.imshow('Difference Highlight', difference)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # 결과를 저장
    cv2.imwrite(output_filepath1, image1)
    cv2.imwrite(output_diff_path, difference)

    print(f"Results saved to: {output_filepath1}, {output_diff_path}")