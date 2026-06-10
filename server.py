from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import random
import yagmail
import os

app = Flask(__name__)
CORS(app)

# --- НАСТРОЙКИ ПОЧТЫ (это на сервере, никто не увидит!) ---
EMAIL_ADDRESS = "ТВОЙ_EMAIL@gmail.com"
EMAIL_PASSWORD = "ТВОЙ_ПАРОЛЬ_ПРИЛОЖЕНИЯ"

# Хранилище кодов
codes = {}  # {email: {"code": 1234, "expires": время}}
names = {}  # {name: email}

def send_code_email(email, code):
    try:
        yag = yagmail.SMTP(EMAIL_ADDRESS, EMAIL_PASSWORD)
        yag.send(
            to=email,
            subject="Код подтверждения - Surcul Modes",
            contents=f"Ваш код: {code}"
        )
        return True
    except:
        return False

@app.route('/check_name', methods=['POST'])
def check_name():
    data = request.json
    name = data.get("name")
    if name in names:
        return jsonify({"available": False})
    return jsonify({"available": True})

@app.route('/send_code', methods=['POST'])
def send_code():
    data = request.json
    email = data.get("email")
    name = data.get("name")
    
    # Проверяем ник
    if name in names:
        return jsonify({"success": False, "error": "Ник уже занят"})
    
    # Проверяем email (не слишком много запросов)
    if email in codes and codes[email]["expires"] > time.time():
        return jsonify({"success": False, "error": "Код уже отправлен, подождите"})
    
    # Генерируем код
    code = random.randint(1000, 9999)
    
    # Отправляем
    if send_code_email(email, code):
        codes[email] = {"code": code, "expires": time.time() + 300}  # 5 минут
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Ошибка отправки"})

@app.route('/verify_code', methods=['POST'])
def verify_code():
    data = request.json
    email = data.get("email")
    code = int(data.get("code"))
    name = data.get("name")
    
    # Проверяем код
    if email in codes and codes[email]["code"] == code and codes[email]["expires"] > time.time():
        # Сохраняем ник
        names[name] = email
        del codes[email]
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Неверный код"})

@app.route('/get_rooms', methods=['GET'])
def get_rooms():
    # Временно возвращаем пустой список, пока без комнат
    return jsonify({"rooms": []})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
