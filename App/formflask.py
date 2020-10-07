from flask import Flask, render_template, request, redirect, session, flash
from flask_socketio import SocketIO, join_room, leave_room
import base64
# from config import secret_key
import sqlite3
import os
from datetime import date
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/Users/ASUS/Documents/MIPT/Software development practice/Phystechgram/App/static/images'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__, template_folder='templates')
socketio = SocketIO(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.urandom(24)


# with sqlite3.connect('memory.db') as conn:
#     conn.execute("PRAGMA foreign_keys = 1")
#     cursor = conn.cursor()
#     cursor.execute("DROP TABLE IF EXISTS users")
#     cursor.execute("CREATE TABLE users "
#                    "(user_id char(50), "
#                    "name char(50) PRIMARY KEY, "
#                    "email char(50), "
#                    "password char(30), "
#                    "university char(50), "
#                    "birthday char(50), "
#                    "age char(10), "
#                    "hometown char(50), "
#                    "photo, "
#                    "status char(50), "
#                    "friends int(1000));")
# # #
#     cursor.execute("DROP TABLE IF EXISTS friends")
#     cursor.execute('''CREATE TABLE IF NOT EXISTS friends
#     (friend TEXT,
#     user    TEXT,
#     FOREIGN KEY (user) REFERENCES users (name))''')
#     conn.commit()
# # #
#     cursor.execute("DROP TABLE IF EXISTS posts")
#     cursor.execute('''CREATE TABLE IF NOT EXISTS posts
#     (feeds TEXT,
#     photo   TEXT,
#     user    TEXT,
#     FOREIGN KEY (user) REFERENCES users (name))''')
#     conn.commit()

@app.route('/')
def login():
    return render_template('login.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/home')
def home():
    if 'user_id' in session:
        session['logged_in'] = True
        # return render_template("home.html", name=session['name'].capitalize())
        return render_template("home.html", name=session['name'].capitalize(), feed=post_feed(), image=post_image(),
                               user=post_user())
    else:
        return redirect('/')


@app.route('/feeds', methods=['POST'])
def feeds():
    session['name'] = request.form.get('name')
    password = request.form.get('password')

    # cursor.execute("""SELECT * FROM `users` WHERE `email` LIKE '{}' AND `password` LIKE '{}'""".format(email, password))
    with sqlite3.connect('memory.db') as conn:
        cursor = conn.cursor()
    # cursor.execute("""SELECT * FROM `users` WHERE `email` LIKE '{}' AND `password` LIKE '{}'""".format(email, password))

    cursor.execute('''SELECT * FROM users WHERE name=? AND password=?''', (session['name'], password))
    users = cursor.fetchall()

    if len(users) > 0:
        session['user_id'] = users[0][0]
        # session1 = session["name"]
        # user = users[name]
        # session["NAME"] = user["name"]
        session['logged_in'] = True
        # name = session['name']
        # cursor.execute('''SELECT * FROM users WHERE name=?''', (name,))
        # # cursor.execute("""INSERT INTO users(university) VALUES ("mipt")""")
        # exists1 = cursor.fetchall()
        # # my_list = []
        # # for row in exists1:
        # #     my_list.append(row)
        #
        # print(exists1)
        # print(session1)
        return redirect('/home')

    else:
        # return redirect('/')
        flash('Wrong username or password!')
        return redirect('/')


@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.form.get('uname')
    email = request.form.get('uemail')
    password = request.form.get('upassword')

    with sqlite3.connect('memory.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM users WHERE email=? OR name=?''', (email, name))
        exists = cursor.fetchall()
    if not exists:
        # userID = cursor.fetchall()
        # count = 1
        # for line in userID:
        # print("Line {}: {}".format(userID, lines.strip()), sep='')
        cursor.execute(
            """INSERT INTO users(user_id, name, email, password) VALUES (NULL, '{}', '{}', '{}')""".format(name, email,
                                                                                                           password))
        # count += 1
        conn.commit()

        cursor.execute('''SELECT * FROM users WHERE email=?''', (email,))
        myuser = cursor.fetchall()
        session['user_id'] = myuser[0][0]
        session['logged_in'] = True
        return redirect('/')
    else:
        return redirect('/register')


@app.route('/logout')
def logout():
    session.pop('user_id')
    session['logged_in'] = False
    return redirect('/')


@app.route('/settings')
def settings():
    if 'user_id' in session:
        session['logged_in'] = True
        with sqlite3.connect('memory.db') as conn:
            cursor = conn.cursor()
        name = session['name']
        cursor.execute('''SELECT * FROM users WHERE name=?''', (name,))
        exists1 = cursor.fetchall()
        session['university'] = exists1[0][4]
        session['birthday'] = exists1[0][5]
        session['hometown'] = exists1[0][7]
        session['photo'] = exists1[0][8]
        session['status'] = exists1[0][9]

        return render_template("settings.html", name=session['name'].capitalize(),
                               university=session['university'], birthday=session['birthday'],
                               hometown=session['hometown'], photo=session['photo'], status=session['status'])
    else:
        return redirect('/')


def calculateAge(birthDate):
    today = date.today()
    age = today.year - birthDate.year - ((today.month, today.day) < (birthDate.month, birthDate.day))
    return age


@app.route('/edit_settings', methods=['POST'])
def edit_settings():
    if 'user_id' in session:
        session['logged_in'] = True
        university = request.form.get('university')
        birthday = request.form.get('birthday')
        hometown = request.form.get('hometown')
        status = request.form.get('status')

        with sqlite3.connect('memory.db') as conn:
            cursor = conn.cursor()
            name = session['name']
            cursor.execute('''SELECT * FROM users WHERE name=?''', (name,))

            cursor.execute('''UPDATE users SET university=? WHERE name=?''', (university, name))
            cursor.execute('''UPDATE users SET birthday=? WHERE name=?''', (birthday, name))
            cursor.execute('''UPDATE users SET hometown=? WHERE name=?''', (hometown, name))
            cursor.execute('''UPDATE users SET status=? WHERE name=?''', (status, name))
            year = int(birthday[0:4])
            month = int(birthday[5:7])
            day = int(birthday[8:10])
            subtraction = date(year, month, day)
            age = calculateAge(subtraction)
            cursor.execute('''UPDATE users SET age=? WHERE name=?''', (age, name))

            # cursor.execute("""INSERT INTO users(university) VALUES ('{}') WHERE name=?""".format(university, name))
            conn.commit()
            # cursor.execute('''SELECT * FROM users WHERE email=?''', (email,))
            # myuser = cursor.fetchall()
            # session['user_id'] = myuser[0][0]

            return redirect("/settings")
    else:
        return redirect('/')


@app.route('/add_picture', methods=['POST'])
def add_picture():
    if 'user_id' in session:
        session['logged_in'] = True
        # photo = request.form.get('photo')

        image = request.files['file']  # myfile is name of input tag
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        path = os.path.realpath(image.filename)
        # print(image.filename)
        # print(path)

        with sqlite3.connect('memory.db') as conn:
            cursor = conn.cursor()
            name = session['name']
            cursor.execute('''UPDATE users SET photo=? WHERE name=?''', (image.filename, name))
            conn.commit()

        return redirect("/settings")
    else:
        return redirect('/')


@app.route('/myprofile')
def myprofile():
    if 'user_id' in session:
        session['logged_in'] = True

        with sqlite3.connect('memory.db') as conn:
            cursor = conn.cursor()
        name = session['name']
        cursor.execute('''SELECT * FROM users WHERE name=?''', (name,))
        exists1 = cursor.fetchall()
        username = exists1[0][1]
        email = exists1[0][2]
        session['university'] = exists1[0][4]
        session['birthday'] = exists1[0][5]
        session['age'] = exists1[0][6]
        session['hometown'] = exists1[0][7]
        session['photo'] = exists1[0][8]
        session['status'] = exists1[0][9]
        # print(exists1)
        # print(username, ' | ', email)
        # , username = username, email = email

        return render_template("myprofile.html", name=session['name'].capitalize(), username=username, email=email,
                               university=session['university'], birthday=session['birthday'],
                               hometown=session['hometown'], photo=session['photo'],
                               status=session['status'], age=session['age'], rows=count_friends(),
                               friends=friends_list(), feed=post_feed(), image=post_image(), user=post_user()
                               )
    else:
        return redirect('/')


@app.route('/search', methods=['POST'])
def search():
    if 'user_id' in session:
        session['logged_in'] = True
        name = session['name']
        user_search = request.form.get('name')
        print(user_search)
        with sqlite3.connect('memory.db') as conn:
            cursor = conn.cursor()
        cursor.execute('''SELECT * FROM users WHERE name=?''', (user_search,))
        exists1 = cursor.fetchall()
        if exists1:
            session['name_search'] = exists1[0][1]
            session['email_search'] = exists1[0][2]
            session['university_search'] = exists1[0][4]
            session['birthday_search'] = exists1[0][5]
            session['age_search'] = exists1[0][6]
            session['hometown_search'] = exists1[0][7]
            session['photo_search'] = exists1[0][8]
            session['status_search'] = exists1[0][9]
            # room = session['name_search']
            # print(room)
            return render_template("search.html", name=name, user_search=user_search,
                                   university=session['university_search'], hometown=session['hometown_search'],
                                   photo=session['photo_search'], age=session['age_search'])
        else:
            session['not_found'] = "Sorry, we couldn't find anything :("
            return render_template("search.html", error=session['not_found'])

    else:
        return redirect('/')


def post_feed():
    with sqlite3.connect('memory.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM posts")
        rows = cursor.fetchall()
        for row in rows:
            feed = row[0]
            # print(feed)
            yield feed


def post_image():
    with sqlite3.connect('memory.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM posts")
        rows = cursor.fetchall()
        for row in rows:
            image = row[1]
            # print(image)
            yield image


def post_user():
    with sqlite3.connect('memory.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM posts")
        rows = cursor.fetchall()
        for row in rows:
            user = row[2]
            # print(user)
            yield user


@app.route('/user')
def user():
    if 'user_id' in session:
        session['logged_in'] = True
        name = session['name']
        user = request.args.get('id')
        print(user)

        with sqlite3.connect('memory.db') as conn:
            cursor = conn.cursor()
        cursor.execute('''SELECT * FROM users WHERE name=?''', (user,))
        exists1 = cursor.fetchall()
        if exists1:
            session['name_user'] = exists1[0][1]
            session['email_user'] = exists1[0][2]
            session['university_user'] = exists1[0][4]
            session['birthday_user'] = exists1[0][5]
            session['age_user'] = exists1[0][6]
            session['hometown_user'] = exists1[0][7]
            session['photo_user'] = exists1[0][8]
            session['status_user'] = exists1[0][9]

        return render_template("user.html", name=name, user=session['name_user'], email=session['email_user'],
                               university=session['university_user'], birthday=session['birthday_user'],
                               hometown=session['hometown_user'],
                               photo=session['photo_user'], age=session['age_user'],
                               status=session['status_user'])
    else:
        return redirect('/')


def count_friends():
    with sqlite3.connect('memory.db') as conn:
        cursor = conn.cursor()
        name = session['name']
        cursor.execute('''SELECT COUNT(*) FROM friends WHERE user=?''', (name,))
        count = cursor.fetchone()
        rows = count[0]
        return rows


def friends_list():
    with sqlite3.connect('memory.db') as conn:
        cursor = conn.cursor()
        name = session['name']
        cursor.execute('''SELECT * FROM friends WHERE user=?''', (name,))
        rows = cursor.fetchall()
        for row in rows:
            friends = row[0]
            yield friends


@app.route('/follow_friend', methods=['POST'])
def follow_friend():
    if 'user_id' in session:
        session['logged_in'] = True
        name = session['name']
        name_search = session['name_search']
        # if name==name_search(done)/ if name_search is none/ if name_search already in friends/ allow multiple names go to the column(done)

        with sqlite3.connect('memory.db') as conn:
            cursor = conn.cursor()

            cursor.execute('''SELECT * FROM friends WHERE user=?''', (name,))
            exists1 = cursor.fetchall()
            # print(exists1)
            # print(name)
            # print(name_search)

            match = (name_search, name)
            if match in exists1:
                return render_template("search.html")

            elif name == name_search:
                return render_template("search.html")

            else:
                cursor.execute("""INSERT INTO friends(friend, user) VALUES ('{}', '{}')""".format(name_search, name))
                conn.commit()
                return redirect('/user')

    else:
        return redirect('/')


@app.route('/add_post', methods=['POST'])
def add_post():
    if 'user_id' in session:
        session['logged_in'] = True
        name = session['name']
        feeds = request.form.get('feeds')

        image = request.files['file']  # myfile is name of input tag
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        path = os.path.realpath(image.filename)

        with sqlite3.connect('memory.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO posts(feeds, photo, user) VALUES ('{}', '{}', '{}')""".format(feeds, image.filename,
                                                                                             name))
            # cursor.execute("""INSERT INTO posts(photo, user) VALUES ('{}', '{}')""".format(image.filename, name))
            conn.commit()

            return redirect('/home')

    else:
        return redirect('/')


@app.route('/messages')
def messages():
    if 'user_id' in session:
        session['logged_in'] = True
        name = session['name']
        # name_search = request.form.get('name_search')
        # print(name_search)
        # room = request.form.get('room')
        # print(room)

        return render_template('messages.html', name=name)

    else:
        return redirect('/')


@socketio.on('send_message')
def handle_send_message_event(data):
    app.logger.info("{} has sent message to the room {}: {}".format(data['name'],
                                                                    data['room'],
                                                                    data['message']))
    socketio.emit('receive_message', data, room=data['room'])


@socketio.on('join_room')
def handle_join_room_event(data):
    app.logger.info("{} has joined the room with {}".format(data['name'], data['room']))
    join_room(data['room'])
    socketio.emit('join_room_announcement', data)


@socketio.on('leave_room')
def handle_leave_room_event(data):
    app.logger.info("{} has left the room {}".format(data['name'], data['room']))
    leave_room(data['room'])
    socketio.emit('leave_room_announcement', data, room=data['room'])


if __name__ == '__main__':
    socketio.run(app, debug=True)
