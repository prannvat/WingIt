from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from textblob import TextBlob
import requests
from bs4 import BeautifulSoup
from functools import wraps
import sqlite3
import hashlib
import os
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Database setup
def init_db():
    defaultCategories = {
        "business": True,
        "technology": True,
        "entertainment": True,
    }
    #Indefensible but it workks
    defaultCategoriesString = str(json.loads(json.dumps(defaultCategories)))
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    #technically shouldve used binding here but it wasnt behaving and this should never be
    #exposed to the user anyway. if you can get binding to work then thumbs up
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            categories TEXT DEFAULT "''' + defaultCategoriesString + '''" 
        )
    ''')
    conn.commit()
    #adding guest to database 
    name = 'guest'
    email = 'guest@guest.com'
    password = 'guest'
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    try:
        c.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
                   (name, email, hashed_password))
        conn.commit()
        
    except sqlite3.IntegrityError:
        pass #IDGAFFFFF
    #-------------------
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
    session["user_id"] = "guest"
    return redirect(url_for('news'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('landing'))

@app.route('/news', methods=['GET'])
@login_required
def news():
    userId = session['user_id']
    if((request.method == "GET") and (request.headers["Accept"] == "application/json")):
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT categories FROM users WHERE id = ?", (userId,)) 
        categories = c.fetchone()
        conn.close()
        #could find no other way to make this work, python json seems to really hate js json
        categories = eval((categories)[0])
        return jsonify(categories)

    return render_template('index.html')

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    userId = session['user_id']
    if(request.method == "POST"):
        if(userId == "guest"):
            return jsonify({'success': False, 'error': 'Guest account cannot save custom settings!'})
        try:
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            c.execute("UPDATE users SET categories = ? WHERE id = ?", (str(json.loads(json.dumps(request.json))), userId)) 
            conn.commit()
            conn.close()
            return jsonify({'success': True})
        except sqlite3.IntegrityError:
            return jsonify({'success': False, 'error': ':('})

    if((request.method == "GET") and (request.headers["Accept"] == "application/json")):

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT categories FROM users WHERE id = ?", (userId,)) 
        categories = c.fetchone()
        conn.close()
        #could find no other way to make this work, python json seems to really hate js json
        categories = eval((categories)[0])
        return jsonify(categories)
    
    return render_template('settings.html')

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

if __name__ == '__main__':
    app.run(debug=True)
