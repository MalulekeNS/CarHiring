from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Database initialization
def init_db():
    with sqlite3.connect('car_hiring.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                vehicle TEXT NOT NULL,
                pickup_date TEXT NOT NULL,
                return_date TEXT NOT NULL,
                additional_requests TEXT,
                payment_method TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contact_inquiries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                subject TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

# Email validation
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Phone validation
def is_valid_phone(phone):
    pattern = r'^\+?\d{10,12}$'
    return re.match(pattern, phone) is not None

# Date validation
def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

# Send confirmation email
def send_confirmation_email(to_email, subject, body):
    sender_email = "your_email@example.com"  # Replace with your email
    sender_password = "your_password"  # Replace with your email password
    smtp_server = "smtp.gmail.com"  # Adjust based on your email provider
    smtp_port = 587

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

@app.route('/api/bookings', methods=['POST'])
def create_booking():
    data = request.get_json()
    
    # Extract form data
    full_name = data.get('full_name')
    email = data.get('email')
    phone = data.get('phone')
    vehicle = data.get('vehicle')
    pickup_date = data.get('pickup_date')
    return_date = data.get('return_date')
    additional_requests = data.get('additional_requests')
    payment_method = data.get('payment_method')

    # Validate input
    if not all([full_name, email, phone, vehicle, pickup_date, return_date, payment_method]):
        return jsonify({'error': 'All required fields must be filled'}), 400
    
    if not is_valid_email(email):
        return jsonify({'error': 'Invalid email format'}), 400
    
    if not is_valid_phone(phone):
        return jsonify({'error': 'Invalid phone number format'}), 400
    
    if not is_valid_date(pickup_date) or not is_valid_date(return_date):
        return jsonify({'error': 'Invalid date format'}), 400
    
    pickup = datetime.strptime(pickup_date, '%Y-%m-%d')
    return_dt = datetime.strptime(return_date, '%Y-%m-%d')
    if pickup >= return_dt:
        return jsonify({'error': 'Return date must be after pickup date'}), 400
    
    if vehicle not in ['Toyota Corolla', 'Ford Ranger', 'Volkswagen Polo', 'BMW X5', 'Mercedes S-Class']:
        return jsonify({'error': 'Invalid vehicle selection'}), 400
    
    if payment_method not in ['Bank Transfer', 'Credit Card', 'Cash on Delivery']:
        return jsonify({'error': 'Invalid payment method'}), 400

    # Store in database
    try:
        with sqlite3.connect('car_hiring.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO bookings (full_name, email, phone, vehicle, pickup_date, return_date, 
                    additional_requests, payment_method)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (full_name, email, phone, vehicle, pickup_date, return_date, 
                  additional_requests, payment_method))
            conn.commit()
            
            # Send confirmation email
            email_body = f"""
            Booking Confirmation
            Name: {full_name}
            Vehicle: {vehicle}
            Pickup Date: {pickup_date}
            Return Date: {return_date}
            Payment Method: {payment_method}
            Thank you for choosing LTD Car Hiring Services!
            """
            send_confirmation_email(email, "Booking Confirmation", email_body)
            
            return jsonify({'message': 'Booking created successfully'}), 201
    except sqlite3.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/api/contact', methods=['POST'])
def submit_contact_form():
    data = request.get_json()
    
    # Extract form data
    name = data.get('name')
    email = data.get('email')
    subject = data.get('subject')
    message = data.get('message')

    # Validate input
    if not all([name, email, subject, message]):
        return jsonify({'error': 'All fields are required'}), 400
    
    if not is_valid_email(email):
        return jsonify({'error': 'Invalid email format'}), 400

    # Store in database
    try:
        with sqlite3.connect('car_hiring.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO contact_inquiries (name, email, subject, message)
                VALUES (?, ?, ?, ?)
            ''', (name, email, subject, message))
            conn.commit()
            
            # Send confirmation email
            email_body = f"""
            Thank you for contacting LTD Car Hiring Services!
            Name: {name}
            Subject: {subject}
            Message: {message}
            We'll get back to you soon.
            """
            send_confirmation_email(email, "Contact Form Submission", email_body)
            
            return jsonify({'message': 'Contact form submitted successfully'}), 201
    except sqlite3.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    vehicles = [
        {'name': 'Toyota Corolla', 'price': 'R500/day'},
        {'name': 'Ford Ranger', 'price': 'R750/day'},
        {'name': 'Volkswagen Polo', 'price': 'R450/day'},
        {'name': 'BMW X5', 'price': 'R1200/day'},
        {'name': 'Mercedes S-Class', 'price': 'R1500/day'}
    ]
    return jsonify(vehicles), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True)