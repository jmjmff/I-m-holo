

from flask import Flask, render_template, request, redirect, url_for, session
from auth import register_user, login_user

app = Flask(__name__)
#app.secret_key = "b'\xd8\x03\xfaW\xca\x01\x13\xf3\xc6\\\xbf\x1a\xbd\xe2\xe8n\x86\xa1V\xf7\x98\xf1\x9b\xc9'"  # 세션 키

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
        nickname = request.form['nickname']
        if register_user(email, password, nickname):
            session['email'] = email
            return redirect(url_for('dashboard'))
        else:
            return "❌ 회원가입 실패 (이메일 중복?)"
    return render_template("register.html")

@app.route('/dashboard')
def dashboard():
    if 'email' in session:
        return f"✅ 로그인 성공! 환영합니다, {session['email']}!"
    else:
        return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

# 프로필 작성 후 -> DB 에 올라가는 코드
from flask import render_template, request, redirect, url_for, session
from db import get_connection

@app.route('/onboarding', methods=['GET', 'POST'])
def onboarding():
    if 'email' not in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        email = session['email']
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

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO profiles (user_email, animal_icon, mbti, age, job, location, religion, dream, love_style, preference, keywords)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (email, animal, mbti, age, job, location, religion, dream, love_style, preference, keywords))
            conn.commit()
        except Exception as e:
            print("❌ 온보딩 저장 실패:", e)
            return "에러 발생"
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('dashboard'))

    return render_template('onboarding.html')
