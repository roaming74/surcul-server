from flask import Flask, request, jsonify
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

rooms = {}
room_counter = 1

@app.route('/create_room', methods=['POST'])
def create_room():
    global room_counter
    data = request.json
    # Здесь главное отличие: мы берем IP от самого Flask, который видит внешний адрес подключившегося
    host_ip = request.remote_addr
    room_id = str(room_counter)
    room_counter += 1
    rooms[room_id] = {
        "host_ip": host_ip,
        "host_name": data.get("player_name", "Игрок"),
        "players": 1,
        "max_players": 2,
        "created_at": time.time()
    }
    return jsonify({"room_id": room_id, "success": True})

@app.route('/get_rooms', methods=['GET'])
def get_rooms():
    room_list = []
    for room_id, room in rooms.items():
        if room["players"] < room["max_players"]:
            room_list.append({
                "room_id": room_id,
                "host_name": room["host_name"],
                "players": room["players"],
                "host_ip": room["host_ip"]
            })
    return jsonify({"rooms": room_list})

@app.route('/join_room', methods=['POST'])
def join_room():
    data = request.json
    room_id = data.get("room_id")
    if room_id in rooms and rooms[room_id]["players"] < rooms[room_id]["max_players"]:
        rooms[room_id]["players"] += 1
        return jsonify({"success": True, "host_ip": rooms[room_id]["host_ip"]})
    return jsonify({"success": False})

@app.route('/leave_room', methods=['POST'])
def leave_room():
    data = request.json
    room_id = data.get("room_id")
    if room_id in rooms:
        rooms[room_id]["players"] -= 1
        if rooms[room_id]["players"] <= 0:
            del rooms[room_id]
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
