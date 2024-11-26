from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret_key"  # Used for flash messages

# Directory to store user activity files
ACTIVITY_DIR = "user_activities"
if not os.path.exists(ACTIVITY_DIR):
    os.makedirs(ACTIVITY_DIR)


# Initialize the database
def init_db():
    conn = sqlite3.connect("customers.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            address TEXT
        )
    """)
    conn.commit()
    conn.close()


# Route to display the customer form
@app.route("/", methods=["GET", "POST"])
def customer_form():
    if request.method == "POST":
        # Get form data
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        address = request.form["address"]

        if not name or not email:
            flash("Name and Email are required!", "error")
            return redirect(url_for("customer_form"))

        try:
            # Save customer to database
            conn = sqlite3.connect("customers.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO customers (name, email, phone, address) VALUES (?, ?, ?, ?)",
                           (name, email, phone, address))
            conn.commit()
            conn.close()
            flash("Customer added successfully!", "success")
            return redirect(url_for("customer_form"))
        except sqlite3.IntegrityError:
            flash("Email already exists. Please use a different email.", "error")
            return redirect(url_for("customer_form"))

    return render_template("customer_form.html")


# Display all customers
@app.route("/customers")
def customer_list():
    conn = sqlite3.connect("customers.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()
    conn.close()
    return render_template("customer_list.html", customers=customers)


# Route to log activity for a specific user
@app.route("/log_activity/<int:user_id>", methods=["GET", "POST"])
def log_activity(user_id):
    conn = sqlite3.connect("customers.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM customers WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        flash("User not found!", "error")
        return redirect(url_for("customer_list"))

    user_name = user[0]

    if request.method == "POST":
        activity = request.form["activity"]
        payment = request.form["payment"]

        if not activity or not payment:
            flash("Activity and Payment are required!", "error")
            return redirect(url_for("log_activity", user_id=user_id))

        try:
            # Define the file name for the user
            file_path = os.path.join(ACTIVITY_DIR, f"{user_name}_activity.txt")

            # Count current activities for the user
            activity_count = 1
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    lines = f.readlines()
                    activity_count = len(lines) + 1

            # Prepare the activity log entry
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            activity_key = f"{user_name} activity {activity_count}"
            activity_data = {
                "activity": activity,
                "payment": payment,
                "date": timestamp.split(" ")[0],  # Extract date
                "time": timestamp.split(" ")[1]   # Extract time
            }

            # Write the activity log to the user's file
            with open(file_path, "a") as f:
                f.write(f"{activity_key}: {activity_data}\n")

            flash("Activity logged successfully!", "success")
        except Exception as e:
            flash(f"Error logging activity: {e}", "error")

        return redirect(url_for("customer_list"))

    return render_template("log_activity.html", user_name=user_name)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
