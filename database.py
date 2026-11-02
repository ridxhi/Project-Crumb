"""SQLite storage for Project Crumb. All queries use parameters."""
import sqlite3
from contextlib import contextmanager
from datetime import date
from pathlib import Path

DB_PATH = Path(__file__).with_name('project_crumb.db')

@contextmanager
def connect(db_path=None):
    conn = sqlite3.connect(str(db_path or DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def initialize(db_path=None):
    with connect(db_path) as conn:
        conn.executescript('''
        CREATE TABLE IF NOT EXISTS cake_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            phone TEXT NOT NULL DEFAULT '',
            size TEXT NOT NULL,
            cake_flavor TEXT NOT NULL,
            frosting TEXT NOT NULL,
            decorations TEXT NOT NULL DEFAULT '',
            pickup_date TEXT NOT NULL,
            instructions TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'Pending',
            baker_note TEXT NOT NULL DEFAULT '',
            archived INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL COLLATE NOCASE UNIQUE,
            category TEXT NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 0 CHECK(quantity >= 0),
            low_stock_at INTEGER NOT NULL DEFAULT 5 CHECK(low_stock_at >= 0),
            unit TEXT NOT NULL DEFAULT 'units'
        );
        ''')

def create_request(customer_name, phone, size, cake_flavor, frosting, decorations, pickup_date, instructions, db_path=None):
    with connect(db_path) as conn:
        return conn.execute('''INSERT INTO cake_requests
            (customer_name, phone, size, cake_flavor, frosting, decorations, pickup_date, instructions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (customer_name.strip(), phone.strip(), size, cake_flavor, frosting,
             decorations.strip(), str(pickup_date), instructions.strip())).lastrowid

def get_requests(db_path=None):
    with connect(db_path) as conn:
        return [dict(row) for row in conn.execute('SELECT * FROM cake_requests ORDER BY pickup_date ASC, id DESC')]

def update_status(request_id, status, note, db_path=None):
    if status not in ('Pending', 'Approved', 'Changes Requested', 'Declined', 'Completed'):
        raise ValueError('Invalid status')
    with connect(db_path) as conn:
        conn.execute('UPDATE cake_requests SET status=?, baker_note=? WHERE id=?', (status, note.strip(), request_id))

def set_archived(request_id, archived, db_path=None):
    with connect(db_path) as conn:
        conn.execute('UPDATE cake_requests SET archived=? WHERE id=?', (int(archived), request_id))

def get_inventory(db_path=None):
    with connect(db_path) as conn:
        return [dict(row) for row in conn.execute('SELECT * FROM inventory ORDER BY category, name')]

def add_inventory(name, category, quantity, low_stock_at, unit, db_path=None):
    with connect(db_path) as conn:
        conn.execute('INSERT INTO inventory(name, category, quantity, low_stock_at, unit) VALUES (?,?,?,?,?)',
                     (name.strip(), category.strip(), int(quantity), int(low_stock_at), unit.strip()))

def adjust_inventory(item_id, change, db_path=None):
    with connect(db_path) as conn:
        cursor = conn.execute('''UPDATE inventory SET quantity=quantity+?
            WHERE id=? AND quantity+? >= 0''', (int(change), item_id, int(change)))
        return cursor.rowcount == 1

def delete_inventory(item_id, db_path=None):
    with connect(db_path) as conn:
        conn.execute('DELETE FROM inventory WHERE id=?', (item_id,))

def seed_demo(db_path=None):
    """Add clearly fictional sample records only when the database is empty."""
    with connect(db_path) as conn:
        if conn.execute('SELECT COUNT(*) FROM cake_requests').fetchone()[0] == 0:
            conn.executemany('''INSERT INTO cake_requests
                (customer_name,phone,size,cake_flavor,frosting,decorations,pickup_date,instructions,status)
                VALUES (?,?,?,?,?,?,?,?,?)''', [
                ('Demo Customer A','555-0101','8 inch','Vanilla','Vanilla buttercream','Pink flowers','2027-01-15','Write Happy Birthday','Pending'),
                ('Demo Customer B','555-0102','6 inch','Chocolate','Chocolate buttercream','Sprinkles','2027-01-20','Nut-free request (confirm in person)','Approved'),
            ])
        if conn.execute('SELECT COUNT(*) FROM inventory').fetchone()[0] == 0:
            conn.executemany('INSERT INTO inventory(name,category,quantity,low_stock_at,unit) VALUES (?,?,?,?,?)', [
                ('All-purpose flour','Dry ingredients',18,5,'bags'),
                ('Granulated sugar','Dry ingredients',4,5,'bags'),
                ('Butter','Dairy',12,6,'lbs'),
                ('Vanilla extract','Decorations & flavoring',3,4,'bottles'),
                ('Cake boxes','Packaging',25,10,'boxes'),
            ])
