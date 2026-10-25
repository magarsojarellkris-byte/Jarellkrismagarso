
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
        
# Add a new student
@app.route('/api/students', methods=['POST'])
def add_student():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Please provide student data in JSON format."
        }), 400

    required_fields = [
        'student_id', 'name', 'program', 'year', 'section'
    ]

    for field in required_fields:
        if field not in data or str(data[field]).strip() == '':
            return jsonify({
                "error": f"Missing required field: {field}"
            }), 400

    try:
        year = int(data['year'])
    except (ValueError, TypeError):
        return jsonify({
            "error": "Year must be a number from 1 to 4."
        }), 400

    if year not in (1, 2, 3, 4):
        return jsonify({
            "error": "Year must be 1, 2, 3, or 4."
        }), 400

    conn = get_db_connection()

    try:
        cursor = conn.execute(
            """
            INSERT INTO students
            (student_id, name, program, year, section)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                str(data['student_id']).strip(),
                str(data['name']).strip(),
                str(data['program']).strip(),
                year,
                str(data['section']).strip()
            )
        )

        conn.commit()
        new_id = cursor.lastrowid

        return jsonify({
            "message": "Student added successfully.",
            "id": new_id
        }), 201

    except sqlite3.IntegrityError:
        conn.rollback()
        return jsonify({
            "error": "Could not add student. The student ID may already exist."
        }), 409

    except sqlite3.Error:
        conn.rollback()
        app.logger.exception("Database error while adding student.")
        return jsonify({
            "error": "A database error occurred."
        }), 500

    finally:
        conn.close()

# Get a student by ID
@app.route('/api/students/<int:id>', methods=['GET'])
def api_get_student(id):
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

        return jsonify(dict(student)), 200

    finally:
        conn.close()


# Update an existing student
@app.route('/api/students/<int:id>', methods=['PUT'])
def update_student(id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Please provide student data in JSON format."
        }), 400

    required_fields = [
        'student_id', 'name', 'program', 'year', 'section'
    ]

    for field in required_fields:
        if field not in data or str(data[field]).strip() == '':
            return jsonify({
                "error": f"Missing required field: {field}"
            }), 400

    try:
        year = int(data['year'])
    except (ValueError, TypeError):
        return jsonify({
            "error": "Year must be a number from 1 to 4."
        }), 400

    if year not in (1, 2, 3, 4):
        return jsonify({
            "error": "Year must be 1, 2, 3, or 4."
        }), 400

    conn = get_db_connection()

    try:
        student = conn.execute(
            'SELECT id FROM students WHERE id = ?',
            (id,)
        ).fetchone()

        if student is None:
            return jsonify({
                "error": "Student not found."
            }), 404

        conn.execute(
            """
            UPDATE students
            SET student_id = ?,
                name = ?,
                program = ?,
                year = ?,
                section = ?
            WHERE id = ?
            """,
            (
                str(data['student_id']).strip(),
                str(data['name']).strip(),
                str(data['program']).strip(),
                year,
                str(data['section']).strip(),
                id
            )
        )

        conn.commit()

        return jsonify({
            "message": "Student updated successfully.",
            "id": id
        }), 200

    except sqlite3.IntegrityError:
        conn.rollback()
        return jsonify({
            "error": "Could not update student. The student ID may already exist."
        }), 409

    except sqlite3.Error:
        conn.rollback()
        app.logger.exception("Database error while updating student.")
        return jsonify({
            "error": "A database error occurred."
        }), 500

    finally:
        conn.close()


# Delete a student
@app.route('/api/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    conn = get_db_connection()

    try:
        cursor = conn.execute(
            'DELETE FROM students WHERE id = ?',
            (id,)
        )

        if cursor.rowcount == 0:
            return jsonify({
                "error": "Student not found."
            }), 404

        conn.commit()

        return jsonify({
            "message": "Student deleted successfully.",
            "id": id
        }), 200

    except sqlite3.Error:
        conn.rollback()
        app.logger.exception("Database error while deleting student.")
        return jsonify({
            "error": "A database error occurred."
        }), 500

    finally:
        conn.close()
@app.route('/api/students', methods=['GET'])
def api_students():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM students').fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)