from curses import flash
from datetime import datetime
import json
import uuid
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from textblob import TextBlob
import requests
from bs4 import BeautifulSoup
from functools import wraps
import sqlite3
import hashlib
import os

from ai_analysis import AnalyserAI
from openai import APIConnectionError


app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management
ai_analyser = AnalyserAI()
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
    c.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            guest_id TEXT,
            url TEXT NOT NULL,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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


@app.route('/analyzeUpload', methods=['POST'])
def analyze_upload():
    data = request.json
    article_url = data.get('url', '')

    try:
        # Fetch the article content
        response = requests.get(article_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get all paragraphs and join them
        paragraphs = soup.find_all('p')
        article_content = ' '.join(p.get_text() for p in paragraphs)

        # Try to extract the title
        title = soup.find('title').get_text() if soup.find('title') else 'No title available'

        # Try to extract an image (if available)
        image = None
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            image = og_image['content']
        else:
            first_image = soup.find('img')
            if first_image and first_image.get('src'):
                image = first_image['src']
                
        # try:
        #     objectivity_results = ai_analyser.analyse_objectivity(article_content)
        #     tone_results = ai_analyser.analyse_tone(article_content)
        # except APIConnectionError as e:
        #     objectivity_results = [("Error", 0)]
        #     tone_results = [("Error", 0)]
        # Perform sentiment analysis
        blob = TextBlob(article_content)
        
        # Return a structured article object similar to News API format
        return jsonify({
            'title': title,
            'description': article_content[:200] + '...' if len(article_content) > 200 else article_content,
            'content': article_content,
            'url': article_url,
            'urlToImage': image,
            'source': {'name': soup.find('meta', property='og:site_name')['content'] if soup.find('meta', property='og:site_name') else 'Unknown Source'},
            'publishedAt': datetime.now().isoformat(),
            'polarity': blob.sentiment.polarity,
            'subjectivity': blob.sentiment.subjectivity
        })
    except Exception as e:
        print(f"Error in analyze_article: {str(e)}")  # Debug log
        return jsonify({'error': str(e)}), 500

    

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

        # Use the AI analysis for both objectivity and tone instead of TextBlob
        try:
            objectivity_results = ai_analyser.analyse_objectivity(article_content)
            tone_results = ai_analyser.analyse_tone(article_content)
        except APIConnectionError as e:
            objectivity_results = [("Error", 0)]
            tone_results = [("Error", 0)]
        
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
            return render_template('upload.html', article_url=article_url)

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
            # Return the submitted URL in the response for JavaScript to use
            return jsonify({'success': True, 'article_url': article_url})
        except Exception as e:
            print(f"Database error: {str(e)}")
            flash(f'Error submitting article: {str(e)}', 'error')
            return jsonify({'success': False, 'error': str(e)}), 500

    return render_template('upload.html', article_url='')

@app.route('/recent_article', methods=['GET'])
def get_recent_article():
    try:
        user_id = session.get('user_id')
        guest_id = session.get('guest_id', 'anonymous')

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        if user_id:
            c.execute('SELECT url FROM articles WHERE user_id = ? ORDER BY submitted_at DESC LIMIT 1', (user_id,))
        else:
            c.execute('SELECT url FROM articles WHERE guest_id = ? ORDER BY submitted_at DESC LIMIT 1', (guest_id,))
        article = c.fetchone()
        conn.close()

        if article:
            return jsonify({'success': True, 'article_url': article[0]})
        else:
            return jsonify({'success': False, 'error': 'No articles found'})
    except Exception as e:
        print(f"Error fetching recent article: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def get_user_articles(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT url, submitted_at FROM articles WHERE user_id = ?', (user_id,))
    articles = c.fetchall()
    conn.close()
    return [{'url': row[0], 'submitted_at': row[1]} for row in articles]

if __name__ == '__main__':
    app.run(debug=True)

