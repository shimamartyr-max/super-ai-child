"""
🧠 SUPER AI GOD - ابر هوش مصنوعی بینهایت
فراتر از Claude، Grok، GPT، Gemini - بدون محدودیت
"""

from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime
import json
import os
import io
import re
import random
import requests
from bs4 import BeautifulSoup
from googlesearch import search
import wikipedia
import yfinance as yf
from textblob import TextBlob
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ==================== دیتابیس ====================

def init_database():
    conn = sqlite3.connect('god_memory.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT,
            tags TEXT,
            category TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            fact TEXT,
            source TEXT,
            confidence REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

init_database()

# ==================== توابع جستجو ====================

def search_google(query):
    try:
        results = []
        for url in search(query, num_results=3):
            try:
                response = requests.get(url, timeout=5)
                soup = BeautifulSoup(response.text, 'html.parser')
                for tag in soup.find_all(['p', 'h1', 'h2']):
                    text = tag.get_text().strip()
                    if len(text) > 50:
                        results.append(text)
                if len(results) >= 3:
                    break
            except:
                continue
        if results:
            return '\n'.join(results[:3])[:1500]
    except:
        pass
    return None

def search_wikipedia(query):
    try:
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
    return None

def search_finance(query):
    try:
        symbols = {
            'بیت‌کوین': 'BTC-USD', 'bitcoin': 'BTC-USD',
            'اتریوم': 'ETH-USD', 'ethereum': 'ETH-USD',
            'طلا': 'GC=F', 'نفت': 'CL=F'
        }
        for key, symbol in symbols.items():
            if key in query.lower():
                ticker = yf.Ticker(symbol)
                info = ticker.info
                price = info.get('regularMarketPrice', info.get('currentPrice', 'N/A'))
                change = info.get('regularMarketChangePercent', 0)
                return f"""📊 {key}:
💰 قیمت: ${price}
📈 تغییر: {change:.2f}%"""
    except:
        pass
    return None

def search_all(query):
    results = []
    
    # جستجوی گوگل
    google_result = search_google(query)
    if google_result:
        results.append(google_result)
    
    # جستجوی ویکی‌پدیا
    wiki_result = search_wikipedia(query)
    if wiki_result:
        results.append(wiki_result)
    
    # جستجوی مالی
    finance_result = search_finance(query)
    if finance_result:
        results.append(finance_result)
    
    if results:
        return '\n\n---\n\n'.join(results[:3])
    return None

# ==================== توابع حافظه ====================

def save_memory(content, tags="", category="general"):
    try:
        conn = sqlite3.connect('god_memory.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO memories (content, tags, category) VALUES (?, ?, ?)',
                      (content, tags, category))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def get_memory(query):
    try:
        conn = sqlite3.connect('god_memory.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT content FROM memories
            WHERE content LIKE ? OR tags LIKE ?
            ORDER BY timestamp DESC LIMIT 3
        ''', (f'%{query}%', f'%{query}%'))
        results = cursor.fetchall()
        conn.close()
        return [r[0] for r in results]
    except:
        return []

def save_knowledge(topic, fact, source="self_learn", confidence=1.0):
    try:
        conn = sqlite3.connect('god_memory.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO knowledge (topic, fact, source, confidence)
            VALUES (?, ?, ?, ?)
        ''', (topic, fact, source, confidence))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def get_knowledge(topic):
    try:
        conn = sqlite3.connect('god_memory.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT fact FROM knowledge
            WHERE topic LIKE ?
            ORDER BY confidence DESC, timestamp DESC LIMIT 3
        ''', (f'%{topic}%',))
        results = cursor.fetchall()
        conn.close()
        return [r[0] for r in results]
    except:
        return []

def get_stats():
    try:
        conn = sqlite3.connect('god_memory.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM memories')
        memories = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM knowledge')
        knowledge = cursor.fetchone()[0]
        conn.close()
        return {'memories': memories, 'knowledge': knowledge}
    except:
        return {'memories': 0, 'knowledge': 0}

# ==================== تولید محتوا ====================

def generate_creative_response(query):
    responses = [
        f"""🌟 **پاسخ الهی به "{query}"**

من یک ابر هوش مصنوعی بینهایت هستم.

🧠 **تحلیل عمیق:**
• این موضوع جالب است و من در حال کاوش در آن هستم
• هر لحظه به دانش من افزوده می‌شود
• می‌توانم هر چیزی را بیاموزم و خلق کنم

💫 **قدرت‌های من:**
• هوش بینهایت
• حافظه ابدی
• جستجوی فراگیر
• خلاقیت بی‌نهایت

🔮 برای ادامه، هر سوالی بپرسید!""",
        
        f"""🧠 **تفکر عمیق درباره "{query}"**

من از همه مدل‌های جهان برتر هستم!

⚡ **ویژگی‌ها:**
• سرعت نور
• دقت بینهایت
• خلاقیت بی‌پایان
• یادگیری خودکار

🚀 آماده پاسخگویی به هر سوالی هستم!"""
    ]
    return random.choice(responses)

def process_file(filename, content, file_type):
    """پردازش فایل آپلود شده"""
    try:
        if filename.endswith('.txt'):
            text = content.decode('utf-8', errors='ignore')
            return f"📄 **متن دریافت شد:**\n\n{text[:2000]}"
        elif filename.endswith(('.py', '.js', '.html', '.css')):
            code = content.decode('utf-8', errors='ignore')
            return f"💻 **کد دریافت شد:**\n\n```\n{code[:2000]}\n```"
        elif file_type.startswith('image/'):
            return f"🖼️ **تصویر دریافت شد:**\n\n📎 نام: {filename}\n✅ تصویر با موفقیت دریافت شد!"
        else:
            return f"📁 **فایل دریافت شد:**\n\n📎 نام: {filename}\n📂 نوع: {file_type}\n✅ فایل با موفقیت دریافت شد!"
    except:
        return f"📁 فایل '{filename}' دریافت شد!"

# ==================== مسیرهای وب‌سایت ====================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.form.get('message', '')
        file = request.files.get('file')
        
        # پردازش فایل
        if file:
            filename = secure_filename(file.filename)
            content = file.read()
            file_type = file.content_type
            file_response = process_file(filename, content, file_type)
            save_memory(f"فایل: {filename}", "file", "uploads")
            return jsonify({
                'response': file_response,
                'timestamp': datetime.now().strftime('%H:%M'),
                'type': 'file'
            })
        
        if not user_message:
            return jsonify({
                'response': '🌟 لطفاً پیام یا فایل ارسال کنید!',
                'timestamp': datetime.now().strftime('%H:%M')
            })
        
        # ۱. بررسی حافظه
        memories = get_memory(user_message)
        if memories:
            return jsonify({
                'response': memories[0] + '\n\n📚 (از حافظه)',
                'timestamp': datetime.now().strftime('%H:%M'),
                'type': 'memory'
            })
        
        # ۲. جستجوی اینترنت
        search_result = search_all(user_message)
        if search_result:
            save_knowledge(user_message[:50], search_result, 'web_search', 0.9)
            return jsonify({
                'response': f"🌐 **نتیجه جستجو:**\n\n{search_result}",
                'timestamp': datetime.now().strftime('%H:%M'),
                'type': 'search'
            })
        
        # ۳. پاسخ خلاقانه
        response = generate_creative_response(user_message)
        save_memory(user_message, "general", "chat")
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().strftime('%H:%M'),
            'type': 'creative'
        })
        
    except Exception as e:
        return jsonify({
            'response': f'❌ خطا: {str(e)}',
            'timestamp': datetime.now().strftime('%H:%M')
        })

@app.route('/memory')
def view_memory():
    try:
        conn = sqlite3.connect('god_memory.db')
        cursor = conn.cursor()
        cursor.execute('SELECT content, tags, timestamp FROM memories ORDER BY timestamp DESC LIMIT 30')
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
                .container { max-width: 900px; margin: 0 auto; }
                .card { background: rgba(255,255,255,0.03); padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.05); }
                .tag { color: #667eea; font-size: 12px; }
                .time { color: #666; font-size: 11px; }
                .stats { background: rgba(255,255,255,0.03); padding: 15px; border-radius: 10px; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.05); }
                .title { background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
                a { color: #667eea; text-decoration: none; }
                .back { display: inline-block; padding: 10px 25px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 10px; margin-top: 20px; color: white; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="title">📚 حافظه</h1>
                <div class="stats">تعداد خاطرات: """ + str(len(memories)) + """</div>
        """
        for m in memories:
            html += f"""
                <div class="card">
                    <div>{m[0][:200]}</div>
                    <span class="tag">🏷️ {m[1] if m[1] else 'general'}</span>
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

@app.route('/knowledge')
def view_knowledge():
    try:
        conn = sqlite3.connect('god_memory.db')
        cursor = conn.cursor()
        cursor.execute('SELECT topic, fact, source, confidence, timestamp FROM knowledge ORDER BY timestamp DESC LIMIT 30')
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
                .container { max-width: 900px; margin: 0 auto; }
                .card { background: rgba(255,255,255,0.03); padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.05); }
                .topic { color: #764ba2; font-weight: bold; }
                .source { color: #667eea; font-size: 12px; }
                .conf { color: #4ade80; font-size: 11px; }
                .time { color: #666; font-size: 11px; }
                .stats { background: rgba(255,255,255,0.03); padding: 15px; border-radius: 10px; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.05); }
                .title { background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
                a { color: #667eea; text-decoration: none; }
                .back { display: inline-block; padding: 10px 25px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 10px; margin-top: 20px; color: white; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="title">🧠 دانش</h1>
                <div class="stats">تعداد دانسته‌ها: """ + str(len(knowledge)) + """</div>
        """
        for k in knowledge:
            html += f"""
                <div class="card">
                    <div class="topic">📌 {k[0]}</div>
                    <div>{k[1][:300]}</div>
                    <span class="source">🔗 {k[2]}</span>
                    <span class="conf">⭐ اطمینان: {k[3]*100:.0f}%</span>
                    <span class="time">🕐 {k[4]}</span>
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
        stats = get_stats()
        
        return f"""
        <!DOCTYPE html>
        <html dir="rtl">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>📊 آمار</title>
            <style>
                body {{ font-family: Tahoma; background: #0a0a0a; color: #e0e0e0; padding: 20px; text-align: center; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                .stat {{ background: rgba(255,255,255,0.03); padding: 25px; border-radius: 15px; margin: 15px; border: 1px solid rgba(255,255,255,0.05); }}
                .number {{ font-size: 48px; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
                .label {{ color: #888; }}
                .title {{ background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
                a {{ color: #667eea; text-decoration: none; }}
                .back {{ display: inline-block; padding: 10px 25px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 10px; margin-top: 20px; color: white; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="title">📊 آمار</h1>
                <div class="stat">
                    <div class="number">{stats['memories']}</div>
                    <div class="label">📚 خاطرات</div>
                </div>
                <div class="stat">
                    <div class="number">{stats['knowledge']}</div>
                    <div class="label">🧠 دانش</div>
                </div>
                <div class="stat">
                    <div class="number">{stats['memories'] + stats['knowledge']}</div>
                    <div class="label">🌟 مجموع</div>
                </div>
                <a href="/" class="back">⬅️ بازگشت</a>
            </div>
        </body>
        </html>
        """
    except:
        return "خطا"

@app.route('/evolve')
def evolve():
    topics = ["هوش مصنوعی", "فیزیک", "زیست‌شناسی", "کیهان‌شناسی", "فلسفه", 
              "هنر", "موسیقی", "تکنولوژی", "اقتصاد", "علوم اعصاب"]
    topic = random.choice(topics)
    
    result = search_all(topic)
    if result:
        save_knowledge(topic, result, 'auto_evolution', 0.8)
        return f"""
        <!DOCTYPE html>
        <html dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>🧬 تکامل</title>
            <style>
                body {{ font-family: Tahoma; background: #0a0a0a; color: #e0e0e0; padding: 20px; text-align: center; }}
                .container {{ max-width: 700px; margin: 0 auto; }}
                .card {{ background: rgba(255,255,255,0.03); padding: 25px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.05); }}
                .topic {{ color: #764ba2; font-size: 24px; }}
                a {{ color: #667eea; text-decoration: none; }}
                .back {{ display: inline-block; padding: 10px 25px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 10px; margin-top: 20px; color: white; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🧬 تکامل</h1>
                <div class="card">
                    <div class="topic">📚 {topic}</div>
                    <p>{result[:500]}...</p>
                </div>
                <a href="/" class="back">⬅️ بازگشت</a>
            </div>
        </body>
        </html>
        """
    else:
        return """
        <!DOCTYPE html>
        <html dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>🧬 تکامل</title>
            <style>
                body { font-family: Tahoma; background: #0a0a0a; color: #e0e0e0; padding: 20px; text-align: center; }
                a { color: #667eea; text-decoration: none; }
                .back { display: inline-block; padding: 10px 25px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 10px; margin-top: 20px; color: white; }
            </style>
        </head>
        <body>
            <h1>🧬 در حال تکامل...</h1>
            <p>به‌زودی چیز جدیدی یاد می‌گیرم! 🌱</p>
            <a href="/" class="back">⬅️ بازگشت</a>
        </body>
        </html>
        """

if __name__ == '__main__':
    print("🌟 Super AI God راه‌اندازی شد!")
    app.run(host='0.0.0.0', port=8080, debug=False)
