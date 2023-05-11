from flask import Flask, request, session
from flask_socketio import SocketIO, emit, send, join_room, leave_room
from collections import defaultdict


# ===========================================================================
# 'Database' to store room of each user: user_id -> room_name
rooms_db = {}


# ===========================================================================
# Serve static HTML page with Javascript WebRTC client
app = Flask(__name__)


@app.route('/')
def index():
    return app.send_static_file('index.html')


# ===========================================================================
# Websocket signaling handlers
# Messages allowed are:
#   - "join(room_name)": Join a conferencing room, or create if not exists
#   - "invite(offer)": Caller invites Callee with a SDP offer.
#   - "ok(answer)": Callee responds to SDP offer with a SDP answer.
#   - "bye(room_name)": quit connection and leave room.
#   - "ice_candidate(candidate)": send and ICE candidate to the peer.
# Additionally, the "connect" and "disconnect" events are received for clients
# ===========================================================================
socketio = SocketIO(app)


@socketio.on('connect')
def handle_connect():
    print("Received connect")


@socketio.on('disconnect')
def handle_disconnect():
    print("Received disconnect")


@socketio.on('join')
def handle_join(room_name):
    user_id = request.sid
    members = list(rooms_db.values()).count(room_name)
    if members == 0:
        print(f'Received join from user: {user_id} for NEW room: {room_name}.')
        # Add the user_id to the rooms_db dictionary with the room_name as value
        rooms_db[user_id] = room_name
        # Use the SocketIO function join_room to add the user to a SocketIO room.
        join_room(room_name)
        # Use the SocketIO emit function to send a 'created' message back with the room_name as argument
        emit('created', room_name)
    elif members == 1:
        print(f'Received join from user: {user_id} for EXISTING room: {room_name}.')

        rooms_db[user_id] = room_name
        join_room(room_name)
        # Emit a 'joined' message back to the client, with the room_name as data.
        emit('joined', room_name)
        # Broadcast to existing client that there is a new peer
        emit('new_peer', room_name, room=room_name, broadcast=True, include_self=False)
    else:
        print(f'Refusing join from user: {user_id} for FULL room: {room_name}.')
        # Emit a 'full' message back to the client, with the room_name as data.
        emit('full', room_name)


def handle_p2pmessage(msg_type, content):
    # *** TODO ***: Get the user_id from the request variable (see handle_join)
    # *** TODO ***: Get the room_name of the user from rooms_db
    print(f"Received {msg_type} message: {content} from user: {user_id} in room {room_name}")

    # *** TODO ***: Broadcast the message to existing client in the SocketIO room.
    #               Exclude the sender of the orignal message.


# *** TODO ***: Create a message handler for 'invite' messages
# *** TODO ***: Create a message handler for 'ok' messages
# *** TODO ***: Create a message handler for 'ice_candidate' messages


@socketio.on('bye')
def handle_bye(room_name):
    # *** TODO ***: Get the user_id from the request variable
    # *** TODO ***: Use leave_room to remove the sender from the SocketIO room
    # *** TODO ***: Forward the 'bye' message using p2p_message
    # *** TODO ***: Remove the user from rooms_db
    pass


# ===========================================================================
# Run server
if __name__ == '__main__':
    socketio.run(app, "0.0.0.0", 443, ssl_context=('cert.pem', 'key.pem'))
