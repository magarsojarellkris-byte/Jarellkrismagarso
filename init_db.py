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
    section TEXT NOT NULL,
    source TEXT DEFAULT 'Local'
)
''')

# Add the source column if the database already exists without it
cursor.execute("PRAGMA table_info(students)")
columns = [column[1] for column in cursor.fetchall()]

if 'source' not in columns:
    cursor.execute("""
        ALTER TABLE students
        ADD COLUMN source TEXT DEFAULT 'Local'
    """)

# WARNING: This deletes ALL existing student records.
# Keep this line only if you intentionally want to reset the records.
cursor.execute('DELETE FROM students')

students = [
    ('24-00154', 'Janine Pagmanoja', 'BSIT', 3, 'B', 'Local'),
    ('25-00094', 'Kristel Joy Camimo', 'BSHM', 2, 'C', 'Local'),
    ('26-00034', 'Princess Ubasan', 'BSA', 1, 'A', 'Local'),
    ('26-00254', 'Sheine Hope Quibingco', 'BSIT', 1, 'D', 'Local'),
    ('25-00089', 'Joemarie Lapasara', 'BSIT', 2, 'B', 'Local'),
    ('25-00176', 'Andrea Castillo', 'BSED', 2, 'C', 'Local')
]

cursor.executemany('''
INSERT INTO students
    (student_id, name, program, year, section, source)
VALUES (?, ?, ?, ?, ?, ?)
''', students)

# Save changes and close the connection
conn.commit()
conn.close()

print("Database initialized successfully with 6 student records.")