import openai
import sys
import json

# API 키 설정
openai.api_key = "api_key"

def load_text_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        return text
    except Exception as e:
        print(json.dumps({"error": f"Failed to read file: {str(e)}"}), file=sys.stderr)
        sys.exit(1)

def call_openai_api(text_content):
    prompt = f"""
        다음 텍스트 파일을 분석하여 주요 관심사와 '기타' 항목을 포함한 5개 카테고리로 명사를 분류해 주세요.
        - 각 카테고리는 명확하게 정의된 주제를 포함해야 합니다. 카테고리 명은 명사 단어 하나로 표현해주세요.
        - 명사와 복합명사 이외의 단어나 문장은 포함하지 마세요.
        - 중복된 명사는 한 번만 출력합니다.
        - 주요 관심사는 분야로 설명해주세요.
        - 주요 관심사와 카테고리 분류는 명확하게 구분해 주세요.
        - 카테고리 분류 시 각 카테고리별 분류된 단어가 분석한 텍스트 파일에 몇 개 있었는지 count를 항목을 추가해주세요. 이 때 count는 텍스트 파일에 있는 단어 중 해당되는 모든 단어를 집계하는 것으로 중복 가능.
        - 분석 및 분류 결과를 JSON 형식으로 출력해 주세요.
        - 출력 형식은 아래와 같아야 합니다. 주요 관심사는 단어를 나열하는 형태로 출력해주세요.

        출력 형식
        주요 관심사:

        카테고리 분류: 
            카테고리 명: 단어, ...
            count: n

        분석 대상 텍스트: {text_content}
        """

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            messages=[
                {"role": "system", "content": "당신은 텍스트를 분석하고 명사들을 5개 카테고리로 분류하며 주요 관심사를 추출하는 역할을 합니다."},
                {"role": "user", "content": prompt}
            ]
        )
        analysisResult = response.choices[0].message.content
        return analysisResult
    except Exception as e:
        print(json.dumps({"error": f"Failed to send prompt: {str(e)}"}), file=sys.stderr)
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No file path provided as argument"}), file=sys.stderr)
        sys.exit(1)

    # 파일 경로 받기
    file_path = sys.argv[1]

    # 텍스트 파일 읽기
    text_content = load_text_file(file_path)

    # OpenAI API 호출 및 결과 출력
    result = call_openai_api(text_content)
    print(result)

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    main()