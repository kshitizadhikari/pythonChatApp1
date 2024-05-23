from flask import Flask, render_template, request, session, redirect
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

        if join != False and not room_code:
            return render_template("home.html", error="Enter a Room code to join a room", name=name)


        if create != False:
            code = get_room_code(4)
            rooms[code] = {"members": 0, "messages": []}

        session["room_code"] = code
        session["name"] = name
        return redirect("/room")
    else:
        return render_template("home.html")


@app.route("/room", methods=["GET"])
def room():
    return render_template("chatroom.html")

if __name__ == '__main__':
    socketio.run(app, debug=True)
