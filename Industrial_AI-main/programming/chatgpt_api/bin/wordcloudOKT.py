from wordcloud import WordCloud
import matplotlib.pyplot as plt
from konlpy.tag import Okt
from collections import Counter
import sys
import json
import os
import datetime
import numpy as np
from PIL import Image

# 표준출력에서 UTF-8로 인코딩된 출력이 되도록 설정
sys.stdout.reconfigure(encoding='utf-8')

def generate_wordcloud(text, output_path):
  # KoNLPy의 Okt를 사용하여 텍스트 토큰화
  okt = Okt()

  nouns = okt.nouns(text)

  # 불용어 리스트를 txt 파일에서 읽어오기
  stopword_file_path = 'repo/text/stopword.txt'
  with open(stopword_file_path, 'r', encoding='utf-8') as f:
    stopwords = f.read().splitlines()

  # 한 글자 단어 및 불용어 제거
  filtered_words = [word for word in nouns if len(word) > 1 and word not in stopwords]

  # 토큰 계산
  token_counts = Counter(filtered_words)

  # 가장 많이 언급된 상위 10개 단어 추출
  top_10_words = token_counts.most_common(10)

  top_30_words = token_counts.most_common(30)

  # 이미지 경로
  cloud_image_path = 'public/images/cloud.png'

  # 구름 모양의 마스크 이미지 로드 및 변환
  mask = np.array(Image.open(cloud_image_path))

  # 워드 클라우드 생성
  wordcloud = WordCloud(
      font_path= 'public/vendor/fontawesome-free/font/NanumGothic.ttf',
      width=800,
      height=400,
      background_color='white',
      colormap='Set2',
      mask=mask,
      relative_scaling=0.5,
      max_font_size=150
  ).generate_from_frequencies(dict(top_30_words))

  # 현재 날짜로 파일 이름을 지정
  current_date = datetime.datetime.now().strftime('%Y%m%d')
  wordcloud_image_filename = f"{current_date}_wordcloud.png"
  wordcloud_image_path = os.path.join(output_path, wordcloud_image_filename)

  # 워드 클라우드 이미지를 파일로 저장
  wordcloud.to_file(wordcloud_image_path)

  # 상위 10개 단어와 이미지 경로 반환
  result = {
    'top10': top_10_words,
    'top30': top_30_words
  }

  # JSON으로 결과 출력
  print(json.dumps(result, ensure_ascii=False))

  # 워드 클라우드를 화면에 표시
  # plt.figure(figsize=(10, 5))
  # plt.imshow(wordcloud, interpolation='bilinear')
  # plt.axis('off')
  # plt.show()

def main():
  # 텍스트 파일 경로는 첫 번째 인자로 받음
  file_path = sys.argv[1]

  # 텍스트 파일에서 텍스트 읽기
  with open(file_path, 'r', encoding='utf-8') as file:
    text = file.read()

  # 워드클라우드 이미지를 저장할 폴더 경로 설정
  output_path = "repo/wordcloud"

  # 워드 클라우드 생성 및 상위 10개 단어 추출
  generate_wordcloud(text, output_path)

if __name__ == "__main__":
  main()