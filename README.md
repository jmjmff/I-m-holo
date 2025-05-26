#Edit 들어가서 보세요~


CREATE USER 'proj-1'@'localhost' IDENTIFIED BY 'admin';
CREATE DATABASE `proj-1` CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
GRANT ALL PRIVILEGES ON `proj-1`.* TO 'proj-1'@'localhost';
FLUSH PRIVILEGES;

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  nickname VARCHAR(50),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);


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

ALTER TABLE profiles
ADD gender VARCHAR(10),
ADD phone VARCHAR(30),
ADD instagram VARCHAR(100);

CREATE TABLE messages (
  id INT AUTO_INCREMENT PRIMARY KEY,
  sender VARCHAR(255),
  receiver VARCHAR(255),
  content TEXT,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE likes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    from_user VARCHAR(255) NOT NULL,
    to_user VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (from_user, to_user)
);


ALTER TABLE users DROP COLUMN nickname;
ALTER TABLE profiles ADD nickname VARCHAR(50);


USE `proj-1`;
SELECT * FROM users;
select * from profiles;
