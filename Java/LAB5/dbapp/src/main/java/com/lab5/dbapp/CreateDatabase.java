package com.lab5.dbapp;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.Statement;

public class CreateDatabase {

    public static void main(String[] args) {

        try {
            String path = "lab5.db"; 
            Connection conn = DriverManager.getConnection("jdbc:sqlite:" + path);
            Statement stmt = conn.createStatement();

            // =============== TABLES ===============

            stmt.execute("""
                CREATE TABLE IF NOT EXISTS departments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL
                );
            """);

            stmt.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    age INTEGER,
                    department_id INTEGER,
                    email TEXT,
                    FOREIGN KEY(department_id) REFERENCES departments(id)
                );
            """);

            stmt.execute("""
                CREATE TABLE IF NOT EXISTS teachers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    position TEXT,
                    department_id INTEGER,
                    FOREIGN KEY(department_id) REFERENCES departments(id)
                );
            """);

            stmt.execute("""
                CREATE TABLE IF NOT EXISTS courses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    teacher_id INTEGER,
                    credits INTEGER,
                    semester INTEGER,
                    FOREIGN KEY(teacher_id) REFERENCES teachers(id)
                );
            """);

            stmt.execute("""
                CREATE TABLE IF NOT EXISTS enrollments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER,
                    course_id INTEGER,
                    grade INTEGER,
                    FOREIGN KEY(student_id) REFERENCES students(id),
                    FOREIGN KEY(course_id) REFERENCES courses(id)
                );
            """);

            // =============== INSERT DATA ===============

            stmt.execute("INSERT INTO departments(name) VALUES ('Computer Science');");
            stmt.execute("INSERT INTO departments(name) VALUES ('Mathematics');");
            stmt.execute("INSERT INTO departments(name) VALUES ('Physics');");
            stmt.execute("INSERT INTO departments(name) VALUES ('Economics');");
            stmt.execute("INSERT INTO departments(name) VALUES ('Biology');");

            String[] studentData = {
                    "('Vlad', 19, 1, 'vlad@gmail.com')",
                    "('Anna', 20, 2, 'anna@gmail.com')",
                    "('Max', 21, 1, 'max@ukr.net')",
                    "('Oleh', 22, 3, 'oleh@gmail.com')",
                    "('Sofia', 19, 4, 'sofia@gmail.com')",
                    "('Dmytro', 18, 1, 'dmytro@mail.com')",
                    "('Ira', 20, 1, 'ira@mail.com')",
                    "('Yulia', 21, 5, 'yulia@gmail.com')",
                    "('Serhii', 23, 2, 'serhii@mail.com')",
                    "('Nazar', 24, 3, 'nazar@mail.com')",
                    "('Oksana', 22, 4, 'oksana@gmail.com')",
                    "('Taras', 20, 5, 'taras@gmail.com')",
                    "('Lera', 18, 1, 'lera@gmail.com')",
                    "('Maria', 19, 2, 'maria@mail.com')",
                    "('Bogdan', 21, 3, 'bogdan@mail.com')"
            };

            for (String s : studentData)
                stmt.execute("INSERT INTO students(name, age, department_id, email) VALUES " + s + ";");

            stmt.execute("INSERT INTO teachers(name, position, department_id) VALUES ('Petrenko I.I.', 'Professor', 1);");
            stmt.execute("INSERT INTO teachers(name, position, department_id) VALUES ('Ivanova T.P.', 'Associate Professor', 2);");
            stmt.execute("INSERT INTO teachers(name, position, department_id) VALUES ('Bondar O.S.', 'Lecturer', 3);");
            stmt.execute("INSERT INTO teachers(name, position, department_id) VALUES ('Koval R.V.', 'Assistant', 1);");
            stmt.execute("INSERT INTO teachers(name, position, department_id) VALUES ('Hrytsenko M.M.', 'Senior Lecturer', 4);");
            stmt.execute("INSERT INTO teachers(name, position, department_id) VALUES ('Melnyk P.V.', 'Lecturer', 5);");
            stmt.execute("INSERT INTO teachers(name, position, department_id) VALUES ('Kramar A.O.', 'Professor', 3);");
            stmt.execute("INSERT INTO teachers(name, position, department_id) VALUES ('Zhuk O.G.', 'Assistant', 1);");

            stmt.execute("INSERT INTO courses(title, teacher_id, credits, semester) VALUES ('Algorithms', 1, 5, 1);");
            stmt.execute("INSERT INTO courses(title, teacher_id, credits, semester) VALUES ('Linear Algebra', 2, 4, 1);");
            stmt.execute("INSERT INTO courses(title, teacher_id, credits, semester) VALUES ('Quantum Mechanics', 3, 6, 3);");
            stmt.execute("INSERT INTO courses(title, teacher_id, credits, semester) VALUES ('Microeconomics', 5, 3, 2);");
            stmt.execute("INSERT INTO courses(title, teacher_id, credits, semester) VALUES ('Data Structures', 4, 5, 2);");
            stmt.execute("INSERT INTO courses(title, teacher_id, credits, semester) VALUES ('Operating Systems', 1, 4, 3);");
            stmt.execute("INSERT INTO courses(title, teacher_id, credits, semester) VALUES ('Databases', 4, 5, 2);");
            stmt.execute("INSERT INTO courses(title, teacher_id, credits, semester) VALUES ('Statistics', 2, 3, 1);");
            stmt.execute("INSERT INTO courses(title, teacher_id, credits, semester) VALUES ('Genetics', 6, 4, 2);");
            stmt.execute("INSERT INTO courses(title, teacher_id, credits, semester) VALUES ('Machine Learning', 1, 6, 3);");

            for (int i = 1; i <= 15; i++) {
                for (int c = 1; c <= 5; c++) {
                    int grade = (int)(Math.random() * 40 + 60);
                    stmt.execute("INSERT INTO enrollments(student_id, course_id, grade) VALUES ("+i+", "+c+", "+grade+");");
                }
            }

            // =============== VIEW ===============

            stmt.execute("""
                CREATE VIEW IF NOT EXISTS student_department AS
                SELECT students.name AS student,
                       students.age,
                       students.email,
                       departments.name AS department
                FROM students
                JOIN departments ON students.department_id = departments.id;
            """);

            // =============== TRIGGER ===============

            stmt.execute("""
                CREATE TRIGGER IF NOT EXISTS enroll_log AFTER INSERT ON enrollments
                BEGIN
                    INSERT INTO teachers(name, position, department_id)
                    VALUES ('AUTO_LOG', 'Inserted enrollment for student ' || NEW.student_id, 1);
                END;
            """);

            conn.close();
            System.out.println("lab5.db created with FULL DATA, VIEW, and TRIGGER!");

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
