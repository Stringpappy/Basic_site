from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta

app = Flask(__name__)

# Data for rooms
is_available = True
is_available = True
standard_single_room = [
    {"caption": "Single Room", "price": 100, "id": 1, "is_available": is_available, "src": "https://example.com/single-room.jpg"},
    {"caption": "Double Room", "price": 150, "id": 2, "is_available": is_available, "src": "https://example.com/double-room.jpg"},
    {"caption": "Three Bed", "price": 200, "id": 3, "is_available": is_available, "src": "https://example.com/three-bed.jpg"},
    {"caption": "Single Room", "price": 250, "id": 4, "is_available": is_available, "src": "https://example.com/single-room-premium.jpg"},
    {"caption": "Double Room", "price": 350, "id": 5, "is_available": is_available, "src": "https://example.com/double-room-premium.jpg"},
    {"caption": "Three Bed", "price": 500, "id": 6, "is_available": is_available, "src": "https://example.com/three-bed-premium.jpg"}
]

luxury_single_room = [
    {"caption": "Single Room", "price": 250, "id": 4, "is_available": is_available, "src": "https://example.com/single-room-premium.jpg"},
    {"caption": "Double Room", "price": 350, "id": 5, "is_available": is_available, "src": "https://example.com/double-room-premium.jpg"},
    {"caption": "Three Bed", "price": 500, "id": 6, "is_available": is_available, "src": "https://example.com/three-bed-premium.jpg"}
]

# Room categories data
room_categories = [
    {"category": "Standard Room", "rooms": standard_single_room},
    {"category": "Luxury Room", "rooms": luxury_single_room}
]

# Dictionary to store room bookings with end time
room_bookings = {}

@app.route('/')
def landpage():
    return render_template('landpage.html')

@app.route('/index.html')
def index():
    return render_template('index.html', room_categories=room_categories)

@app.route('/standard_room')
def standard_room():
    # Find the "Standard Room" category
    standard_room_category = next(
        (category for category in room_categories if category['category'] == 'Standard Room'),
        None
    )
    if standard_room_category:
        return render_template('standard_html.html', rooms=standard_room_category['rooms'])
    return "Standard Room category not found", 404

@app.route('/book_room/<int:room_id>', methods=['POST'])
def book_room(room_id):
    # Check if the room exists in the standard room category
    room = next((room for room in standard_single_room if room['id'] == room_id), None)
    if room:
        # Check if the room is available
        if room['is_available']:
            # Get the duration from the form (assuming the user submits a 'duration' in days)
            duration = int(request.form['duration'])  # Duration in days
            end_time = datetime.now() + timedelta(days=duration)

            # Mark the room as booked and set the unavailable status
            room['is_available'] = False
            room_bookings[room_id] = end_time

            # Redirect to a confirmation page (optional)
            return redirect(url_for('confirmation', room_id=room_id))
        else:
            return "Room is already booked for the selected period.", 400
    return "Room not found.", 404

@app.route('/confirmation/<int:room_id>')
def confirmation(room_id):
    room = next((room for room in standard_single_room if room['id'] == room_id), None)
    if room:
        return f"Booking Confirmed for {room['name']}. The room is booked until {room_bookings[room_id].strftime('%Y-%m-%d %H:%M:%S')}."
    return "Room not found.", 404

@app.before_request
def check_room_availability():
    # Before every request, check if any rooms have expired bookings and set them back to available
    for room_id, end_time in list(room_bookings.items()):
        if datetime.now() > end_time:
            # Find the room and mark it available again
            room = next((room for room in standard_single_room if room['id'] == room_id), None)
            if room:
                room['is_available'] = True
                del room_bookings[room_id]  # Remove the booking from the dictionary








#this code below is for booking session
temporary_bookings = {}

# SQLite database setup (for persistence)
def init_db():
    conn = sqlite3.connect('bookings.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id TEXT PRIMARY KEY, 
            customer_name TEXT NOT NULL,
            customer_email TEXT NOT NULL,
            check_in TEXT NOT NULL,
            check_out TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS booking_rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id TEXT, 
            room_id INTEGER,
            room_name TEXT,
            price DECIMAL,
            status TEXT,
            FOREIGN KEY(booking_id) REFERENCES bookings(id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()  # Ensure the database table exists

# Route to submit booking
@app.route('/submit_booking', methods=['POST'])
def submit_booking():
    room_ids = request.form.getlist('room_id')  # List of room IDs for the multiple rooms
    check_in = request.form['check_in']
    check_out = request.form['check_out']
    num_rooms = len(room_ids)  # Number of rooms being booked
    customer_name = request.form['customer_name']
    customer_email = request.form['customer_email']
    
    # Generate a unique booking ID
    booking_id = str(uuid.uuid4())  # Unique booking ID
    
    # Store multiple rooms under the same booking ID
    temporary_bookings[booking_id] = {
        'check_in': check_in,
        'check_out': check_out,
        'rooms': [{'room_id': room_id} for room_id in room_ids],  # List of rooms
        'num_rooms': num_rooms,
        'customer_name': customer_name,
        'customer_email': customer_email
    }

    # Redirect to the payment page with booking_id as a query parameter
    return redirect(url_for('payment', booking_id=booking_id))

# Route to display payment page
@app.route('/payment')
def payment():
    booking_id = request.args.get('booking_id')
    return render_template('payment.html', booking_id=booking_id)

# Route to process payment
@app.route('/process_payment', methods=['POST'])
def process_payment():
    booking_id = request.form['booking_id']
    card_number = request.form['card_number']
    expiration = request.form['expiration']
    cvv = request.form['cvv']
    billing_address = request.form['billing_address']
    
    # Logic to process the payment (you can integrate a payment gateway here)
    # For now, we simulate a successful payment.
    
    payment_status = "Paid"
    
    # Retrieve the booking data from memory
    if booking_id in temporary_bookings:
        booking_details = temporary_bookings[booking_id]
        
        # Save the booking data to the database
        save_to_database(booking_id, booking_details, payment_status)
        
        # Remove from in-memory storage after saving to the database
        del temporary_bookings[booking_id]
        
    return "Payment Processed Successfully!"

# Function to save the booking and room details to the database
def save_to_database(booking_id, booking_details, payment_status):
    conn = sqlite3.connect('bookings.db')
    cursor = conn.cursor()
    
    # Insert the booking into the bookings table
    cursor.execute('''
        INSERT INTO bookings (id, customer_name, customer_email, check_in, check_out)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        booking_id,
        booking_details['customer_name'],
        booking_details['customer_email'],
        booking_details['check_in'],
        booking_details['check_out']
    ))
    
    # Insert the room details into the booking_rooms table for each room
    for room in booking_details['rooms']:
        cursor.execute('''
            INSERT INTO booking_rooms (booking_id, room_id, room_name, price, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            booking_id,
            room['room_id'],
            "Room Name",  # You can replace with actual room name or lookup table
            100.0,        # Example price, you can replace with actual price
            payment_status
        ))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    app.run(debug=True)
