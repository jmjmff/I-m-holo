from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# MySQL 설정
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'proj-1'
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_DB'] = 'proj-1' 
app.config['MYSQL_CHARSET'] = 'utf8'
mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/explore', methods=['GET', 'POST'])
def explore():
    cur = mysql.connection.cursor()
    gender = request.form.get('gender')
    icon = request.form.get('icon')

    query = "SELECT * FROM users WHERE 1=1"
    params = []
    if gender:
        query += " AND gender=%s"
        params.append(gender)
    if icon and icon != 'all':
        query += " AND animal_icon=%s"
        params.append(icon)

    cur.execute(query, params)
    users = cur.fetchall()
    cur.close()
    return render_template('explore.html', users=users)

@app.route('/profile/<int:user_id>')
def profile_detail(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cur.fetchone()
    cur.close()
    return render_template('profile_detail.html', user=user)

@app.route('/like/<int:target_user_id>', methods=['POST'])
def like_user(target_user_id):
    from_user_id = session.get('user_id')
    if not from_user_id:
        return redirect('/')
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO likes (from_user_id, to_user_id) VALUES (%s, %s)", (from_user_id, target_user_id))
    # 매칭 확인
    cur.execute("SELECT * FROM likes WHERE from_user_id=%s AND to_user_id=%s", (target_user_id, from_user_id))
    if cur.fetchone():
        cur.execute("INSERT INTO matches (user1_id, user2_id) VALUES (%s, %s)", (from_user_id, target_user_id))
    mysql.connection.commit()
    cur.close()
    return redirect('/explore')

@app.route('/matches')
def match_list():
    user_id = session.get('user_id')
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT * FROM users WHERE id IN (
            SELECT user2_id FROM matches WHERE user1_id=%s
            UNION
            SELECT user1_id FROM matches WHERE user2_id=%s
        )
    """, (user_id, user_id))
    matches = cur.fetchall()
    cur.close()
    return render_template('matches.html', matched_users=matches)

@app.route('/me')
def my_profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/')
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cur.fetchone()
    cur.close()
    return render_template('my_profile_view.html', user=user)

@app.route('/me/edit', methods=['GET', 'POST'])
def edit_profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/')
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        data = (
            request.form['username'], request.form['gender'], request.form['animal_icon'],
            request.form['age'], request.form['job'], request.form['location'],
            request.form['mbti'], request.form['instagram'], request.form['contact'], user_id
        )
        cur.execute("""
            UPDATE users SET username=%s, gender=%s, animal_icon=%s,
            age=%s, job=%s, location=%s, mbti=%s, instagram=%s, contact=%s WHERE id=%s
        """, data)
        mysql.connection.commit()
        cur.close()
        return redirect('/me')
    else:
        cur.execute("SELECT * FROM users WHERE id=%s", (user_id,))
        user = cur.fetchone()
        cur.close()
        return render_template('edit_profile.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)