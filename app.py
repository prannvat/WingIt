from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
import uuid
from datetime import datetime
from textblob import TextBlob
import requests
from bs4 import BeautifulSoup
from functools import wraps
import hashlib
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Database setup
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # Drop the existing articles table (if you’re okay with losing data)
    c.execute('DROP TABLE IF EXISTS articles')

    # Recreate the articles table without NOT NULL constraints on title and content
    c.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            guest_id TEXT,
            title TEXT,  -- Removed NOT NULL
            content TEXT,  -- Removed NOT NULL
            url TEXT NOT NULL,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (guest_id) REFERENCES guests(id) ON DELETE SET NULL
        )
    ''')

    # Recreate other tables (users and guests) as before
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS guests (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE
        )
    ''')

    conn.commit()
    conn.close()

# Run the function to initialize the database
init_db()

# Initialize database when app starts
with app.app_context():
    init_db()

# Login decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session and 'guest' not in session:
            return redirect(url_for('landing'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def landing():
    if 'user_id' in session or 'guest' in session:
        return redirect(url_for('news'))
    return render_template('landing.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        # Hash password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT id FROM users WHERE email = ? AND password = ?', 
                 (email, hashed_password))
        user = c.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            return jsonify({'success': True, 'redirect': url_for('news')})
        else:
            return jsonify({'success': False, 'error': 'Invalid credentials'})
    
    return render_template('signin.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.json
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        
        # Hash password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        try:
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            c.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
                     (name, email, hashed_password))
            conn.commit()
            user_id = c.lastrowid
            conn.close()
            
            session['user_id'] = user_id
            return jsonify({'success': True, 'redirect': url_for('news')})
        except sqlite3.IntegrityError:
            return jsonify({'success': False, 'error': 'Email already exists'})
    
    return render_template('signup.html')

@app.route('/guest')
def guest_access():
    session['guest'] = True
    return redirect(url_for('news'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('landing'))

@app.route('/news')
# @login_required
def news():
    category = request.args.get('category', default='')  # Get the category from the query parameter
    print(f"Navigated to /news with category: {category}")  # Debug log
    # Pass the category to the template
    return render_template('index.html', category=category)

@app.route('/analyze', methods=['POST'])
def analyze_article():
    data = request.json
    article_url = data.get('url', '')

    try:
        # Fetch the article content
        response = requests.get(article_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get all paragraphs and join them
        paragraphs = soup.find_all('p')
        article_content = ' '.join(p.get_text() for p in paragraphs)

        # Perform sentiment analysis
        blob = TextBlob(article_content)
        
        return jsonify({
            'content': article_content,
            'polarity': blob.sentiment.polarity,
            'subjectivity': blob.sentiment.subjectivity
        })
    except Exception as e:
        print(f"Error in analyze_article: {str(e)}")  # Debug log
        return jsonify({'error': str(e)}), 500

@app.route('/article')
# @login_required
def article():
    return render_template('article.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_page():
    if 'user_id' not in session and 'guest_id' not in session:
        session['guest_id'] = str(uuid.uuid4())
        session['guest'] = True
        print(f"Created new guest_id: {session['guest_id']}")

    if request.method == 'POST':
        article_url = request.form.get('article-url')
        print(f"Received URL: {article_url}")

        if not article_url.startswith(('http://', 'https://')):
            flash('Invalid URL format. Please enter a valid web address.', 'error')
            return render_template('upload.html', article_url=article_url)  # Stay on upload page with error

        try:
            user_id = session.get('user_id')
            guest_id = session.get('guest_id', 'anonymous')
            print(f"User ID: {user_id}, Guest ID: {guest_id}")

            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            if user_id:
                c.execute('INSERT INTO articles (user_id, url) VALUES (?, ?)', (user_id, article_url))
            else:
                c.execute('INSERT INTO articles (url, guest_id) VALUES (?, ?)', (article_url, guest_id))
            conn.commit()
            conn.close()
            flash('Article URL submitted successfully!', 'success')
            return render_template('upload.html', article_url='')  # Stay on upload page with cleared input

        except Exception as e:
            print(f"Database error: {str(e)}")
            flash(f'Error submitting article: {str(e)}', 'error')
            return render_template('upload.html', article_url=article_url)  # Stay on upload page with error

    return render_template('upload.html', article_url='')  # Initial GET request with empty input

def get_user_articles(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT url, submitted_at FROM articles WHERE user_id = ?', (user_id,))
    articles = c.fetchall()
    conn.close()
    return [{'url': row[0], 'submitted_at': row[1]} for row in articles]

if __name__ == '__main__':
    app.run(debug=True)
    