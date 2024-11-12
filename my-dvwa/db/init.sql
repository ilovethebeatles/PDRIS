CREATE DATABASE web_application;
USE web_application;
CREATE TABLE users(
id INTEGER PRIMARY KEY AUTO_INCREMENT,
username VARCHAR(256) UNIQUE NOT NULL,
password VARCHAR(256) NOT NULL,
role VARCHAR(10) NOT NULL,
cookie VARCHAR(256),
avatar_url VARCHAR(256));

CREATE TABLE session_cookies(
id INTEGER PRIMARY KEY AUTO_INCREMENT,
cookie VARCHAR(256) NOT NULL,
username VARCHAR(256) NOT NULL,
last_login TIMESTAMP);

CREATE TABLE posts(
id INTEGER PRIMARY KEY AUTO_INCREMENT,
author VARCHAR(255) NOT NULL,
content TEXT NOT NULL,
created_at TIMESTAMP);

INSERT INTO users VALUES (1, "admin", "qejqjwoejgqijweiogfjqiowjgoijefeirjgilwehrgi", "admin", NULL, NULL);