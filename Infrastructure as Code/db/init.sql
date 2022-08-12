CREATE DATABASE library;
use library;

DROP TABLE IF EXISTS books;
CREATE TABLE books
(
    id     INT NOT NULL UNIQUE AUTO_INCREMENT,
    name   VARCHAR(20),
    genres ENUM ('Fantasy','Mystery','Romance'),
    writer VARCHAR(20)
);

DROP TABLE IF EXISTS user;
CREATE TABLE user
(
    id           INT         NOT NULL UNIQUE AUTO_INCREMENT,
    name         varchar(60) NOT NULL,
    Phone_Number varchar(11) NOT NULL UNIQUE,
    Password     varchar(255)
);
