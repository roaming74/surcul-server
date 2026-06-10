from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import random
import yagmail
import re

app = Flask(__name__)
CORS(app)

EMAIL_ADDRESS = "arosvlad3@gmail.com"
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

codes = {}
names = {}

def is_valid_email(email):
    """Проверка, похоже ли на email"""
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email) is not None

def send_code_email(to_email, code):
    try:
        yag = yagmail.SMTP(EMAIL_ADDRESS, EMAIL_PASSWORD)
        yag.send(
            to=to_email,
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
    return jsonify({"available": name not in names})

@app.route('/send_code', methods=['POST'])
def send_code():
    data = request.json
    email = data.get("email")
    name = data.get("name")
    
    # Проверка 1: Ник уже занят
    if name in names:
        return jsonify({"success": False, "error": "Ник уже занят"})
    
    # Проверка 2: Неправильный email (там где "ЛДОАВПМИРЫОЛДВРТСВЛДОСЬЛДОАР")
    if not is_valid_email(email):
        return jsonify({"success": False, "error": "Неверный формат email"})
    
    # Проверка 3: Слишком часто
    if email in codes and codes[email]["expires"] > time.time():
        return jsonify({"success": False, "error": "Подождите 5 минут"})
    
    code = random.randint(1000, 9999)
    
    # Проверка 4: Не удалось отправить письмо (почта существует, но письмо не ушло)
    if send_code_email(email, code):
        codes[email] = {"code": code, "expires": time.time() + 300}
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Не удалось отправить код"})

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
