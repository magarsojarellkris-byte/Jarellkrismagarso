
import sqlite3
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def home():
    return render_template('index.html')


# Get a sample student
@app.route('/student')
def get_student():
    return jsonify({
        "student_id": "24-00138",
        "name": "Jarell Kris Magarso",
        "program": "BSIT",
        "year": 3,
        "section": "B"
    })


# Greeting API
@app.route('/hello')
def say_hello():
    name = request.args.get('name', 'Student').strip()

    if not name:
        name = 'Student'

    return jsonify({
        "message": f"Hello, {name}!"
    })


# Multiply API
@app.route('/multiply')
def multiply_numbers():
    num1 = request.args.get('num1', type=float)
    num2 = request.args.get('num2', type=float)

    if num1 is None or num2 is None:
        return jsonify({
            "error": "Please provide num1 and num2."
        }), 400

    return jsonify({
        "number1": num1,
        "number2": num2,
        "result": num1 * num2
    })


# Get all students
@app.route('/students')
def get_students():
    conn = get_db_connection()

    try:
        students = conn.execute(
            'SELECT * FROM students'
        ).fetchall()

        return jsonify([dict(student) for student in students])
    finally:
        conn.close()


# Get a student by database ID
@app.route('/students/<int:id>')
def get_student_by_id(id):
    conn = get_db_connection()

    try:
        student = conn.execute(
            'SELECT * FROM students WHERE id = ?',
            (id,)
        ).fetchone()

        if student is None:
            return jsonify({
                "error": "Student not found."
            }), 404

        return jsonify(dict(student))
    finally:
        conn.close()


# Get students by program
@app.route('/students/program')
def get_students_by_program():
    program = request.args.get('program', '').strip()

    if not program:
        return jsonify({
            "error": "Please provide a program, such as BSIT or BSHM or BSED."
        }), 400

    conn = get_db_connection()

    try:
        students = conn.execute(
            '''
            SELECT * FROM students
            WHERE UPPER(program) = ?
            ORDER BY year, section, name
            ''',
            (program.upper(),)
        ).fetchall()

        return jsonify([dict(student) for student in students])
    finally:
        conn.close()


# Get students by section
@app.route('/students/section')
def get_students_by_section():
    section = request.args.get('section', '').strip()

    if not section:
        return jsonify({
            "error": "Please provide a section, such as A, B, or C."
        }), 400

    conn = get_db_connection()

    try:
        students = conn.execute(
            '''
            SELECT * FROM students
            WHERE UPPER(section) = ?
            ORDER BY year, name
            ''',
            (section.upper(),)
        ).fetchall()

        return jsonify([dict(student) for student in students])
    finally:
        conn.close()


# Get students by year level
@app.route('/students/year')
def get_students_by_year():
    year = request.args.get('year', type=int)

    if year is None or year < 1:
        return jsonify({
            "error": "Please provide a valid year level, such as 1, 2, 3, or 4."
        }), 400

    conn = get_db_connection()

    try:
        students = conn.execute(
            '''
            SELECT * FROM students
            WHERE year = ?
            ORDER BY section, name
            ''',
            (year,)
        ).fetchall()

        return jsonify([dict(student) for student in students])
    finally:
        conn.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)