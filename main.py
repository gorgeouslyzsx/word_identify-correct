import requests
import json
import base64
import urllib
import re
from flask import Flask, request, jsonify

CORRECT_API_KEY = "bALlCpcThGlI9SlQC6ACbxvO"
CORRECT_SECRET_KEY = "VdpiHlLfRM62ScoyuBorTLtZyTBZqMLN"
IDENTIFY_API_KEY = "rTlkww5HQCmyNUkE468a5ZZk"
IDENTIFY_SECRET_KEY = "pfGmaBPblnVEUQsQjWau4HeZfkUxYkKS"
image_path = ""
sentence = []  # 存储句子的列表
ori_word = []  # 存储原始单词的列表
correct_word = []  # 存储纠正后单词的列表
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/ocr', methods=['POST'])
def main():
    global sentence, ori_word, correct_word
    
    url = "https://aip.baidubce.com/rpc/2.0/nlp/v2/text_correction?charset=UTF-8&access_token=" + get_access_token()
    
    text_to_correct = get_text_from_image()  # 获取OCR识别的文本信息
    text_to_correct = text_to_correct.replace('\n', '')
    payload = json.dumps({
        "text": text_to_correct
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    result = json.loads(response.text)
    if 'item' in result and 'correct_query' in result['item']:  
        corrected_text = result['item']['correct_query']
        details = result['item']['details']
        count_errors = 0  # 记录错误数量的变量
        for detail in details:
            vec_fragment = detail['vec_fragment']
            for fragment in vec_fragment:
                if fragment['ori_frag'] != fragment['correct_frag']:
                    count_errors += 1  # 每次发现不同的原始和纠正文本增加错误数量计数
                    print(f"在句子'{detail['sentence_fixed']}'中，将'{fragment['ori_frag']}'替换为'{fragment['correct_frag']}'")
                    sentence.append(detail['sentence_fixed'])
                    ori_word.append(fragment['ori_frag'])
                    correct_word.append(fragment['correct_frag'])
        print(f"一共有{count_errors}处错误")  # 打印错误数量
        print("纠正后的文本：", corrected_text)
        
        # 返回结果给客户端
        return jsonify({
            'identify_text':text_to_correct,
            'sentence': sentence,
            'ori_word': ori_word,
            'correct_word': correct_word
            
        })
    else:
        print("文本纠错失败")
        return jsonify({'error': 'Text correction failed'})
def get_text_from_image():
    global image_path
    data = request.get_json()
    if 'image_path' in data:
        image_path = data['image_path']
    else:
        return "image_path not found in JSON"
        
    url = "https://aip.baidubce.com/rest/2.0/ocr/v1/handwriting?access_token=" + identify_get_access_token()
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    
    response = requests.get(image_path)
    if response.status_code == 200:
        image_content = response.content
        payload = {"image": base64.b64encode(image_content).decode("utf8")}
    
    response = requests.request("POST", url, headers=headers, data=payload)
    
    result = response.json()
    
    if "words_result" in result:
        words_result = result["words_result"]
        text = ''.join([word['words'] for word in words_result])
        text = text.replace(",", "，").replace(".", "。").replace("?", "？").replace("!", "！")
        text = text.replace(";", "；").replace(":", "：").replace("'", "’").replace("`", "‘")
        text = text.replace("\"", "”").replace("[", "【").replace("]", "】").replace("{", "｛")
        text = text.replace("}", "｝").replace("(", "（").replace(")", "）").replace("-", "－")
        print("纠正前的文本：", text)
        return text
        
    else:
        print(result)
        return "OCR failed"



def get_file_content_as_base64(path, urlencoded=False):
    with open(path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf8")
        if urlencoded:
            content = urllib.parse.quote_plus(content)
    return content

def get_access_token():
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": CORRECT_API_KEY, "client_secret": CORRECT_SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))

def identify_get_access_token():
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": IDENTIFY_API_KEY, "client_secret": IDENTIFY_SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))


if __name__ == '__main__':
    app.run()
