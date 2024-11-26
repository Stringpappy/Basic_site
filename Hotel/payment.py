from flask import Flask, render_template, request, jsonify
import stripe

app = Flask(__name__)
app.config.from_pyfile('config.py')

stripe.api_key = app.config['STRIPE_SECRET_KEY']

@app.route('/payment', methods=['GET'])
def payment_page():
    return render_template('payment.html', public_key=app.config['STRIPE_PUBLIC_KEY'])

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': 'Product Name'},
                        'unit_amount': 1000,  # Amount in cents ($10.00)
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url='http://127.0.0.1:5000/success',
            cancel_url='http://127.0.0.1:5000/payment',
        )
        return jsonify({'id': session.id})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/success', methods=['GET'])
def success_page():
    return render_template('success.html')

if __name__ == '__main__':
    app.run(debug=True)
