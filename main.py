from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase

app = Flask(__name__)
app.config["SECRET_KEY"] = "abcd"
socketio = SocketIO(app)
rooms = {}

def get_room_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)

        if code not in rooms:
            break
    
    return code




@app.route("/", methods=["POST", "GET"])
def home():
    session.clear()
    if request.method == 'POST':
        name = request.form.get("name")
        room_code = request.form.get("room_code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)

        if not name:
            return render_template("home.html", error="Name cannot be empty", room_code=room_code)

        if not room_code and join != False:
            return render_template("home.html", error="Enter a Room code to join a room", name=name)

        room = room_code
        if create != False:
            room = get_room_code(4)
            rooms[room] = {"members": 0, "messages": []}
        session["room"] = room
        session["name"] = name

        return redirect(url_for("room"))
    else:
        return render_template("home.html")


@app.route("/room", methods=["GET"])
def room():
    room = session["room"]
    if room is None or session["name"] is None or room not in rooms:
        return redirect(url_for("home"))
    

    return render_template("room.html")



@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")
    if not room or not name:
        return

    if room not in rooms:
        leave_room(room)

    join_room(room)
    send({"name": name, "message": "has entered the room"})
    rooms[room]["members"] += 1
    print(f"{name} has joined the room {room}")


@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]
    send({"name": name, "message": "has left the room"})
    print(f"{name} has left the room")







if __name__ == '__main__':
    socketio.run(app, debug=True)
