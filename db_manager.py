import sqlite3
from datetime import datetime

def setup_database():
    """Create the database and tables if they don't exist."""
    conn = sqlite3.connect('multiplication_stats.db')
    cursor = conn.cursor()
    
    # Create a table for tracking statistics for each multiplication combination
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stats (
        id INTEGER PRIMARY KEY,
        num1 INTEGER,
        num2 INTEGER,
        correct_count INTEGER DEFAULT 0,
        incorrect_count INTEGER DEFAULT 0,
        total_attempts INTEGER DEFAULT 0,
        avg_duration REAL DEFAULT 0,
        last_attempt TIMESTAMP
    )
    ''')
    
    # Create a table for tracking individual attempts
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS attempts (
        id INTEGER PRIMARY KEY,
        num1 INTEGER,
        num2 INTEGER,
        user_answer INTEGER,
        correct_answer INTEGER,
        is_correct INTEGER,
        duration REAL,
        timestamp TIMESTAMP
    )
    ''')
    
    # Populate the stats table with all combinations from 5x5 to 9x9 if not already present
    for num1 in range(5, 10):
        for num2 in range(5, 10):
            cursor.execute('''
            INSERT OR IGNORE INTO stats (num1, num2, correct_count, incorrect_count, total_attempts)
            VALUES (?, ?, 0, 0, 0)
            ''', (num1, num2))
    
    conn.commit()
    conn.close()

def update_stats(num1, num2, user_answer, correct_answer, duration):
    """Update the database with statistics from this attempt."""
    conn = sqlite3.connect('multiplication_stats.db')
    cursor = conn.cursor()
    
    is_correct = 1 if user_answer == correct_answer else 0
    timestamp = datetime.now()
    
    # Record this attempt
    cursor.execute('''
    INSERT INTO attempts (num1, num2, user_answer, correct_answer, is_correct, duration, timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (num1, num2, user_answer, correct_answer, is_correct, duration, timestamp))
    
    # Update the stats for this multiplication combination
    if is_correct:
        cursor.execute('''
        UPDATE stats
        SET correct_count = correct_count + 1,
            total_attempts = total_attempts + 1,
            avg_duration = ((avg_duration * correct_count) + ?) / (correct_count + 1),
            last_attempt = ?
        WHERE num1 = ? AND num2 = ?
        ''', (duration, timestamp, num1, num2))
    else:
        cursor.execute('''
        UPDATE stats
        SET incorrect_count = incorrect_count + 1,
            total_attempts = total_attempts + 1,
            last_attempt = ?
        WHERE num1 = ? AND num2 = ?
        ''', (timestamp, num1, num2))
    
    conn.commit()
    conn.close()

def get_stats(num1, num2):
    """Get the statistics for a specific multiplication problem."""
    conn = sqlite3.connect('multiplication_stats.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT correct_count, incorrect_count, total_attempts, avg_duration
    FROM stats
    WHERE num1 = ? AND num2 = ?
    ''', (num1, num2))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'correct_count': result[0],
            'incorrect_count': result[1],
            'total_attempts': result[2],
            'avg_duration': result[3]
        }
    return None

def get_weakest_combinations(limit=3):
    """Get the multiplication combinations with the lowest success rate."""
    conn = sqlite3.connect('multiplication_stats.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT num1, num2, correct_count, total_attempts,
           CASE WHEN total_attempts > 0 THEN CAST(correct_count AS REAL) / total_attempts ELSE 0 END AS success_rate
    FROM stats
    WHERE total_attempts > 0
    ORDER BY success_rate ASC, total_attempts DESC
    LIMIT ?
    ''', (limit,))
    
    results = cursor.fetchall()
    conn.close()
    
    return [{'num1': r[0], 'num2': r[1], 'correct_count': r[2], 'total_attempts': r[3], 'success_rate': r[4]} 
            for r in results] 