USE student_management;

DROP TABLE IF EXISTS students;

CREATE TABLE students (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    full_name     VARCHAR(100)  NOT NULL,
    email         VARCHAR(100)  NOT NULL UNIQUE,
    phone         VARCHAR(15)   NOT NULL,
    course        VARCHAR(50)   NOT NULL,
    enrolled_on   DATE          NOT NULL DEFAULT (CURRENT_DATE)
);