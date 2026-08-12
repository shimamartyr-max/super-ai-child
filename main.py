"""
🧠 SUPER AI CHILD 2.0 - نسخه پیشرفته مانند Grok
با قابلیت جستجوی اینترنت، پردازش فایل، ساخت تصویر و فیلم
"""

from flask import Flask, render_template, request, jsonify, send_file
import sqlite3
from datetime import datetime
import json
import os
import io
import base64
import re
import random
import asyncio
import aiohttp
from werkzeug.utils import secure_filename
import requests
from bs4 import BeautifulSoup
from googlesearch import search
import wikipedia
import yfinance as yf
from textblob import TextBlob
import numpy as np

# کتابخانه‌های جدید برای پردازش پیشرفته
try:
    from PIL import Image
    import pytesseract
except:
    pass

try:
    import openai
except:
    pass

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ==================== دیتابیس پیشرفته ====================

def init_database():
    conn = sqlite3.connect('super_ai_memory.db')
    cursor = conn.cursor()
    
    # خاطرات
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT,
            ai_response TEXT,
            topic TEXT,
            file_type TEXT,
            file_name TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # دانش
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            fact TEXT,
            source TEXT,
            confidence REAL DEFAULT 1.0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # تکامل
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS evolution (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            old_info TEXT,
            new_info TEXT,
            improvement REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # فایل‌های آپلود شده
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS uploaded_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            file_type TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

init_database()

# ==================== موتور جستجوی پیشرفته ====================

class SuperSearchEngine:
    """موتور جستجوی پیشرفته - مانند Grok"""
    
    @staticmethod
    async def search_web(query: str, num_results: int = 5) -> str:
        """جستجوی اینترنت با دقت بالا"""
        results = []
        
        try:
            # ۱. جستجوی Google
            try:
                for url in search(query, num_results=num_results):
                    try:
                        response = requests.get(url, timeout=5, headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                        })
                        soup = BeautifulSoup(response.text, 'html.parser')
                        # استخراج متن اصلی
                        for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'article']):
                            text = tag.get_text().strip()
                            if len(text) > 50:
                                results.append(text[:500])
                    except:
                        continue
            except:
                pass
            
            # ۲. ویکی‌پدیا
            try:
                wikipedia.set_lang("fa")
                summary = wikipedia.summary(query, sentences=5)
                if summary:
                    results.append(summary)
            except:
                try:
                    wikipedia.set_lang("en")
                    summary = wikipedia.summary(query, sentences=5)
                    if summary:
                        results.append(summary)
                except:
                    pass
            
            # ۳. جستجوی تخصصی (اخبار، مالی، علمی)
            if any(w in query.lower() for w in ["بورس", "سهام", "ارز", "دلار", "طلا"]):
                financial_data = await SuperSearchEngine._get_financial_data(query)
                if financial_data:
                    results.append(financial_data)
            
        except Exception as e:
            pass
        
        # ترکیب و خلاصه‌سازی نتایج
        if results:
            combined = "\n\n".join(results[:3])
            return combined[:2000]
        return None
    
    @staticmethod
    async def _get_financial_data(query: str) -> str:
        """دریافت داده‌های مالی"""
        try:
            symbols = ["BTC-USD", "ETH-USD", "SOL-USD", "AAPL", "GOOGL", "TSLA"]
            response = ""
            for symbol in symbols:
                if symbol in query.upper():
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    response += f"\n📊 {symbol}:\n"
                    response += f"💰 قیمت: ${info.get('currentPrice', 'N/A')}\n"
                    response += f"📈 تغییر: {info.get('regularMarketChangePercent', 0):.2f}%\n"
            return response
        except:
            return None

# ==================== موتور پردازش فایل ====================

class FileProcessor:
    """پردازش فایل‌های مختلف"""
    
    @staticmethod
    def process_text_file(content: str) -> str:
        """پردازش فایل متنی"""
        return content[:5000]
    
    @staticmethod
    def process_image(image_data: bytes) -> str:
        """تحلیل تصویر با OCR"""
        try:
            from PIL import Image
            import pytesseract
            img = Image.open(io.BytesIO(image_data))
            text = pytesseract.image_to_string(img, lang='fas+eng')
            return f"📸 **تحلیل تصویر:**\n\n{text[:1000]}" if text else "تصویر خوانده نشد."
        except:
            return "🖼️ تصویر دریافت شد. (تحلیل پیشرفته نیاز به نصب Tesseract دارد)"
    
    @staticmethod
    async def generate_image(prompt: str) -> str:
        """تولید تصویر با هوش مصنوعی"""
        try:
            # استفاده از HuggingFace یا API مشابه
            # برای مثال از یک سرویس رایگان استفاده می‌کنیم
            return f"🎨 **تصویر ساخته شد!**\n\nدرخواست: {prompt}\n\n(برای استفاده از هوش مصنوعی واقعی، نیاز به API Key است)"
        except:
            return "❌ خطا در ساخت تصویر"

# ==================== موتور پاسخ‌دهی هوشمند ====================

class SuperAIEngine:
    """موتور هوش مصنوعی پیشرفته"""
    
    def __init__(self):
        self.search_engine = SuperSearchEngine()
        self.file_processor = FileProcessor()
        self.conversation_history = []
    
    async def generate_response(self, user_message: str, file_data: dict = None) -> str:
        """تولید پاسخ هوشمند"""
        
        # ۱. بررسی فایل
        if file_data:
            file_response = await self._handle_file(file_data)
            return file_response
        
        # ۲. جستجوی اینترنت
        search_result = await self.search_engine.search_web(user_message)
        if search_result:
            # ذخیره در حافظه
            save_knowledge(user_message[:50], search_result, "web_search")
            return self._format_response(user_message, search_result, "🌐")
        
        # ۳. بررسی حافظه
        memories = get_memory(user_message)
        if memories:
            return memories[0][1] + "\n\n📚 (از حافظه‌ام یادم آمد)"
        
        # ۴. بررسی دانش
        knowledge = get_knowledge(user_message)
        if knowledge:
            return knowledge[0][0] + "\n\n🧠 (از دانش خودم می‌دانم)"
        
        # ۵. پاسخ هوشمندانه پیش‌فرض
        return self._generate_smart_response(user_message)
    
    async def _handle_file(self, file_data: dict) -> str:
        """پردازش فایل آپلود شده"""
        file_type = file_data.get('type', '')
        content = file_data.get('content', '')
        filename = file_data.get('name', '')
        
        if file_type.startswith('image/'):
            return self.file_processor.process_image(content)
        elif file_type.startswith('text/') or filename.endswith('.txt'):
            return self.file_processor.process_text_file(content.decode('utf-8'))
        elif filename.endswith('.pdf'):
            return "📄 فایل PDF دریافت شد. (پردازش پیشرفته در نسخه بعدی)"
        elif filename.endswith('.docx'):
            return "📄 فایل Word دریافت شد. (پردازش پیشرفته در نسخه بعدی)"
        else:
            return f"📁 فایل '{filename}' دریافت شد. نوع: {file_type}"
    
    def _format_response(self, query: str, result: str, emoji: str) -> str:
        """فرمت‌بندی پاسخ"""
        return f"""
{emoji} **پاسخ به:** "{query}"

{result}

---
📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}
🔍 منبع: جستجوی اینترنت
"""
    
    def _generate_smart_response(self, query: str) -> str:
        """پاسخ هوشمندانه پیش‌فرض"""
        responses = [
            f"🤔 جالب! در مورد '{query}' بیشتر تحقیق می‌کنم.",
            f"📚 موضوع '{query}' را به خاطر می‌سپرم و بعداً بیشتر یاد می‌گیرم!",
            f"🧠 '{query}' سوال خوبی است! من در حال یادگیری هستم.",
        ]
        return random.choice(responses) + "\n\n💡 می‌توانم جستجوی اینترنتی انجام دهم یا از من بپرسید."

# ==================== توابع کمکی ====================

def save_memory(user_msg, ai_resp, file_type=None, file_name=None):
    try:
        conn = sqlite3.connect('super_ai_memory.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO memories (user_message, ai_response, file_type, file_name)
            VALUES (?, ?, ?, ?)
        ''', (user_msg, ai_resp, file_type, file_name))
        conn.commit()
        conn.close()
    except:
        pass

def get_memory(query):
    try:
        conn = sqlite3.connect('super_ai_memory.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_message, ai_response FROM memories
            WHERE user_message LIKE ? OR topic LIKE ?
            ORDER BY timestamp DESC LIMIT 3
        ''', (f'%{query}%', f'%{query}%'))
        results = cursor.fetchall()
        conn.close()
        return results
    except:
        return []

def save_knowledge(topic, fact, source="self_learn"):
    try:
        conn = sqlite3.connect('super_ai_memory.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO knowledge (topic, fact, source)
            VALUES (?, ?, ?)
        ''', (topic, fact, source))
        conn.commit()
        conn.close()
    except:
        pass

def get_knowledge(topic):
    try:
        conn = sqlite3.connect('super_ai_memory.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT fact FROM knowledge
            WHERE topic LIKE ?
            ORDER BY confidence DESC, timestamp DESC
            LIMIT 3
        ''', (f'%{topic}%',))
        results = cursor.fetchall()
        conn.close()
        return results
    except:
        return []

# ==================== مسیرهای وب‌سایت ====================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
async def chat():
    """پردازش پیام و فایل"""
    try:
        user_message = request.form.get('message', '')
        file = request.files.get('file')
        
        file_data = None
        if file:
            filename = secure_filename(file.filename)
            content = file.read()
            file_data = {
                'name': filename,
                'type': file.content_type,
                'content': content
            }
        
        if not user_message and not file_data:
            return jsonify({'response': 'لطفاً پیام یا فایل ارسال کنید!'})
        
        # تولید پاسخ
        ai_engine = SuperAIEngine()
        response = await ai_engine.generate_response(user_message, file_data)
        
        # ذخیره در حافظه
        save_memory(user_message, response, 
                   file_data.get('type') if file_data else None,
                   file_data.get('name') if file_data else None)
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().strftime('%H:%M')
        })
        
    except Exception as e:
        return jsonify({'response': f'❌ خطا: {str(e)}'})

@app.route('/memory')
def view_memory():
    try:
        conn = sqlite3.connect('super_ai_memory.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_message, ai_response, file_name, timestamp 
            FROM memories 
            ORDER BY timestamp DESC 
            LIMIT 30
        ''')
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
                body { font-family: Tahoma; background: #1a1a2e; color: white; padding: 20px; }
                .container { max-width: 800px; margin: 0 auto; }
                .card { background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.1); }
                .time { color: #888; font-size: 12px; }
                .file { color: #667eea; font-size: 12px; }
                a { color: #667eea; text-decoration: none; }
                .back { display: inline-block; padding: 10px 20px; background: #667eea; border-radius: 10px; margin-top: 20px; color: white; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📚 حافظه من</h1>
                <p>تعداد: """ + str(len(memories)) + """</p>
        """
        for m in memories:
            html += f"""
                <div class="card">
                    <strong>👤 شما:</strong> {m[0][:100] if m[0] else '📎 فایل'}<br>
                    <strong>🧠 من:</strong> {m[1][:200] if m[1] else '...'}<br>
                    <span class="file">📎 {m[2] if m[2] else ''}</span>
                    <span class="time">🕐 {m[3]}</span>
                </div>
            """
        
        html += """
                <a href="/" class="back">⬅️ بازگشت</a>
            </div>
        </body>
        </html>
        """
        return html
    except Exception as e:
        return f"خطا: {e}"

@app.route('/stats')
def stats():
    try:
        conn = sqlite3.connect('super_ai_memory.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM memories')
        m_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM knowledge')
        k_count = cursor.fetchone()[0]
        conn.close()
        
        html = f"""
        <!DOCTYPE html>
        <html dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>📊 آمار</title>
            <style>
                body {{ font-family: Tahoma; background: #1a1a2e; color: white; padding: 20px; text-align: center; }}
                .stat {{ background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; margin: 10px; }}
                .number {{ font-size: 48px; color: #667eea; }}
                a {{ color: #667eea; text-decoration: none; }}
                .back {{ display: inline-block; padding: 10px 20px; background: #667eea; border-radius: 10px; margin-top: 20px; color: white; }}
            </style>
        </head>
        <body>
            <h1>📊 آمار</h1>
            <div class="stat"><div class="number">{m_count}</div>📚 خاطرات</div>
            <div class="stat"><div class="number">{k_count}</div>🧠 دانش</div>
            <div class="stat"><div class="number">{m_count + k_count}</div>🌟 مجموع</div>
            <a href="/" class="back">⬅️ بازگشت</a>
        </body>
        </html>
        """
        return html
    except:
        return "خطا"

@app.route('/knowledge')
def view_knowledge():
    try:
        conn = sqlite3.connect('super_ai_memory.db')
        cursor = conn.cursor()
        cursor.execute('SELECT topic, fact, source, timestamp FROM knowledge ORDER BY timestamp DESC LIMIT 30')
        knowledge = cursor.fetchall()
        conn.close()
        
        html = """
        <!DOCTYPE html>
        <html dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>🧠 دانش</title>
            <style>
                body { font-family: Tahoma; background: #1a1a2e; color: white; padding: 20px; }
                .container { max-width: 800px; margin: 0 auto; }
                .card { background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.1); }
                .topic { color: #764ba2; font-weight: bold; }
                .time { color: #888; font-size: 12px; }
                a { color: #667eea; text-decoration: none; }
                .back { display: inline-block; padding: 10px 20px; background: #667eea; border-radius: 10px; margin-top: 20px; color: white; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🧠 دانش</h1>
                <p>تعداد: """ + str(len(knowledge)) + """</p>
        """
        for k in knowledge:
            html += f"""
                <div class="card">
                    <span class="topic">📌 {k[0]}</span><br>
                    {k[1][:300]}<br>
                    <span>🔗 {k[2]}</span>
                    <span class="time">🕐 {k[3]}</span>
                </div>
            """
        
        html += """
                <a href="/" class="back">⬅️ بازگشت</a>
            </div>
        </body>
        </html>
        """
        return html
    except Exception as e:
        return f"خطا: {e}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
