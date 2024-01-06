import requests
from flask import Flask, request, jsonify

url = "http://localhost:5000/ocr"

data = {
    "image_path": "1.jpg"
}

response = requests.post(url, json=data)

result = response.json()

print(result)