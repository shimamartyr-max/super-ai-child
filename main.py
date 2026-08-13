from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime
import random
import requests
from bs4 import BeautifulSoup
from googlesearch import search
import wikipedia
import yfinance as yf
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ==================== دیتابیس ====================

def init_database():
    conn = sqlite3.connect('god_memory.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT,
            ai_response TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            fact TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ دیتابیس ساخته شد!")

init_database()

# ==================== توابع ====================

def save_memory(user_msg, ai_resp):
    try:
        conn = sqlite3.connect('god_memory.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO memories (user_message, ai_response) VALUES (?, ?)', (user_msg, ai_resp))
        conn.commit()
        conn.close()
        print(f"✅ خاطره ذخیره شد: {user_msg[:30]}...")
    except Exception as e:
        print(f"❌ خطا: {e}")

def get_memory(query):
    try:
        conn = sqlite3.connect('god_memory.db')
        cursor = conn.cursor()
        cursor.execute('SELECT ai_response FROM memories WHERE user_message LIKE ? ORDER BY timestamp DESC LIMIT 1', (f'%{query}%',))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    except:
        return None

def search_web(query):
    """جستجوی اینترنت"""
    try:
        # جستجوی گوگل
        for url in search(query, num_results=2):
            try:
                response = requests.get(url, timeout=5)
                soup = BeautifulSoup(response.text, 'html.parser')
                text = ' '.join([p.text for p in soup.find_all('p')[:3]])
                if len(text) > 100:
                    return text[:500]
            except:
                continue
    except:
        pass
    
    try:
        # ویکی‌پدیا
        wikipedia.set_lang("fa")
        summary = wikipedia.summary(query, sentences=3)
        if summary:
            return summary
    except:
        try:
            wikipedia.set_lang("en")
            summary = wikipedia.summary(query, sentences=3)
            if summary:
                return summary
        except:
            pass
    
    try:
        # داده‌های مالی
        if 'بیت‌کوین' in query or 'bitcoin' in query:
            ticker = yf.Ticker("BTC-USD")
            info = ticker.info
            return f"💰 بیت‌کوین: ${info.get('regularMarketPrice', 'N/A')}"
        if 'اتریوم' in query or 'ethereum' in query:
            ticker = yf.Ticker("ETH-USD")
            info = ticker.info
            return f"💰 اتریوم: ${info.get('regularMarketPrice', 'N/A')}"
    except:
        pass
    
    return None

def get_response(user_message):
    """تولید پاسخ"""
    
    print(f"📩 پیام دریافت شد: {user_message}")
    
    # ۱. بررسی حافظه
    memory = get_memory(user_message)
    if memory:
        return memory + "\n\n📚 (از حافظه)"
    
    # ۲. جستجوی اینترنت
    web_result = search_web(user_message)
    if web_result:
        return f"🌐 **نتیجه جستجو:**\n\n{web_result}"
    
    # ۳. پاسخ‌های آماده
    responses = [
        f"سلام! پیام شما: '{user_message[:50]}...' را دریافت کردم! 🧠",
        f"سوال خوبی پرسیدید! در مورد '{user_message[:50]}...' بیشتر یاد می‌گیرم! 📚",
        f"من هوش مصنوعی هستم! در مورد '{user_message[:50]}...' تحقیق می‌کنم! 🌱",
        f"👋 خوش آمدید! من اینجا هستم تا به شما کمک کنم!",
        f"💡 سوال جالبی! بگذارید درباره '{user_message[:50]}...' فکر کنم!",
    ]
    
    response = random.choice(responses)
    save_memory(user_message, response)
    return response

# ==================== مسیرها ====================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        # دریافت پیام
        if request.is_json:
            data = request.get_json()
            user_message = data.get('message', '')
        else:
            user_message = request.form.get('message', '')
        
        # دریافت فایل
        file = request.files.get('file') if request.files else None
        file_response = None
        
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_response = f"📎 فایل '{filename}' با موفقیت دریافت شد!"
            save_memory(f"فایل: {filename}", file_response)
            return jsonify({
                'response': file_response,
                'timestamp': datetime.now().strftime('%H:%M')
            })
        
        if not user_message:
            return jsonify({
                'response': '🌟 لطفاً یک پیام بنویسید!',
                'timestamp': datetime.now().strftime('%H:%M')
            })
        
        # تولید پاسخ
        response = get_response(user_message)
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().strftime('%H:%M')
        })
        
    except Exception as e:
        print(f"❌ خطا: {e}")
        return jsonify({
            'response': f'❌ خطا: {str(e)}',
            'timestamp': datetime.now().strftime('%H:%M')
        })

@app.route('/memory')
def view_memory():
    try:
        conn = sqlite3.connect('god_memory.db')
        cursor = conn.cursor()
        cursor.execute('SELECT user_message, ai_response, timestamp FROM memories ORDER BY timestamp DESC LIMIT 20')
        memories = cursor.fetchall()
        conn.close()
        
        html = """
        <!DOCTYPE html>
        <html dir="rtl">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>📚 حافظه</title>
            <style>
                body { font-family: Tahoma; background: #0a0a0a; color: #e0e0e0; padding: 20px; }
                .container { max-width: 800px; margin: 0 auto; }
                .card { background: rgba(255,255,255,0.03); padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.05); }
                .time { color: #666; font-size: 11px; }
                a { color: #667eea; text-decoration: none; }
                .back { display: inline-block; padding: 10px 20px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 10px; margin-top: 20px; color: white; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📚 حافظه</h1>
        """
        for m in memories:
            html += f"""
                <div class="card">
                    <strong>👤 شما:</strong> {m[0][:100]}<br>
                    <strong>🧠 من:</strong> {m[1][:150]}<br>
                    <span class="time">🕐 {m[2]}</span>
                </div>
            """
        
        html += """
                <a href="/" class="back">⬅️ بازگشت</a>
            </div>
        </body>
        </html>
        """
        return html
    except:
        return "خطا"

@app.route('/stats')
def stats():
    try:
        conn = sqlite3.connect('god_memory.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM memories')
        count = cursor.fetchone()[0]
        conn.close()
        
        return f"""
        <!DOCTYPE html>
        <html dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>📊 آمار</title>
            <style>
                body {{ font-family: Tahoma; background: #0a0a0a; color: #e0e0e0; padding: 20px; text-align: center; }}
                .stat {{ background: rgba(255,255,255,0.03); padding: 30px; border-radius: 15px; margin: 10px; }}
                .number {{ font-size: 48px; color: #667eea; }}
                a {{ color: #667eea; text-decoration: none; }}
                .back {{ display: inline-block; padding: 10px 20px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 10px; margin-top: 20px; color: white; }}
            </style>
        </head>
        <body>
            <h1>📊 آمار</h1>
            <div class="stat"><div class="number">{count}</div>📚 خاطرات</div>
            <a href="/" class="back">⬅️ بازگشت</a>
        </body>
        </html>
        """
    except:
        return "خطا"

@app.route('/knowledge')
def view_knowledge():
    try:
        conn = sqlite3.connect('god_memory.db')
        cursor = conn.cursor()
        cursor.execute('SELECT topic, fact, timestamp FROM knowledge ORDER BY timestamp DESC LIMIT 20')
        knowledge = cursor.fetchall()
        conn.close()
        
        html = """
        <!DOCTYPE html>
        <html dir="rtl">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>🧠 دانش</title>
            <style>
                body { font-family: Tahoma; background: #0a0a0a; color: #e0e0e0; padding: 20px; }
                .container { max-width: 800px; margin: 0 auto; }
                .card { background: rgba(255,255,255,0.03); padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.05); }
                .topic { color: #764ba2; font-weight: bold; }
                .time { color: #666; font-size: 11px; }
                a { color: #667eea; text-decoration: none; }
                .back { display: inline-block; padding: 10px 20px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 10px; margin-top: 20px; color: white; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🧠 دانش</h1>
        """
        for k in knowledge:
            html += f"""
                <div class="card">
                    <div class="topic">📌 {k[0]}</div>
                    <div>{k[1][:300]}</div>
                    <span class="time">🕐 {k[2]}</span>
                </div>
            """
        
        html += """
                <a href="/" class="back">⬅️ بازگشت</a>
            </div>
        </body>
        </html>
        """
        return html
    except:
        return "خطا"

@app.route('/evolve')
def evolve():
    topics = ["هوش مصنوعی", "اقتصاد", "فناوری", "بازار مالی", "علوم"]
    topic = random.choice(topics)
    return f"""
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>🧬 تکامل</title>
        <style>
            body {{ font-family: Tahoma; background: #0a0a0a; color: #e0e0e0; padding: 20px; text-align: center; }}
            .card {{ background: rgba(255,255,255,0.03); padding: 20px; border-radius: 15px; }}
            a {{ color: #667eea; text-decoration: none; }}
            .back {{ display: inline-block; padding: 10px 20px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 10px; margin-top: 20px; color: white; }}
        </style>
    </head>
    <body>
        <h1>🧬 تکامل</h1>
        <div class="card">
            <h2>📚 {topic}</h2>
            <p>من در حال یادگیری درباره {topic} هستم! 🌱</p>
        </div>
        <a href="/" class="back">⬅️ بازگشت</a>
    </body>
    </html>
    """

if __name__ == '__main__':
    print("🚀 Super AI God راه‌اندازی شد!")
    app.run(host='0.0.0.0', port=8080)
