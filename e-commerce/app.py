from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Dummy data for cart items
cart_items = []

# Routes
@app.route('/')
def homepage():
    return render_template('homepage.html', cart_items=cart_items)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form['search_query']
        return f"Search results for: {query}"
    return redirect(url_for('homepage'))

@app.route('/add_to_cart/<item>')
def add_to_cart(item):
    cart_items.append(item)
    return redirect(url_for('homepage'))

@app.route('/signin',  methdod=['GET', 'POST'])
def signin():
    return render_template('signin.html')

@app.route('/clothes')
def clothes():
    return render_template('clothes.html')

@app.route('/accessories')
def accessories():
    return render_template('accessories.html')

@app.route('/footwares')
def footwares():
    return render_template('footwares.html')

@app.route('/bags')
def bags():
    return render_template('bags.html')

@app.route('/gadget')
def gadget():
    return render_template('gadget.html')

if __name__ == '__main__':
    app.run(debug=True)
