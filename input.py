import requests
from flask import Flask, request, jsonify

url = "http://localhost:5000/ocr"

data = {
    "image_path": "https://www.ertongzy.com/uploads/allimg/150112/1-150112142309.jpg"
}

response = requests.post(url, json=data)

result = response.json()

print(result)