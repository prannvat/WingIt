import json
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from textblob import TextBlob
import requests
from bs4 import BeautifulSoup
from functools import wraps
import sqlite3
import hashlib
import os
from ai_analysis import AnalyserAI
app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management
ai_analyser = AnalyserAI()
# Database setup
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

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
    return render_template('index.html')

# @app.route('/analyze', methods=['POST'])
# def analyze_article():
#     data = request.json
#     article_url = data.get('url', '')

#     try:
#         # Fetch the article content
#         response = requests.get(article_url)
#         soup = BeautifulSoup(response.content, 'html.parser')
        
#         # Get all paragraphs and join them
#         paragraphs = soup.find_all('p')
#         article_content = ' '.join(p.get_text() for p in paragraphs)

#         # Perform sentiment analysis
#         blob = TextBlob(article_content)
        
#         return jsonify({
#             'content': article_content,
#             'polarity': blob.sentiment.polarity,
#             'subjectivity': blob.sentiment.subjectivity
#         })
#     except Exception as e:
#         print(f"Error in analyze_article: {str(e)}")  # Debug log
#         return jsonify({'error': str(e)}), 500

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

        # Use the AI analysis for both objectivity and tone instead of TextBlob
        objectivity_results = ai_analyser.analyse_objectivity(article_content)
        tone_results = ai_analyser.analyse_tone(article_content)
        
        result = {
            'content': article_content,
            'objectivity': objectivity_results,
            'tone': tone_results
        }
        
        result_json = json.dumps(result, indent=2)
        print("Analysis Result:", result_json)   # Debug log
        return result_json
    except Exception as e:
        print(f"Error in analyze_article: {str(e)}")  # Debug log
        return jsonify({'error': str(e)}), 500

@app.route('/article')
# @login_required
def article():
    return render_template('article.html')

if __name__ == '__main__':
    app.run(debug=True)


    