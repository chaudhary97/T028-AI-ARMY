import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import random

class StudentDatabase:
    def __init__(self, db_name="student_database.db"):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Students table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                guardian_name TEXT,
                guardian_phone TEXT,
                guardian_email TEXT,       
                mentor_id TEXT,
                enrollment_date DATE
            )
        ''')
        
        # Attendance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                subject TEXT,
                date DATE,
                present BOOLEAN,
                FOREIGN KEY (student_id) REFERENCES students (student_id)
            )
        ''')
        
        # Test scores table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                subject TEXT,
                test_type TEXT,
                score REAL,
                max_score REAL,
                test_date DATE,
                attempt_number INTEGER,
                FOREIGN KEY (student_id) REFERENCES students (student_id)
            )
        ''')
        
        # Fee payments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fee_payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                amount_due REAL,
                amount_paid REAL,
                due_date DATE,
                payment_date DATE,
                status TEXT,
                FOREIGN KEY (student_id) REFERENCES students (student_id)
            )
        ''')
        
        # Risk assessment table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS risk_assessment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                assessment_date DATE,
                overall_risk_score REAL,
                risk_level TEXT,
                attendance_risk REAL,
                academic_risk REAL,
                financial_risk REAL,
                reasons TEXT,
                FOREIGN KEY (student_id) REFERENCES students (student_id)
            )
        ''')
        
        # Notifications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                mentor_id TEXT,
                notification_type TEXT,
                message TEXT,
                sent_date DATE,
                status TEXT,
                FOREIGN KEY (student_id) REFERENCES students (student_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Database tables initialized successfully!")
    
    def generate_sample_data(self, num_students=50):
        """Generate sample data for testing"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Clear existing data (optional)
        cursor.execute("DELETE FROM notifications")
        cursor.execute("DELETE FROM risk_assessment")
        cursor.execute("DELETE FROM fee_payments")
        cursor.execute("DELETE FROM test_scores")
        cursor.execute("DELETE FROM attendance")
        cursor.execute("DELETE FROM students")
        
        # Generate sample students
        students = []
        for i in range(num_students):
            student_id = f"STU{1000 + i}"
            students.append((
                student_id,
                f"Student {i+1}",
                f"student{i+1}@institute.edu",
                f"98765432{str(i).zfill(2)}",
                f"Guardian {i+1}",
                f"98765432{str(i+100).zfill(2)}",
                f"MENT{(i % 10) + 1}",
                "2024-01-15"
            ))
        
        cursor.executemany('''
            INSERT INTO students 
            (student_id, name, email, phone, guardian_name, guardian_phone, mentor_id, enrollment_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', students)
        
        # Generate sample attendance data
        subjects = ['Mathematics', 'Physics', 'Chemistry', 'English', 'Computer Science']
        attendance_data = []
        for student in students:
            student_id = student[0]
            for subject in subjects:
                for day in range(30):  # Last 30 days
                    date = (datetime.now() - timedelta(days=30-day)).strftime('%Y-%m-%d')
                    # Simulate attendance patterns - some students have poor attendance
                    if int(student_id[3:]) % 5 == 0:  # 20% of students have poor attendance
                        present = random.random() > 0.4  # 60% attendance
                    else:
                        present = random.random() > 0.1  # 90% attendance
                    attendance_data.append((student_id, subject, date, present))
        
        cursor.executemany('''
            INSERT INTO attendance (student_id, subject, date, present)
            VALUES (?, ?, ?, ?)
        ''', attendance_data)
        
        # Generate sample test scores
        test_data = []
        for student in students:
            student_id = student[0]
            for subject in subjects:
                attempts = random.randint(1, 3)
                for attempt in range(attempts):
                    # Students with ID ending in 0,4,7 have academic issues
                    if int(student_id[3:]) % 10 in [0,4,7]:
                        base_score = 55  # Lower scores for at-risk students
                    else:
                        base_score = 75
                    
                    score = max(0, min(100, random.normalvariate(base_score, 12)))
                    test_type = f"Unit Test {attempt + 1}"
                    test_date = (datetime.now() - timedelta(days=30-attempt*7)).strftime('%Y-%m-%d')
                    test_data.append((
                        student_id, subject, test_type, score, 100, test_date, attempt+1
                    ))
        
        cursor.executemany('''
            INSERT INTO test_scores 
            (student_id, subject, test_type, score, max_score, test_date, attempt_number)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', test_data)
        
        # Generate sample fee payment data
        fee_data = []
        for student in students:
            student_id = student[0]
            # 15% of students have fee issues
            has_fee_issue = int(student_id[3:]) % 10 in [2, 5]
            amount_due = 5000
            amount_paid = 0 if has_fee_issue else 5000
            status = "Pending" if has_fee_issue else "Paid"
            due_date = (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d')
            payment_date = None if has_fee_issue else (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')
            
            fee_data.append((
                student_id, amount_due, amount_paid, due_date, payment_date, status
            ))
        
        cursor.executemany('''
            INSERT INTO fee_payments 
            (student_id, amount_due, amount_paid, due_date, payment_date, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', fee_data)
        
        conn.commit()
        conn.close()
        print(f"✓ Generated sample data for {num_students} students")

    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_name)

# Test the class
if __name__ == "__main__":
    db = StudentDatabase()
    db.generate_sample_data(10)
    print("Database setup completed successfully!")