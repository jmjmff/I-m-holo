from flask import Flask, render_template, request, redirect, url_for, session
from auth import register_user, login_user
from db import get_connection
from flask_socketio import SocketIO, join_room, emit
from datetime import datetime

app = Flask(__name__)
app.secret_key = "b'\xd8\x03\xfaW\xca\x01\x13\xf3..."  # 세션 키

# SocketIO 초기화
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def home():
    return render_template("login.html")

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    if login_user(email, password):
        session['email'] = email
        return redirect(url_for('dashboard'))
    else:
        return "❌ 로그인 실패!"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if register_user(email, password):
            session['email'] = email
            return redirect(url_for('onboarding'))  # ✅ 수정됨!
        else:
            return "❌ 회원가입 실패 (이메일 중복?)"
    return render_template("register.html")

@app.route('/onboarding', methods=['GET', 'POST'])
def onboarding():
    if 'email' not in session:
        return redirect(url_for('home'))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM profiles WHERE user_email = %s", (session['email'],))
    existing = cursor.fetchone()
    cursor.close()
    conn.close()

    if existing:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = session['email']
        nickname = request.form['nickname']
        animal = request.form['animal']
        mbti = request.form['mbti']
        age = request.form['age']
        job = request.form['job']
        location = request.form['location']
        religion = request.form['religion']
        dream = request.form['dream']
        love_style = request.form['love_style']
        preference = request.form['preference']
        keywords = request.form['keywords']
        gender = request.form['gender']
        phone = request.form['phone']
        instagram = request.form['instagram']

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO profiles (user_email, nickname, animal_icon, mbti, age, job, location, religion, dream, love_style, preference, keywords, gender, phone, instagram)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s)
            """, (email, nickname, animal, mbti, age, job, location, religion, dream, love_style, preference, keywords, gender, phone, instagram))
            conn.commit()
        except Exception as e:
            print("❌ 온보딩 저장 실패:", e)
            return "에러 발생"
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('dashboard'))

    return render_template('onboarding.html')

@app.route('/dashboard')
def dashboard():
    if 'email' not in session:
        return redirect(url_for('home'))

    return render_template('dashboard.html', email=session['email'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/explore', methods=['GET', 'POST'])
def explore():
    if 'email' not in session:
        return redirect(url_for('home'))

    conn = get_connection()
    cursor = conn.cursor()

    gender = ''
    animal = ''
    profiles = []

    # ✅ 내가 이미 좋아요한 사용자 리스트 가져오기
    cursor.execute("SELECT to_user FROM likes WHERE from_user = %s", (session['email'],))
    liked_users = [row[0] for row in cursor.fetchall()]

    if request.method == 'POST':
        gender = request.form.get('gender')
        animal = request.form.get('animal')

        query = "SELECT * FROM profiles WHERE user_email != %s"
        params = [session['email']]  # 자기 자신은 제외

        if gender:
            query += " AND gender = %s"
            params.append(gender)

        if animal:
            query += " AND animal_icon = %s"
            params.append(animal)

        cursor.execute(query, tuple(params))
        profiles = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("explore.html", profiles=profiles, liked_users=liked_users)


@app.route('/like/<to_email>')
def like_user(to_email):
    if 'email' not in session:
        return redirect(url_for('home'))

    from_email = session['email']

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT IGNORE INTO likes (from_user, to_user)
            VALUES (%s, %s)
        """, (from_email, to_email))

        cursor.execute("""
            SELECT id FROM likes
            WHERE from_user = %s AND to_user = %s
        """, (to_email, from_email))

        match = cursor.fetchone()
        conn.commit()

        if match:
            return f"💘 매칭 완료! {to_email}님과 연결되었습니다."
        else:
            return f"❤️ 좋아요를 보냈습니다!"
    except Exception as e:
        print("❌ 좋아요 오류:", e)
        return "에러 발생"
    finally:
        cursor.close()
        conn.close()



@app.route('/matches')
def matches():
    if 'email' not in session:
        return redirect(url_for('home'))

    my_email = session['email']

    conn = get_connection()
    cursor = conn.cursor()

    # 상호 좋아요 된 사용자만 추출
    cursor.execute("""
        SELECT p.nickname, p.mbti, p.age, p.location, p.animal_icon, p.instagram, p.phone, p.user_email
        FROM profiles p
        WHERE p.user_email IN (
            SELECT l1.to_user
            FROM likes l1
            JOIN likes l2
              ON l1.to_user = l2.from_user AND l1.from_user = l2.to_user
            WHERE l1.from_user = %s
        )
    """, (my_email,))
    
    matches = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("matches.html", matches=matches)

def make_room(a, b):
    """두 이메일로 방 이름 생성 (순서 무관)"""
    return "_".join(sorted([a, b]))

@app.route('/chat/<user_email>')
def chat(user_email):
    if 'email' not in session:
        return redirect(url_for('home'))

    my_email = session['email']
    # 채팅 기록은 최초 로드 시 한 번만 가져와서 렌더링
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sender, content, timestamp
        FROM messages
        WHERE (sender = %s AND receiver = %s)
           OR (sender = %s AND receiver = %s)
        ORDER BY timestamp ASC
    """, (my_email, user_email, user_email, my_email))
    messages = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template(
        'chat.html',
        messages=messages,
        my_email=my_email,
        user_email=user_email
    )


@socketio.on('join')
def on_join(data):
    room = make_room(data['my_email'], data['user_email'])
    join_room(room)


@socketio.on('send_message')
def on_send_message(data):
    my_email = data['my_email']
    user_email = data['user_email']
    content = data['message']

    # 1) DB에 저장
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (sender, receiver, content) VALUES (%s, %s, %s)",
        (my_email, user_email, content)
    )
    conn.commit()
    cursor.close()
    conn.close()

    # 2) 브로드캐스트
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    room = make_room(my_email, user_email)
    emit('receive_message', {
        'sender': my_email,
        'content': content,
        'timestamp': timestamp
    }, room=room)

@app.route('/unmatch/<user_email>', methods=['POST'])
def unmatch(user_email):
    if 'email' not in session:
        return redirect(url_for('home'))

    my_email = session['email']

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            DELETE FROM likes
            WHERE (from_user = %s AND to_user = %s)
               OR (from_user = %s AND to_user = %s)
        """, (my_email, user_email, user_email, my_email))
        conn.commit()
    except Exception as e:
        print("❌ 매칭 취소 실패:", e)
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('matches'))



if __name__ == '__main__':
    # app.run(debug=True
    socketio.run(app, debug=True)
