
import sqlite3

conn = sqlite3.connect('students.db')
cursor = conn.cursor()

# Create the students table if it does not exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    name TEXT NOT NULL,
    program TEXT NOT NULL,
    year INTEGER NOT NULL,
    section TEXT NOT NULL
)
''')

# Clear existing student records
cursor.execute('DELETE FROM students')

# Six realistic, fictional sample student records
students = [
    ('24-00138', 'Jarell Kris Magarso', 'BSIT', 1, 'B'),
    ('24-00132', 'Sofia Mendoza', 'BSIT', 1, 'B'),
    ('25-00133', 'Daniel Garcia', 'BSIT', 2, 'A'),
    ('21-00134', 'Isabella Torres', 'BSIT', 1, 'B'),
    ('23-00135', 'Miguel Flores', 'BSIT', 4, 'A'),
    ('25-00136', 'Andrea Castillo', 'BSIt', 2, 'C')
]

# Insert the sample records
cursor.executemany('''
INSERT INTO students (student_id, name, program, year, section)
VALUES (?, ?, ?, ?, ?)
''', students)

# Save changes and close the connection
conn.commit()
conn.close()

print("Database initialized successfully with 6 student records.")
