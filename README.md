1. 현재 생성된  테이블
   ![image](https://github.com/user-attachments/assets/60f1b1ac-c35c-43a2-a9f2-3d97bf9a8302)

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


