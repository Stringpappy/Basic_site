from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# Initialize database
def init_db():
    with sqlite3.connect("hotel.db") as conn:
        cursor = conn.cursor()
        # Create tables for users and workers
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                second_name TEXT NOT NULL,
                UNIQUE(profession) ON CONFLICT IGNORE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                second_name TEXT NOT NULL
            )
        """)

@app.route('/admin', methods=['GET'])
def admin():
    with sqlite3.connect("hotel.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT profession, first_name, second_name, id FROM workers")
        workers = cursor.fetchall()
    return render_template('admin.html', workers=workers)


@app.route('/remove_worker', methods=['POST'])
def remove_worker():
    worker_id = request.form['worker_id']
    with sqlite3.connect("hotel.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM workers WHERE id = ?", (worker_id,))
    return redirect('/admin')

@app.route('/register_worker', methods=['GET', 'POST'])
def register_worker():
    if request.method == 'POST':
        try:
            first_name = request.form['first_name']
            second_name = request.form['second_name']
            profession = request.form['profession']
            
            if not profession:  # Validate the profession field
                return "Please select a valid profession.", 400

            if profession.lower() == "manager":
                # Check if a manager already exists
                with sqlite3.connect("hotel.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM workers WHERE profession = 'manager'")
                    manager_count = cursor.fetchone()[0]
                    if manager_count > 0:
                        return "A manager already exists. Only one manager is allowed.", 400

            # Insert the worker into the database
            with sqlite3.connect("hotel.db") as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO workers (first_name, second_name, profession) VALUES (?, ?, ?)",
                    (first_name, second_name, profession)
                )
            return redirect('/list_workers')
        except KeyError as e:
            return f"Missing required field: {e}", 400
    return render_template('worker_signup.html')



# Route for the customer signup page
@app.route('/register_customer', methods=['GET', 'POST'])
def register_customer():
    if request.method == 'POST':
        first_name = request.form['first_name']
        second_name = request.form['second_name']
        with sqlite3.connect("hotel.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (first_name, second_name) VALUES (?, ?)", 
                           (first_name, second_name))
        return "Customer registered successfully!"
    return render_template('customer_signup.html')


@app.route('/')
def home():
    return render_template('landing_page.html')


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email_or_phone = request.form['email_or_phone']
        password = request.form['password']

        # Authenticate user
        with sqlite3.connect("hotel.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email_or_phone = ? AND password = ?", 
                           (email_or_phone, password))
            user = cursor.fetchone()

        if user:
            return redirect(url_for('make_reservation'))
        else:
            flash('Invalid email/number or password. Please try again.')
            return redirect(url_for('signin'))

    return render_template('signin.html')


@app.route('/customer_signup')
def customer_signup():
    return render_template('customers_signup.html')

@app.route('/make_reservation')
def make_reservation():
    return render_template('make_reservation.html')

@app.route('/search')
def search():
    return "Search Results Page"


# Route to list all workers
@app.route('/list_workers')
def list_workers():
    with sqlite3.connect("hotel.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT profession, first_name, second_name FROM workers")
        workers = cursor.fetchall()
    return render_template('list_workers.html', workers=workers)

# Start the application and initialize the database
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
