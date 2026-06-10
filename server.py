from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import random
import yagmail
import os

app = Flask(__name__)
CORS(app)

# БЕРЁМ ПАРОЛЬ ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ (НЕ ИЗ КОДА!)
EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

codes = {}
names = {}

def send_code_email(email, code):
    try:
        yag = yagmail.SMTP(EMAIL_ADDRESS, EMAIL_PASSWORD)
        yag.send(to=email, subject="Код подтверждения - Surcul Modes", contents=f"Ваш код: {code}")
        return True
    except:
        return False

@app.route('/check_name', methods=['POST'])
def check_name():
    data = request.json
    name = data.get("name")
    return jsonify({"available": name not in names})

@app.route('/send_code', methods=['POST'])
def send_code():
    data = request.json
    email = data.get("email")
    name = data.get("name")
    
    if name in names:
        return jsonify({"success": False, "error": "Ник уже занят"})
    
    if email in codes and codes[email]["expires"] > time.time():
        return jsonify({"success": False, "error": "Подождите 5 минут"})
    
    code = random.randint(1000, 9999)
    
    if send_code_email(email, code):
        codes[email] = {"code": code, "expires": time.time() + 300}
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Ошибка отправки"})

@app.route('/verify_code', methods=['POST'])
def verify_code():
    data = request.json
    email = data.get("email")
    code = int(data.get("code"))
    name = data.get("name")
    
    if email in codes and codes[email]["code"] == code and codes[email]["expires"] > time.time():
        names[name] = email
        del codes[email]
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Неверный код"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
