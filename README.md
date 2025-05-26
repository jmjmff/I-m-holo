편집중 ---- <br>
# mini-project1 <br>


#MySQL root 계정으로 DB 생성 <br>

CREATE USER 'proj-1'@'localhost' IDENTIFIED BY 'admin'; <br>
CREATE DATABASE `proj-1` CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci; <br>
GRANT ALL PRIVILEGES ON `proj-1`.* TO 'proj-1'@'localhost'; <br>
FLUSH PRIVILEGES; <br>

#workbench 에서 계정 생성 <br>

host='127.0.0.1', <br>
port=3306, <br>
user='proj-1', <br>
passwd='admin', <br>
database='proj-1' <br>


1. 현재 생성된  테이블 <br>
   ![image](https://github.com/user-attachments/assets/60f1b1ac-c35c-43a2-a9f2-3d97bf9a8302) <br>
'''
1-1 users 의 테이블 생성 
   CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password VARBINARY(255) NOT NULL,
  nickname VARCHAR(50),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

1-2 profiles 의 테이블 생성
CREATE TABLE profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    animal_icon VARCHAR(10),
    mbti VARCHAR(4),
    age INT,
    job VARCHAR(100),
    location VARCHAR(100),
    religion VARCHAR(50),
    dream TEXT,
    love_style TEXT,
    preference TEXT,
    keywords TEXT,
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
);
'''
-------------------------- 
#구조

미니프로젝트1/ <br>
├── app.py <br>
├── db.py              👈 여기로 이동하려는 것 <br>
├── auth.py            👈 여기서 db.py를 불러옴 <br>
├── templates/ <br>
│   ├── login.html <br>
│   └── register.html <br>

