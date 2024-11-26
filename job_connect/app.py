from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'seeker' or 'provider'

# Job model
class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=True)  # Optional price for service
    location = db.Column(db.String(200), nullable=True)  # Optional location
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@app.route('/')
def homepage():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            session['email'] = user.email
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials", 401
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    username = session['username']
    email = session['email']

    # Fetch jobs posted by the logged-in user
    jobs = Job.query.filter_by(user_id=user_id).all()

    return render_template('dashboard.html', username=username, email=email, jobs=jobs)


@app.route('/post-job', methods=['GET', 'POST'])
def post_job():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        user_id = session['user_id']
        
        # Save the job to the database
        new_job = Job(title=title, description=description, user_id=user_id)
        db.session.add(new_job)
        db.session.commit()
        
        return redirect(url_for('dashboard'))
    
    return render_template('post_job.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        keyword = request.form['keyword']

        # Search for jobs containing the keyword in the title or description
        jobs = Job.query.filter(
            (Job.title.contains(keyword)) | (Job.description.contains(keyword))
        ).all()

        return render_template('search_results.html', jobs=jobs, keyword=keyword)

    return render_template('search.html')

@app.route('/profile/<int:user_id>')
def profile(user_id):
    user = User.query.get_or_404(user_id)

    if user.role == 'provider':
        # Fetch jobs posted by the provider
        jobs = Job.query.filter_by(user_id=user_id).all()
    else:
        jobs = None  # Job seekers don't post jobs

    return render_template('profile.html', user=user, jobs=jobs)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('homepage'))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
