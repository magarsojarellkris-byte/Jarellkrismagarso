
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import sqlite3
import requests

app = Flask(__name__)
CORS(app)


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_db_connection():
    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    return conn


# ==========================================
# DATABASE INITIALIZATION
# ==========================================

def initialize_database():
    conn = get_db_connection()

    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                program TEXT NOT NULL,
                year INTEGER NOT NULL,
                section TEXT NOT NULL,
                source TEXT DEFAULT 'Local'
            )
        """)

        columns = [
            row['name']
            for row in conn.execute(
                "PRAGMA table_info(students)"
            ).fetchall()
        ]

        if 'source' not in columns:
            conn.execute("""
                ALTER TABLE students
                ADD COLUMN source TEXT DEFAULT 'Local'
            """)

        conn.commit()

    finally:
        conn.close()


# Initialize database when the Flask application loads.
initialize_database()


# ==========================================
# STUDENT DATA VALIDATION
# ==========================================

def validate_student(data):

    if not isinstance(data, dict):
        return None, "Please provide student data in JSON format."

    required_fields = [
        'student_id',
        'name',
        'program',
        'year',
        'section'
    ]

    for field in required_fields:
        if field not in data or str(data[field]).strip() == '':
            return None, f"Missing required field: {field}"

    try:
        year = int(data['year'])
    except (ValueError, TypeError):
        return None, "Year must be a number from 1 to 4."

    if year not in (1, 2, 3, 4):
        return None, "Year must be 1, 2, 3, or 4."

    validated_data = {
        'student_id': str(data['student_id']).strip(),
        'name': str(data['name']).strip(),
        'program': str(data['program']).strip(),
        'year': year,
        'section': str(data['section']).strip()
    }

    return validated_data, None


# ==========================================
# HOME
# ==========================================

@app.route('/')
def home():
    return render_template('index.html')


# ==========================================
# GET A SAMPLE STUDENT
# ==========================================

@app.route('/student')
def get_student():
    return jsonify({
        "student_id": "24-00138",
        "name": "Jarell Kris Magarso",
        "program": "BSIT",
        "year": 3,
        "section": "B"
    })


# ==========================================
# GREETING API
# ==========================================

@app.route('/hello')
def say_hello():
    name = request.args.get('name', 'Student').strip()

    if not name:
        name = 'Student'

    return jsonify({
        "message": f"Hello, {name}!"
    })


# ==========================================
# MULTIPLY API
# ==========================================

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


# ==========================================
# GET ALL STUDENTS
# ==========================================

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


# ==========================================
# GET STUDENT BY DATABASE ID
# ==========================================

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


# ==========================================
# GET STUDENTS BY PROGRAM
# ==========================================

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


# ==========================================
# GET STUDENTS BY SECTION
# ==========================================

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


# ==========================================
# GET STUDENTS BY YEAR LEVEL
# ==========================================

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


# ==========================================
# ADD A NEW STUDENT
# POST /api/students
# Supports External API / Partner API
# ==========================================

@app.route('/api/students', methods=['POST'])
def add_student():

    raw_data = request.get_json(silent=True)

    if not isinstance(raw_data, dict):
        return jsonify({
            'error': 'Please provide student data in JSON format.'
        }), 400

    # Default source for externally received records
    source = raw_data.get('source', 'External API')

    if not isinstance(source, str) or not source.strip():
        source = 'External API'
    else:
        source = source.strip()

    data, error = validate_student(raw_data)

    if error:
        return jsonify({
            'error': error
        }), 400

    conn = get_db_connection()

    try:
        cursor = conn.execute(
            '''
            INSERT INTO students
            (student_id, name, program, year, section, source)
            VALUES (?, ?, ?, ?, ?, ?)
            ''',
            (
                data['student_id'],
                data['name'],
                data['program'],
                data['year'],
                data['section'],
                source
            )
        )

        conn.commit()

        return jsonify({
            'message': 'Student added successfully.',
            'id': cursor.lastrowid,
            'student_id': data['student_id'],
            'name': data['name'],
            'program': data['program'],
            'year': data['year'],
            'section': data['section'],
            'source': source
        }), 201

    except sqlite3.IntegrityError:
        conn.rollback()

        return jsonify({
            'error': 'Could not add student. The student ID may already exist.'
        }), 409

    except sqlite3.Error:
        conn.rollback()
        app.logger.exception("Database error while adding student.")

        return jsonify({
            'error': 'A database error occurred while adding the student.'
        }), 500

    finally:
        conn.close()


# ==========================================
# GET STUDENT THROUGH API
# ==========================================

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


# ==========================================
# UPDATE AN EXISTING STUDENT
# ==========================================

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


# ==========================================
# DELETE A STUDENT
# ==========================================

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


# ==========================================
# GET ALL STUDENTS THROUGH API
# ==========================================

@app.route('/api/students', methods=['GET'])
def api_students():
    conn = get_db_connection()

    try:
        rows = conn.execute(
            'SELECT * FROM students'
        ).fetchall()

        return jsonify([dict(row) for row in rows])

    finally:
        conn.close()


# ==========================================
# RETRIEVE RECORDS FROM PARTNER FLASK API
# ==========================================

@app.route('/partner-records')
def partner_records():

    # Your classmate's deployed Render API
    partner_url = "https://janinepagmanoja.onrender.com/api/students"

    try:
        response = requests.get(partner_url, timeout=15)
        response.raise_for_status()

        return jsonify(response.json())

    except requests.RequestException:
        app.logger.exception("Unable to retrieve partner data.")

        return jsonify({
            "error": "Unable to retrieve partner data."
        }), 502

    except ValueError:
        return jsonify({
            "error": "Partner API returned invalid JSON."
        }), 502


# ==========================================
# IMPORT A STUDENT FROM PARTNER API
# ==========================================

@app.route('/import-student', methods=['POST'])
def import_student():

    data = request.get_json(silent=True)

    student, error = validate_student(data)

    if error:
        return jsonify({
            "error": error
        }), 400

    conn = get_db_connection()

    try:
        cursor = conn.execute(
            """
            INSERT INTO students
            (student_id, name, program, year, section, source)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                student['student_id'],
                student['name'],
                student['program'],
                student['year'],
                student['section'],
                'Classmate API'
            )
        )

        conn.commit()

        return jsonify({
            "message": "Remote record saved successfully.",
            "id": cursor.lastrowid,
            "student_id": student['student_id'],
            "source": "Classmate API"
        }), 201

    except sqlite3.IntegrityError:
        conn.rollback()

        return jsonify({
            "error": "This student ID already exists in your database."
        }), 409

    except sqlite3.Error:
        conn.rollback()
        app.logger.exception("Database error while importing partner student.")

        return jsonify({
            "error": "Unable to import student."
        }), 500

    finally:
        conn.close()


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    )
