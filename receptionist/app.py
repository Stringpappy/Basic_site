from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta

app = Flask(__name__)

# Data for rooms
is_available = True
standard_single_room = [
    {"name": "Single Room", "price": 100, "id": 1, "is_available": is_available},
    {"name": "Double Room", "price": 150, "id": 2, "is_available": is_available},
    {"name": "Three Bed", "price": 200, "id": 3, "is_available": is_available},
    {"name": "Single Room", "price": 250, "id": 4, "is_available": is_available},
    {"name": "Double Room", "price": 350, "id": 5, "is_available": is_available},
    {"name": "Three Bed", "price": 500, "id": 6, "is_available": is_available}
]

luxury_single_room = [
    {"name": "Single Room", "price": 250, "id": 4, "is_available": is_available},
    {"name": "Double Room", "price": 350, "id": 5, "is_available": is_available},
    {"name": "Three Bed", "price": 500, "id": 6, "is_available": is_available}
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

if __name__ == '__main__':
    app.run(debug=True)
