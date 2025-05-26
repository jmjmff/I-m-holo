from flask import *
from db import * 

app = Flask(__name__)

# app 사용 시 필수 변수..?
# app.secret_key='test111'

# depts = DeptDAO().get_depts() # 부서 목록 가져오기

@app.route('profile/<nickname>') # 프로필 페이지 url
def profile(nickname) : # nickname을 받아서 profile()함수 실행
    conn = get_connection()
    cursor = conn.cusor(dictionary=True)

    cusor.execute("SELECT * FROM profiles WHERE nickname = %s", (nickname,)) # nickname에 해당하는 프로필 가져오기
    user = cursor.fetchone() # 프로필 정보 가져오기

    cursor.close() # 커서 닫기
    conn.close()

    if user is None:
        return "해당 프로필이 없습니다.", 404
    
    return render_template('# 프로파일 html', user=user) # 프로필 페이지 렌더링