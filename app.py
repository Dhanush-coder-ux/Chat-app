from flask import Flask, render_template,request
from flask_socketio import SocketIO, emit
from flask_mysqldb import MySQL
import uuid  
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'wertiuyhyuhuybygy7gggyg8yh8y'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Dhanush@2005#'
app.config['MYSQL_DB'] = 'chat_app'
app.config['MYSQL_PORT'] = 3306

mysql = MySQL(app)
socketio = SocketIO(app)


users = {}

@app.route('/')
def home():
   
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM messages")
    messages = cur.fetchall()
    cur.close()
    return render_template('chat.html', messages=messages)

@socketio.on('connect')
def handle_connect():
    user_id = str(uuid.uuid4()) 
    users[user_id] = request.sid 
    emit('assign_user_id', {'user_id': user_id})  
    print(f"Client connected with user ID: {user_id}")

@socketio.on('disconnect')
def handle_disconnect():
    user_id = get_user_id_by_session(request.sid)
    if user_id:
        del users[user_id]
    print(f"Client disconnected with user ID: {user_id}")

@socketio.on('message')
def handle_message(data):
    user_id = data['user_id']  
    message_content = data['content']
    
    print(f"Received from user {user_id}: {message_content}")
    
   
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO messages (content, user_id) VALUES (%s, %s)", (message_content, user_id))
    mysql.connection.commit()
    cur.close()

   
    response_data = {'content': message_content, 'sender': user_id}
    emit('response', response_data, broadcast=True)
    
def get_user_id_by_session(session_id):
    for user_id, sid in users.items():
        if sid == session_id:
            return user_id
    return None

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
