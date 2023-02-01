# Iniciate the database
import sqlite3

BASE_DIR = '/code/db/'
conn = sqlite3.connect(BASE_DIR + 'db.sqlite3')
c = conn.cursor()

# Create test results table
c.execute('CREATE TABLE IF NOT EXISTS site_test_results (\
            id INTEGER PRIMARY KEY AUTOINCREMENT,\
            code TEXT,\
            file_path TEXT)')

# Create contact us table
c.execute('CREATE TABLE IF NOT EXISTS site_contact_us (\
            id INTEGER PRIMARY KEY AUTOINCREMENT,\
            name TEXT,\
            email TEXT,\
            phone TEXT,\
            message TEXT)')

# Create reviews table
c.execute('CREATE TABLE IF NOT EXISTS site_reviews (\
            id INTEGER PRIMARY KEY AUTOINCREMENT,\
            name TEXT,\
            email TEXT,\
            message TEXT)')

# Create services table
c.execute('CREATE TABLE IF NOT EXISTS site_services (\
            id INTEGER PRIMARY KEY AUTOINCREMENT,\
            name TEXT,\
            description TEXT)')

conn.commit()