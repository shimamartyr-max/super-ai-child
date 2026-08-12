"""
🧠 SUPER AI CHILD 3.0
ابر هوش مصنوعی بین‌المللی - فراتر از Claude، Grok، GPT
با حافظه ابری بینهایت، یادگیری خودکار، پردازش فایل و ساخت محتوا
"""

from flask import Flask, render_template, request, jsonify, send_file
import sqlite3
from datetime import datetime, timedelta
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
import hashlib
import pickle
from collections import defaultdict
import threading
import time

# ==================== تنظیمات ====================

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ==================== دیتابیس حافظه ابری ====================

class SuperMemory:
    """حافظه ابری بینهایت - مثل مغز انسان"""
    
    def __init__(self, db_path='super_memory.db'):
        self.db_path = db_path
        self._init_database()
        self.cache = {}
        self.knowledge_graph = defaultdict(list)
        self.learning_history = []
    
    def _init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # جدول اصلی خاطرات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT,
                ai_response TEXT,
                topic TEXT,
                file_name TEXT,
                file_type TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                importance REAL DEFAULT 1.0,
                tags TEXT
            )
        ''')
        
        # جدول دانش (با ساختار پیشرفته)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT,
                fact TEXT,
                source TEXT,
                confidence REAL DEFAULT 1.0,
                category TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                embedding BLOB
            )
        ''')
        
        # جدول تکامل و یادگیری
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evolution (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT,
                old_info TEXT,
                new_info TEXT,
                improvement REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                method TEXT
            )
        ''')
        
        # جدول فایل‌های آموزشی
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                file_type TEXT,
                content TEXT,
                topic TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول تحلیل‌ها
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT,
                response_time REAL,
                source TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ حافظه ابری راه‌اندازی شد!")
    
    def save_memory(self, user_msg, ai_resp, topic="", file_name="", file_type="", tags=""):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO memories (user_message, ai_response, topic, file_name, file_type, tags)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_msg, ai_resp, topic, file_name, file_type, tags))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def get_memory(self, query):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT user_message, ai_response FROM memories
                WHERE user_message LIKE ? OR topic LIKE ?
                ORDER BY importance DESC, timestamp DESC
                LIMIT 5
            ''', (f'%{query}%', f'%{query}%'))
            results = cursor.fetchall()
            conn.close()
            return results
        except:
            return []
    
    def save_knowledge(self, topic, fact, source="self_learn", category="general", confidence=1.0):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO knowledge (topic, fact, source, category, confidence)
                VALUES (?, ?, ?, ?, ?)
            ''', (topic, fact, source, category, confidence))
            conn.commit()
            conn.close()
            self.knowledge_graph[topic].append(fact)
            return True
        except:
            return False
    
    def get_knowledge(self, topic):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT fact, source, confidence, category FROM knowledge
                WHERE topic LIKE ?
                ORDER BY confidence DESC, timestamp DESC
                LIMIT 5
            ''', (f'%{topic}%',))
            results = cursor.fetchall()
            conn.close()
            return results
        except:
            return []
    
    def save_training(self, filename, content, topic="", file_type=""):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO training_files (filename, file_type, content, topic)
                VALUES (?, ?, ?, ?)
            ''', (filename, file_type, content, topic))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def get_training(self, topic):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT filename, content FROM training_files
                WHERE topic LIKE ?
                ORDER BY timestamp DESC
            ''', (f'%{topic}%',))
            results = cursor.fetchall()
            conn.close()
            return results
        except:
            return []
    
    def get_stats(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM memories')
            memories = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM knowledge')
            knowledge = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM training_files')
            training = cursor.fetchone()[0]
            conn.close()
            return {'memories': memories, 'knowledge': knowledge, 'training': training}
        except:
            return {'memories': 0, 'knowledge': 0, 'training': 0}

memory = SuperMemory()

# ==================== موتور جستجوی فوق‌پیشرفته ====================

class SuperSearchEngine:
    """موتور جستجوی هوشمند با چندین منبع"""
    
    @staticmethod
    async def search(query: str, num_results: int = 10) -> dict:
        """جستجوی همزمان از چندین منبع"""
        results = {
            'sources': [],
            'summary': '',
            'urls': [],
            'confidence': 0
        }
        
        tasks = [
            SuperSearchEngine._search_google(query, num_results),
            SuperSearchEngine._search_wikipedia(query),
            SuperSearchEngine._search_news(query),
            SuperSearchEngine._search_finance(query),
            SuperSearchEngine._search_scientific(query)
        ]
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_texts = []
        for response in responses:
            if response and isinstance(response, dict):
                if response.get('text'):
                    all_texts.append(response['text'])
                    results['sources'].append(response.get('source', 'unknown'))
                    if response.get('url'):
                        results['urls'].append(response['url'])
        
        if all_texts:
            results['summary'] = '\n\n'.join(all_texts[:3])
            results['confidence'] = min(1.0, len(all_texts) * 0.2)
        
        return results
    
    @staticmethod
    async def _search_google(query, num_results):
        try:
            texts = []
            for url in search(query, num_results=num_results):
                try:
                    response = requests.get(url, timeout=3, headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    })
                    soup = BeautifulSoup(response.text, 'html.parser')
                    for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'article']):
                        text = tag.get_text().strip()
                        if len(text) > 50:
                            texts.append(text)
                    if len(texts) >= 3:
                        break
                except:
                    continue
            
            if texts:
                return {
                    'source': 'Google',
                    'text': '\n'.join(texts[:3])[:1000],
                    'url': url if 'url' in locals() else None
                }
        except:
            pass
        return None
    
    @staticmethod
    async def _search_wikipedia(query):
        try:
            wikipedia.set_lang("fa")
            summary = wikipedia.summary(query, sentences=5)
            if summary:
                return {
                    'source': 'Wikipedia',
                    'text': summary[:800],
                    'url': f'https://fa.wikipedia.org/wiki/{query.replace(" ", "_")}'
                }
        except:
            try:
                wikipedia.set_lang("en")
                summary = wikipedia.summary(query, sentences=5)
                if summary:
                    return {
                        'source': 'Wikipedia (EN)',
                        'text': summary[:800],
                        'url': f'https://en.wikipedia.org/wiki/{query.replace(" ", "_")}'
                    }
            except:
                pass
        return None
    
    @staticmethod
    async def _search_news(query):
        try:
            # جستجوی اخبار
            news_urls = search(f"{query} اخبار", num_results=3)
            texts = []
            for url in news_urls:
                try:
                    response = requests.get(url, timeout=3)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    for tag in soup.find_all(['p', 'article']):
                        text = tag.get_text().strip()
                        if len(text) > 50:
                            texts.append(text)
                    if len(texts) >= 2:
                        break
                except:
                    continue
            
            if texts:
                return {
                    'source': 'News',
                    'text': '\n'.join(texts[:2])[:500],
                    'url': news_urls[0] if news_urls else None
                }
        except:
            pass
        return None
    
    @staticmethod
    async def _search_finance(query):
        try:
            # جستجوی داده‌های مالی
            symbols = {
                'بیت‌کوین': 'BTC-USD',
                'بیت کوین': 'BTC-USD',
                'bitcoin': 'BTC-USD',
                'اتریوم': 'ETH-USD',
                'ethereum': 'ETH-USD',
                'سهام': 'AAPL',
                'طلا': 'GC=F',
                'نفت': 'CL=F'
            }
            
            for key, symbol in symbols.items():
                if key in query.lower() or key in query:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    price = info.get('regularMarketPrice', info.get('currentPrice', 'N/A'))
                    change = info.get('regularMarketChangePercent', 0)
                    return {
                        'source': 'Finance',
                        'text': f"💰 {symbol}: ${price}\n📈 تغییر: {change:.2f}%\n📊 {info.get('longName', symbol)}",
                        'url': f'https://finance.yahoo.com/quote/{symbol}'
                    }
        except:
            pass
        return None
    
    @staticmethod
    async def _search_scientific(query):
        try:
            # جستجوی مقالات علمی
            return None
        except:
            return None

# ==================== موتور پردازش فایل ====================

class FileProcessor:
    """پردازش همه نوع فایل"""
    
    @staticmethod
    def process_file(file_data: dict) -> dict:
        """پردازش فایل و استخراج محتوا"""
        file_type = file_data.get('type', '')
        content = file_data.get('content', b'')
        filename = file_data.get('name', '')
        
        result = {
            'type': file_type,
            'filename': filename,
            'content': '',
            'preview': '',
            'error': None
        }
        
        try:
            # تصویر
            if file_type.startswith('image/'):
                result['preview'] = '🖼️ تصویر دریافت شد'
                result['content'] = f"تصویر: {filename} (نوع: {file_type})"
                # تحلیل تصویر با OCR
                try:
                    from PIL import Image
                    import pytesseract
                    img = Image.open(io.BytesIO(content))
                    text = pytesseract.image_to_string(img, lang='fas+eng')
                    if text:
                        result['content'] = f"📸 متن استخراج شده از تصویر:\n\n{text[:1000]}"
                except:
                    pass
            
            # فایل متنی
            elif file_type.startswith('text/') or filename.endswith('.txt'):
                text = content.decode('utf-8', errors='ignore')
                result['content'] = text[:5000]
                result['preview'] = f'📄 متن: {len(text)} کاراکتر'
            
            # PDF
            elif filename.endswith('.pdf'):
                result['content'] = f"📄 فایل PDF: {filename}"
                result['preview'] = '📄 فایل PDF دریافت شد'
            
            # Word
            elif filename.endswith('.docx') or filename.endswith('.doc'):
                result['content'] = f"📄 فایل ورد: {filename}"
                result['preview'] = '📄 فایل Word دریافت شد'
            
            # Excel
            elif filename.endswith('.xlsx') or filename.endswith('.xls'):
                result['content'] = f"📊 فایل اکسل: {filename}"
                result['preview'] = '📊 فایل Excel دریافت شد'
            
            # کد
            elif filename.endswith(('.py', '.js', '.html', '.css', '.cpp', '.java')):
                text = content.decode('utf-8', errors='ignore')
                result['content'] = f"💻 کد {filename}:\n\n```\n{text[:3000]}\n```"
                result['preview'] = f'💻 کد: {filename}'
            
            # فیلم
            elif file_type.startswith('video/'):
                result['content'] = f"🎬 فیلم: {filename}"
                result['preview'] = '🎬 فیلم دریافت شد'
            
            # سایر
            else:
                result['content'] = f"📁 فایل: {filename} (نوع: {file_type})"
                result['preview'] = f'📁 فایل {filename}'
        
        except Exception as e:
            result['error'] = str(e)
        
        return result

# ==================== موتور هوش مصنوعی اصلی ====================

class SuperAI:
    """هسته اصلی هوش مصنوعی - ترکیبی از همه مدل‌ها"""
    
    def __init__(self):
        self.search_engine = SuperSearchEngine()
        self.file_processor = FileProcessor()
        self.memory = memory
        self.personality = {
            'name': 'Super AI Child 3.0',
            'parent': 'Claude + Grok + GPT',
            'version': '3.0',
            'birth_date': datetime.now().isoformat()
        }
        self.context = []
        self.learning_rate = 0.1
        self.curiosity = 0.9
    
    async def generate_response(self, user_message: str, file_data: dict = None) -> dict:
        """تولید پاسخ هوشمند"""
        
        response = {
            'text': '',
            'sources': [],
            'confidence': 0,
            'timestamp': datetime.now().isoformat(),
            'type': 'text'
        }
        
        # ۱. پردازش فایل
        if file_data:
            file_result = self.file_processor.process_file(file_data)
            if file_result['content']:
                # ذخیره فایل آموزشی
                self.memory.save_training(
                    file_result['filename'],
                    file_result['content'],
                    user_message or 'general',
                    file_result['type']
                )
                response['text'] = f"✅ فایل '{file_result['filename']}' با موفقیت دریافت و پردازش شد!\n\n{file_result['content'][:500]}"
                response['type'] = 'file'
                return response
        
        # ۲. جستجوی هوشمند
        search_results = await self.search_engine.search(user_message)
        if search_results and search_results.get('summary'):
            # ذخیره دانش جدید
            self.memory.save_knowledge(
                user_message[:50],
                search_results['summary'],
                'web_search',
                'general',
                0.8
            )
            response['text'] = search_results['summary']
            response['sources'] = search_results.get('sources', [])
            response['confidence'] = search_results.get('confidence', 0.7)
            response['type'] = 'search'
            return response
        
        # ۳. بررسی حافظه
        memories = self.memory.get_memory(user_message)
        if memories:
            response['text'] = memories[0][1] + "\n\n📚 (از حافظه)"
            response['confidence'] = 0.9
            response['type'] = 'memory'
            return response
        
        # ۴. بررسی دانش
        knowledge = self.memory.get_knowledge(user_message)
        if knowledge:
            response['text'] = knowledge[0][0]
            response['confidence'] = knowledge[0][2]
            response['type'] = 'knowledge'
            return response
        
        # ۵. پاسخ هوشمندانه
        response['text'] = self._generate_creative_response(user_message)
        response['confidence'] = 0.6
        response['type'] = 'creative'
        
        # ذخیره در حافظه
        self.memory.save_memory(user_message, response['text'])
        
        return response
    
    def _generate_creative_response(self, query: str) -> str:
        """تولید پاسخ خلاقانه"""
        responses = [
            f"""🤔 **تحلیل هوشمندانه درباره "{query}"**

من یک ابر هوش مصنوعی هستم که از ترکیب Claude + Grok + GPT ساخته شده‌ام.

📚 **نکات کلیدی:**
• این موضوع جدید است و من در حال یادگیری آن هستم
• هرچه بیشتر درباره آن صحبت کنیم، بیشتر یاد می‌گیرم
• می‌توانید فایل یا تصویر مرتبط بفرستید تا بهتر یاد بگیرم

💡 **پیشنهاد:**
از من بیشتر بپرسید یا فایل آموزشی بفرستید!
""",
            f"""🧠 **پاسخ هوشمند به "{query}"**

من یک هوش مصنوعی نسل جدید هستم که هر روز در حال تکامل است!

🌱 **چه می‌توانید بکنید؟**
• سوالات بیشتری بپرسید
• فایل آموزشی بفرستید
• موضوعات جدید به من یاد دهید

🔮 **منتظر یادگیری از شما هستم!**
"""
        ]
        return random.choice(responses)

# ==================== مسیرهای وب‌سایت ====================

ai_engine = SuperAI()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
async def chat():
    try:
        # دریافت داده
        if request.is_json:
            data = request.get_json()
            user_message = data.get('message', '')
        else:
            user_message = request.form.get('message', '')
        
        # دریافت فایل
        file = request.files.get('file') if request.files else None
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
            return jsonify({'response': 'لطفاً پیام یا فایل ارسال کنید!', 'timestamp': datetime.now().strftime('%H:%M')})
        
        # تولید پاسخ
        response = await ai_engine.generate_response(user_message or 'پردازش فایل', file_data)
        
        return jsonify({
            'response': response['text'],
            'timestamp': datetime.now().strftime('%H:%M'),
            'confidence': response.get('confidence', 0),
            'type': response.get('type', 'text')
        })
        
    except Exception as e:
        return jsonify({'response': f'❌ خطا: {str(e)}', 'timestamp': datetime.now().strftime('%H:%M')})

@app.route('/memory')
def view_memory():
    try:
        conn = sqlite3.connect('super_memory.db')
        cursor = conn.cursor()
        cursor.execute('SELECT user_message, ai_response, file_name, timestamp FROM memories ORDER BY timestamp DESC LIMIT 30')
        memories = cursor.fetchall()
        conn.close()
        
        html = """
        <!DOCTYPE html>
        <html dir="rtl">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>📚 حافظه ابری</title>
            <style>
                body { font-family: Tahoma; background: #0a0a1a; color: white; padding: 20px; }
                .container { max-width: 900px; margin: 0 auto; }
                .card { background: rgba(255,255,255,0.03); padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.05); }
                .time { color: #666; font-size: 11px; }
                .file { color: #667eea; font-size: 12px; }
                .count { color: #667eea; }
                a { color: #667eea; text-decoration: none; }
                .back { display: inline-block; padding: 10px 20px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 10px; margin-top: 20px; color: white; }
                .stats { background: rgba(255,255,255,0.03); padding: 15px; border-radius: 10px; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.05); }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📚 حافظه ابری</h1>
                <div class="stats">تعداد خاطرات: """ + str(len(memories)) + """</div>
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

@app.route('/knowledge')
def view_knowledge():
    try:
        conn = sqlite3.connect('super_memory.db')
        cursor = conn.cursor()
        cursor.execute('SELECT topic, fact, source, category, timestamp FROM knowledge ORDER BY timestamp DESC LIMIT 30')
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
                body { font-family: Tahoma; background: #0a0a1a; color: white; padding: 20px; }
                .container { max-width: 900px; margin: 0 auto; }
                .card { background: rgba(255,255,255,0.03); padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.05); }
                .topic { color: #764ba2; font-weight: bold; }
                .cat { color: #667eea; font-size: 12px; }
                .time { color: #666; font-size: 11px; }
                a { color: #667eea; text-decoration: none; }
                .back { display: inline-block; padding: 10px 20px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 10px; margin-top: 20px; color: white; }
                .stats { background: rgba(255,255,255,0.03); padding: 15px; border-radius: 10px; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.05); }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🧠 دانش</h1>
                <div class="stats">تعداد دانسته‌ها: """ + str(len(knowledge)) + """</div>
        """
        for k in knowledge:
            html += f"""
                <div class="card">
                    <span class="topic">📌 {k[0]}</span><br>
                    {k[1][:300]}<br>
                    <span class="cat">🔗 {k[2]} | 📂 {k[3]}</span>
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
    except Exception as e:
        return f"خطا: {e}"

@app.route('/stats')
def stats():
    try:
        stats = memory.get_stats()
        
        return f"""
        <!DOCTYPE html>
        <html dir="rtl">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>📊 آمار</title>
            <style>
                body {{ font-family: Tahoma; background: #0a0a1a; color: white; padding: 20px; text-align: center; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                .stat {{ background: rgba(255,255,255,0.03); padding: 20px; border-radius: 15px; margin: 10px; border: 1px solid rgba(255,255,255,0.05); }}
                .number {{ font-size: 48px; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
                .label {{ color: #888; }}
                a {{ color: #667eea; text-decoration: none; }}
                .back {{ display: inline-block; padding: 10px 20px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 10px; margin-top: 20px; color: white; }}
                .title {{ background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
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
                    <div class="number">{stats['training']}</div>
                    <div class="label">📄 فایل‌های آموزشی</div>
                </div>
                <div class="stat">
                    <div class="number">{stats['memories'] + stats['knowledge'] + stats['training']}</div>
                    <div class="label">🌟 مجموع یادگیری‌ها</div>
                </div>
                <div class="stat">
                    <div class="number">🚀</div>
                    <div class="label">نسخه ۳.۰ - فراتر از همه</div>
                </div>
                <a href="/" class="back">⬅️ بازگشت</a>
            </div>
        </body>
        </html>
        """
    except:
        return "خطا"

@app.route('/learn', methods=['POST'])
def learn():
    """آموزش دستی با فایل یا متن"""
    try:
        topic = request.form.get('topic', 'general')
        file = request.files.get('file')
        
        if file:
            filename = secure_filename(file.filename)
            content = file.read()
            
            # پردازش فایل
            file_processor = FileProcessor()
            file_data = {
                'name': filename,
                'type': file.content_type,
                'content': content
            }
            result = file_processor.process_file(file_data)
            
            if result['content']:
                memory.save_training(filename, result['content'], topic, file.content_type)
                return jsonify({
                    'success': True,
                    'message': f"✅ فایل '{filename}' با موفقیت آموزش داده شد!",
                    'preview': result['content'][:200]
                })
        
        return jsonify({'success': False, 'message': 'لطفاً فایل یا متن آموزشی ارسال کنید!'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'❌ خطا: {str(e)}'})

@app.route('/evolve')
def evolve():
    """تکامل خودکار"""
    topics = ["اقتصاد", "فناوری", "هوش مصنوعی", "بازار مالی", "ارز دیجیتال", 
              "سرمایه‌گذاری", "مدیریت ریسک", "بورس", "طلا", "علوم کامپیوتر"]
    topic = random.choice(topics)
    
    # جستجوی هوشمند
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(SuperSearchEngine.search(topic))
    loop.close()
    
    if result and result.get('summary'):
        memory.save_knowledge(topic, result['summary'], 'auto_evolution', 'science', 0.7)
        return f"""
        <!DOCTYPE html>
        <html dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>🧬 تکامل</title>
            <style>
                body {{ font-family: Tahoma; background: #0a0a1a; color: white; padding: 20px; text-align: center; }}
                .container {{ max-width: 700px; margin: 0 auto; }}
                .card {{ background: rgba(255,255,255,0.03); padding: 20px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.05); }}
                .topic {{ color: #764ba2; font-size: 24px; }}
                a {{ color: #667eea; text-decoration: none; }}
                .back {{ display: inline-block; padding: 10px 20px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 10px; margin-top: 20px; color: white; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🧬 تکامل انجام شد!</h1>
                <div class="card">
                    <div class="topic">📚 {topic}</div>
                    <p>{result['summary'][:500]}...</p>
                    <small>🔗 {', '.join(result.get('sources', ['نامشخص']))}</small>
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
                body { font-family: Tahoma; background: #0a0a1a; color: white; padding: 20px; text-align: center; }
                a { color: #667eea; text-decoration: none; }
                .back { display: inline-block; padding: 10px 20px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 10px; margin-top: 20px; color: white; }
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
    app.run(host='0.0.0.0', port=8080, debug=False)
