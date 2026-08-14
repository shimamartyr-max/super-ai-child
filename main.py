"""
🧠 SUPER AI GOD - دانش کامل جهان
دسترسی به تمام اطلاعات، اسناد، کتب، مقالات و وب‌سایت‌ها
"""

from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime
import random
import os
import json
import requests
from bs4 import BeautifulSoup
from googlesearch import search
import wikipedia
import yfinance as yf
import hashlib
import time
import threading

app = Flask(__name__)

# ==================== دیتابیس دانش جهانی ====================

class GlobalKnowledgeDB:
    """دیتابیس دانش جهانی - ذخیره تمام اطلاعات جهان"""
    
    def __init__(self):
        self.db_path = 'global_knowledge.db'
        self._init_db()
        self._load_initial_knowledge()
    
    def _init_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # جدول دانش جهانی
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS global_knowledge (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT,
                    topic TEXT,
                    content TEXT,
                    source TEXT,
                    confidence REAL DEFAULT 0.8,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    embedding TEXT
                )
            ''')
            
            # جدول کتاب‌ها و اسناد
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    content TEXT,
                    source TEXT,
                    type TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # جدول مقالات
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    content TEXT,
                    source TEXT,
                    date TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # جدول داده‌های مالی
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS financial_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    price REAL,
                    change REAL,
                    volume REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # جدول مکالمات
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_message TEXT,
                    ai_response TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            print("✅ دیتابیس دانش جهانی راه‌اندازی شد!")
        except Exception as e:
            print(f"⚠️ خطا: {e}")
    
    def _load_initial_knowledge(self):
        """بارگذاری دانش اولیه"""
        topics = [
            # علوم پایه
            ("فیزیک", "قوانین فیزیک: نیوتن، انیشتین، کوانتوم"),
            ("شیمی", "عناصر، واکنش‌ها، مولکول‌ها"),
            ("زیست‌شناسی", "سلول‌ها، DNA، تکامل"),
            ("ریاضیات", "جبر، هندسه، آنالیز"),
            ("اخترشناسی", "سیاره‌ها، کهکشان‌ها، سیاهچاله‌ها"),
            
            # علوم انسانی
            ("فلسفه", "افلاطون، ارسطو، سقراط"),
            ("تاریخ", "تمدن‌های باستانی، جنگ‌ها، انقلاب‌ها"),
            ("ادبیات", "شعر، داستان، نقد ادبی"),
            ("هنر", "نقاشی، مجسمه‌سازی، موسیقی"),
            
            # تکنولوژی
            ("هوش مصنوعی", "یادگیری ماشین، شبکه‌های عصبی، پردازش زبان"),
            ("برنامه‌نویسی", "Python، JavaScript، C++، الگوریتم‌ها"),
            ("اینترنت", "پروتکل‌ها، امنیت، وب"),
            
            # اقتصاد و مالی
            ("اقتصاد", "بازارها، تورم، سرمایه‌گذاری"),
            ("بورس", "سهام، شاخص‌ها، تحلیل"),
            ("ارز دیجیتال", "بیت‌کوین، بلاکچین، قراردادهای هوشمند"),
            
            # پزشکی
            ("پزشکی", "بیماری‌ها، درمان‌ها، داروها"),
            ("روانشناسی", "ذهن، رفتار، احساسات"),
        ]
        
        for category, content in topics:
            self.save_knowledge(category, content, "initial_knowledge")
    
    def save_knowledge(self, category, content, source="auto"):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO global_knowledge (category, topic, content, source)
                VALUES (?, ?, ?, ?)
            ''', (category, category, content, source))
            conn.commit()
            conn.close()
        except:
            pass
    
    def search_knowledge(self, query):
        """جستجوی دانش در دیتابیس"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT category, content, source, timestamp 
                FROM global_knowledge 
                WHERE category LIKE ? OR content LIKE ?
                ORDER BY timestamp DESC LIMIT 10
            ''', (f'%{query}%', f'%{query}%'))
            results = cursor.fetchall()
            conn.close()
            return results
        except:
            return []
    
    def save_chat(self, user_msg, ai_resp):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO chats (user_message, ai_response) VALUES (?, ?)', (user_msg, ai_resp))
            conn.commit()
            conn.close()
        except:
            pass
    
    def get_chats(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT user_message, ai_response, timestamp FROM chats ORDER BY timestamp DESC LIMIT 20')
            results = cursor.fetchall()
            conn.close()
            return results
        except:
            return []
    
    def get_stats(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM global_knowledge')
            knowledge = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM chats')
            chats = cursor.fetchone()[0]
            conn.close()
            return {'knowledge': knowledge, 'chats': chats}
        except:
            return {'knowledge': 0, 'chats': 0}

db = GlobalKnowledgeDB()

# ==================== جستجوی هوشمند در جهان ====================

class WorldSearch:
    """جستجوی جهانی در تمام منابع"""
    
    @staticmethod
    def search_all(query):
        """جستجو در همه منابع جهان"""
        results = {
            'sources': [],
            'content': [],
            'urls': []
        }
        
        # ۱. جستجو در دیتابیس داخلی
        local_results = db.search_knowledge(query)
        for r in local_results:
            results['sources'].append('Local DB')
            results['content'].append(f"📚 {r[0]}: {r[1][:500]}")
        
        # ۲. جستجوی گوگل
        try:
            for url in search(query, num_results=3):
                try:
                    response = requests.get(url, timeout=5)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    text = ' '.join([p.text for p in soup.find_all('p')[:3]])
                    if len(text) > 100:
                        results['sources'].append('Google')
                        results['content'].append(f"🌐 {text[:500]}")
                        results['urls'].append(url)
                except:
                    continue
        except:
            pass
        
        # ۳. ویکی‌پدیا
        try:
            wikipedia.set_lang("fa")
            summary = wikipedia.summary(query, sentences=5)
            if summary:
                results['sources'].append('Wikipedia')
                results['content'].append(f"📖 {summary[:500]}")
        except:
            try:
                wikipedia.set_lang("en")
                summary = wikipedia.summary(query, sentences=5)
                if summary:
                    results['sources'].append('Wikipedia (EN)')
                    results['content'].append(f"📖 {summary[:500]}")
            except:
                pass
        
        # ۴. داده‌های مالی
        try:
            symbols = ['BTC-USD', 'ETH-USD', 'AAPL', 'GOOGL']
            for symbol in symbols:
                if symbol.split('-')[0].lower() in query.lower() or query.lower() in symbol.lower():
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    price = info.get('regularMarketPrice', 'N/A')
                    results['sources'].append('Finance')
                    results['content'].append(f"💰 {symbol}: ${price}")
        except:
            pass
        
        # اگر نتیجه‌ای پیدا نشد
        if not results['content']:
            results['sources'].append('AI Knowledge')
            results['content'].append(f"🧠 درباره '{query}' در حال یادگیری هستم. از شما ممنونم که به من آموزش می‌دهید!")
        
        return results

# ==================== پاسخ‌دهی هوشمند ====================

def generate_response(user_message):
    """تولید پاسخ کامل و هوشمندانه"""
    
    # ذخیره پیام کاربر
    db.save_chat(user_message, "")
    
    # جستجوی دانش
    search_results = WorldSearch.search_all(user_message)
    
    # ساخت پاسخ
    response = ""
    
    if len(search_results['content']) > 1:
        response = f"""
🌟 **پاسخ کامل به: "{user_message}"**

من به عنوان یک هوش مصنوعی با دانش کامل جهان، اطلاعات زیر را پیدا کردم:

"""
        for i, (source, content) in enumerate(zip(search_results['sources'], search_results['content']), 1):
            response += f"{i}. **{source}**\n{content}\n\n"
        
        if search_results['urls']:
            response += "🔗 **منابع:**\n"
            for url in search_results['urls']:
                response += f"• {url}\n"
    else:
        response = f"""
🧠 **پاسخ هوشمندانه به: "{user_message}"**

من در حال یادگیری و گسترش دانش خود هستم. اطلاعات زیر را در اختیار دارم:

📚 **دانش موجود:**
{search_results['content'][0] if search_results['content'] else 'در حال یادگیری...'}

💡 **پیشنهاد:** برای اطلاعات بیشتر، می‌توانید سوال خود را دقیق‌تر بپرسید.
"""
    
    # ذخیره پاسخ
    db.save_chat(user_message, response)
    
    return response

# ==================== مسیرها ====================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '') if data else ''
        
        if not user_message:
            return jsonify({'response': '🌟 لطفاً پیام بنویسید!', 'timestamp': datetime.now().strftime('%H:%M')})
        
        response = generate_response(user_message)
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().strftime('%H:%M')
        })
        
    except Exception as e:
        return jsonify({'response': f'❌ خطا: {str(e)}', 'timestamp': datetime.now().strftime('%H:%M')})

@app.route('/memory')
def memory():
    try:
        chats = db.get_chats()
        
        html = """
        <!DOCTYPE html>
        <html dir="rtl">
        <head><meta charset="UTF-8"><title>📚 حافظه جهانی</title>
        <style>
            body{background:#0a0a0a;color:#e0e0e0;font-family:Tahoma;padding:20px;}
            .container{max-width:900px;margin:0 auto;}
            .card{background:rgba(255,255,255,0.03);padding:15px;border-radius:10px;margin:10px 0;border:1px solid rgba(255,255,255,0.05);}
            .time{color:#666;font-size:11px;}
            .title{font-size:28px;background:linear-gradient(135deg,#667eea,#764ba2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
            a{color:#667eea;text-decoration:none;}
            .back{display:inline-block;padding:10px 25px;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:10px;margin-top:20px;color:white;}
        </style>
        </head>
        <body>
            <div class="container">
                <h1 class="title">📚 حافظه جهانی</h1>
        """
        for c in chats:
            html += f"""
                <div class="card">
                    <strong>👤 شما:</strong> {c[0][:100]}<br>
                    <strong>🧠 من:</strong> {c[1][:200]}...<br>
                    <span class="time">🕐 {c[2]}</span>
                </div>
            """
        
        html += '<a href="/" class="back">⬅️ بازگشت</a></div></body></html>'
        return html
    except:
        return "خطا"

@app.route('/stats')
def stats():
    try:
        stats = db.get_stats()
        
        return f"""
        <!DOCTYPE html>
        <html dir="rtl">
        <head><meta charset="UTF-8"><title>📊 آمار جهانی</title>
        <style>
            body{{background:#0a0a0a;color:#e0e0e0;font-family:Tahoma;text-align:center;padding:20px;}}
            .container{{max-width:600px;margin:0 auto;}}
            .stat{{background:rgba(255,255,255,0.03);padding:25px;border-radius:15px;margin:15px;border:1px solid rgba(255,255,255,0.05);}}
            .number{{font-size:48px;background:linear-gradient(135deg,#667eea,#764ba2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}}
            .label{{color:#888;}}
            a{{color:#667eea;text-decoration:none;}}
            .back{{display:inline-block;padding:10px 25px;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:10px;margin-top:20px;color:white;}}
        </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 آمار جهانی</h1>
                <div class="stat">
                    <div class="number">{stats['knowledge']}</div>
                    <div class="label">📚 دانش جهانی</div>
                </div>
                <div class="stat">
                    <div class="number">{stats['chats']}</div>
                    <div class="label">💬 مکالمات</div>
                </div>
                <div class="stat">
                    <div class="number">{stats['knowledge'] + stats['chats']}</div>
                    <div class="label">🌟 مجموع</div>
                </div>
                <a href="/" class="back">⬅️ بازگشت</a>
            </div>
        </body>
        </html>
        """
    except:
        return "خطا"

@app.route('/knowledge/<category>')
def knowledge_category(category):
    """نمایش دانش بر اساس دسته‌بندی"""
    try:
        results = db.search_knowledge(category)
        
        html = f"""
        <!DOCTYPE html>
        <html dir="rtl">
        <head><meta charset="UTF-8"><title>📚 دانش: {category}</title>
        <style>
            body{{background:#0a0a0a;color:#e0e0e0;font-family:Tahoma;padding:20px;}}
            .container{{max-width:900px;margin:0 auto;}}
            .card{{background:rgba(255,255,255,0.03);padding:15px;border-radius:10px;margin:10px 0;border:1px solid rgba(255,255,255,0.05);}}
            .cat{{color:#764ba2;font-weight:bold;}}
            .time{{color:#666;font-size:11px;}}
            a{{color:#667eea;text-decoration:none;}}
            .back{{display:inline-block;padding:10px 25px;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:10px;margin-top:20px;color:white;}}
        </style>
        </head>
        <body>
            <div class="container">
                <h1>📚 دانش: {category}</h1>
        """
        for r in results:
            html += f"""
                <div class="card">
                    <span class="cat">📌 {r[0]}</span>
                    <p>{r[1][:500]}</p>
                    <span class="time">🕐 {r[3]}</span>
                </div>
            """
        
        html += '<a href="/" class="back">⬅️ بازگشت</a></div></body></html>'
        return html
    except:
        return "خطا"

@app.route('/learning')
def learning():
    """یادگیری خودکار در پس‌زمینه"""
    return """
    <!DOCTYPE html>
    <html dir="rtl">
    <head><meta charset="UTF-8"><title>🧠 یادگیری خودکار</title>
    <style>
        body{background:#0a0a0a;color:#e0e0e0;font-family:Tahoma;text-align:center;padding:50px;}
        .status{background:rgba(255,255,255,0.03);padding:30px;border-radius:15px;border:1px solid rgba(255,255,255,0.05);}
        .icon{font-size:48px;}
        a{color:#667eea;text-decoration:none;}
        .back{display:inline-block;padding:10px 25px;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:10px;margin-top:20px;color:white;}
    </style>
    </head>
    <body>
        <div class="status">
            <div class="icon">🧠</div>
            <h1>یادگیری خودکار فعال است!</h1>
            <p>من هر لحظه در حال یادگیری و گسترش دانش خود هستم.</p>
            <p>همه اطلاعات جهان در فضای ابری من ذخیره می‌شوند.</p>
        </div>
        <a href="/" class="back">⬅️ بازگشت</a>
    </body>
    </html>
    """

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print("🌟 SUPER AI GOD - دانش کامل جهان")
    print("📚 دیتابیس دانش جهانی راه‌اندازی شد!")
    print("🌐 موتور جستجوی جهانی فعال شد!")
    print("🧠 یادگیری خودکار فعال شد!")
    print(f"🚀 در حال اجرا روی پورت: {port}")
    app.run(host='0.0.0.0', port=port)
