

import bcrypt
from db import get_connection

def register_user(email, password, nickname):
    conn = get_connection()
    cursor = conn.cursor()
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        cursor.execute(
            "INSERT INTO users (email, password, nickname) VALUES (%s, %s, %s)",
            (email, hashed_pw, nickname)
        )
        conn.commit()
        return True
    except Exception as e:
        print("❌ 회원가입 오류:", e)  # 문제 원인 로그 출력
        return False
    finally:
        cursor.close()
        conn.close()

def login_user(email, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE email = %s", (email,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result:
        return bcrypt.checkpw(password.encode(), result[0])  # 이미 bytes 타입임
    return False
