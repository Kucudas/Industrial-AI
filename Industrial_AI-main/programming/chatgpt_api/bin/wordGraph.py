import openai
import sys
import os
import re
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
import datetime
import json

# API 키 설정
openai.api_key = "api_key"

try:
    raw_input = sys.stdin.buffer.read().decode('utf-8')
    top_words_30 = json.loads(raw_input)
except Exception as e:
    print(json.dumps({"error": f"Failed to load input: {str(e)}"}))
    sys.exit(1)

word_list = [word[0] for word in top_words_30]

prompt = f"다음 단어들을 건강, 생활, 날씨, 지역, 기타 이렇게 5개의 카테고리로 분류하세요: {word_list}"

try:
    response = openai.chat.completions.create(
    model="gpt-4",
    temperature=0,
    messages=[
        {"role": "system", "content": "당신은 단어를 5개의 카테고리로 분류하는 역할을 합니다."}, 
        {"role": "user", "content": prompt}
    ]
)

    categories = response.choices[0].message.content

    # Node.js로 출력
    print(json.dumps({"categories": categories}))

    # 카테고리 추출: 응답에서 카테고리별 단어들을 추출
    categories_dict = {}
    category_pattern = r"(\w+): \[(.*?)\]"
    matches = re.findall(category_pattern, categories)

    for match in matches:
        category_name = match[0]  # 카테고리 이름
        words = re.findall(r"'(.*?)'", match[1])  # 단어 리스트 추출
        categories_dict[category_name] = words

    # 각 카테고리의 단어 빈도수 합계를 계산
    category_counts = {category: 0 for category in categories_dict}

    # top_words_30에서 각 단어의 빈도수를 가져와 카테고리에 합산
    for word, count in top_words_30:
        for category, words in categories_dict.items():
            if word in words:
                category_counts[category] += count

    # 카테고리별 총 단어 빈도수 계산
    total_count = sum(category_counts.values())

    # 퍼센트 계산
    category_percentages = {category: (count / total_count) * 100 for category, count in category_counts.items()}

    # 파이차트 그리기
    labels = list(category_percentages.keys())
    sizes = list(category_percentages.values())

    # 한글 폰트 설정
    font_path = "public/vendor/fontawesome-free/font/NanumGothic.ttf"
    font_prop = font_manager.FontProperties(fname=font_path)
    rc('font', family=font_prop.get_name())

    # 파이 차트 설정
    explode = [0.05] * len(labels)
    colors = ['#ff9999', '#ffc000', '#8fd9b6', '#d395d0', '#66b3ff']

    # 퍼센트 표시 함수
    def autopct_func(pct):
        return ('%.1f%%' % pct) if pct > 0 else ''

    # 파이차트 그리기
    plt.figure(figsize=(8, 8))
    plt.pie(sizes, labels=labels, autopct='%.1f%%', startangle=260, counterclock=False,
            explode=explode, shadow=True, colors=colors,
            textprops={'fontproperties': font_prop, 'fontsize': 15})
    
    # 퍼센트 폰트 사이즈 조정
    for text in plt.gca().texts:
        if '%' in text.get_text():
            text.set_fontsize(10)

    # 한글 폰트를 사용하는 제목 설정
    plt.title('카테고리 비율 현황', fontproperties=font_prop, fontsize=20, weight='bold')

    # 현재 날짜를 YYYYMMDD 형식으로 가져오기
    current_date = datetime.datetime.now().strftime('%Y%m%d')

    # 저장 경로 지정
    save_dir = "repo/chart"
    os.makedirs(save_dir, exist_ok=True)  # 폴더가 없으면 생성
    save_path = os.path.join(save_dir, f"{current_date}_chart.png")

    # 차트를 이미지 파일로 저장
    plt.savefig(save_path)

    # 파이 차트 보여주기
    # plt.show()

except Exception as e:
    print(e)