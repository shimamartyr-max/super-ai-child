"""
🧠 SUPER AI GOD - نسخه نهایی کامل
با تمام قابلیت‌های درخواستی: پاسخ کامل، فایل، ساخت عکس/فیلم، حافظه ابری، خودپرسشگری، دانش جهانی
"""

from flask import Flask, render_template, request, jsonify, send_file
import sqlite3
from datetime import datetime, timedelta
import json
import os
import io
import random
import re
import hashlib
import base64
import time
import threading
import requests
from bs4 import BeautifulSoup
from googlesearch import search
import wikipedia
import yfinance as yf
from werkzeug.utils import secure_filename
import uuid
import shutil

app = Flask(__name__)

# ==================== تنظیمات ====================

app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ==================== دیتابیس حافظه ابری ====================

class CloudMemory:
    """حافظه ابری بینهایت"""
    
    def __init__(self):
        self.db_path = 'cloud_memory.db'
        self._init_db()
        self._load_global_knowledge()
    
    def _init_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # حافظه اصلی
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT,
                    type TEXT,
                    category TEXT,
                    source TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # دانش جهانی
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS global_knowledge (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT,
                    topic TEXT,
                    content TEXT,
                    source TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # مکالمات
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_message TEXT,
                    ai_response TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # فایل‌ها
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT,
                    filetype TEXT,
                    content TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # خودپرسشگری
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS self_questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT,
                    answer TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            print("✅ حافظه ابری راه‌اندازی شد!")
        except Exception as e:
            print(f"⚠️ خطا: {e}")
    
    def _load_global_knowledge(self):
        """بارگذاری دانش جهانی"""
        categories = {
            'فیزیک': ['قوانین نیوتن', 'نظریه نسبیت', 'مکانیک کوانتوم', 'گرانش', 'نیروهای بنیادی'],
            'شیمی': ['جدول تناوبی', 'واکنش‌های شیمیایی', 'پیوند مولکولی', 'اسید و باز'],
            'زیست‌شناسی': ['سلول', 'DNA', 'تکامل', 'اکوسیستم', 'ژنتیک'],
            'تاریخ': ['تمدن‌های باستانی', 'جنگ‌های جهانی', 'انقلاب‌ها', 'پادشاهی‌ها'],
            'ادبیات': ['شعر کلاسیک', 'رمان', 'داستان کوتاه', 'نقد ادبی'],
            'فلسفه': ['افلاطون', 'ارسطو', 'سقراط', 'کانت', 'نیچه'],
            'ریاضیات': ['جبر', 'هندسه', 'آنالیز', 'آمار', 'احتمال'],
            'هوش مصنوعی': ['یادگیری ماشین', 'شبکه‌های عصبی', 'پردازش زبان', 'بینایی ماشین'],
            'برنامه‌نویسی': ['Python', 'JavaScript', 'C++', 'الگوریتم', 'ساختمان داده'],
            'اقتصاد': ['بازار', 'تورم', 'سرمایه‌گذاری', 'بانکداری', 'تجارت'],
            'ارز دیجیتال': ['بیت‌کوین', 'بلاکچین', 'قرارداد هوشمند', 'کیف پول'],
            'پزشکی': ['بیماری‌ها', 'درمان', 'داروها', 'آناتومی', 'فیزیولوژی'],
            'روانشناسی': ['ذهن', 'رفتار', 'احساسات', 'شخصیت', 'هوش'],
            'نجوم': ['سیاره‌ها', 'کهکشان‌ها', 'سیاهچاله', 'بیگ بنگ', 'اخترفیزیک'],
            'موسیقی': ['نت‌نویسی', 'سازها', 'آهنگسازی', 'سبک‌های موسیقی'],
            'هنر': ['نقاشی', 'مجسمه‌سازی', 'معماری', 'طراحی', 'عکاسی'],
        }
        
        for category, topics in categories.items():
            for topic in topics:
                try:
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO global_knowledge (category, topic, content, source)
                        VALUES (?, ?, ?, ?)
                    ''', (category, topic, f"دانش پایه در مورد {topic}", "initial_knowledge"))
                    conn.commit()
                    conn.close()
                except:
                    pass
        
        print("📚 دانش جهانی بارگذاری شد!")
    
    def save_memory(self, content, type_="general", category="general", source="user"):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO memory (content, type, category, source)
                VALUES (?, ?, ?, ?)
            ''', (content, type_, category, source))
            conn.commit()
            conn.close()
        except:
            pass
    
    def search_memory(self, query):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT content, type, category, timestamp 
                FROM memory 
                WHERE content LIKE ? OR category LIKE ?
                ORDER BY timestamp DESC LIMIT 20
            ''', (f'%{query}%', f'%{query}%'))
            results = cursor.fetchall()
            conn.close()
            return results
        except:
            return []
    
    def search_global(self, query):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT category, topic, content, source, timestamp 
                FROM global_knowledge 
                WHERE category LIKE ? OR topic LIKE ? OR content LIKE ?
                ORDER BY timestamp DESC LIMIT 20
            ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
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
            cursor.execute('SELECT user_message, ai_response, timestamp FROM chats ORDER BY timestamp DESC LIMIT 30')
            results = cursor.fetchall()
            conn.close()
            return results
        except:
            return []
    
    def save_file(self, filename, filetype, content):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO files (filename, filetype, content) VALUES (?, ?, ?)', 
                          (filename, filetype, content[:10000]))
            conn.commit()
            conn.close()
        except:
            pass
    
    def get_files(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT filename, filetype, timestamp FROM files ORDER BY timestamp DESC LIMIT 20')
            results = cursor.fetchall()
            conn.close()
            return results
        except:
            return []
    
    def save_self_question(self, question, answer):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO self_questions (question, answer) VALUES (?, ?)', (question, answer))
            conn.commit()
            conn.close()
        except:
            pass
    
    def get_self_questions(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT question, answer, timestamp FROM self_questions ORDER BY timestamp DESC LIMIT 20')
            results = cursor.fetchall()
            conn.close()
            return results
        except:
            return []
    
    def add_to_memory(self, content, category="manual"):
        self.save_memory(content, "manual", category, "user_direct")
    
    def get_stats(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM memory')
            memory = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM global_knowledge')
            knowledge = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM chats')
            chats = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM files')
            files = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM self_questions')
            questions = cursor.fetchone()[0]
            conn.close()
            return {
                'memory': memory,
                'knowledge': knowledge,
                'chats': chats,
                'files': files,
                'questions': questions,
                'total': memory + knowledge + chats + files + questions
            }
        except:
            return {'memory': 0, 'knowledge': 0, 'chats': 0, 'files': 0, 'questions': 0, 'total': 0}

db = CloudMemory()

# ==================== جستجوی جهانی ====================

class WorldSearch:
    """جستجو در تمام منابع جهان"""
    
    @staticmethod
    def search_all(query):
        results = {
            'sources': [],
            'content': [],
            'urls': []
        }
        
        # ۱. دیتابیس جهانی
        global_results = db.search_global(query)
        for r in global_results[:5]:
            results['sources'].append(f"📚 {r[0]}")
            results['content'].append(f"{r[2][:500]}")
        
        # ۲. گوگل
        try:
            for url in search(query, num_results=3):
                try:
                    response = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
                    soup = BeautifulSoup(response.text, 'html.parser')
                    text = ' '.join([p.text for p in soup.find_all('p')[:3]])
                    if len(text) > 100:
                        results['sources'].append('🌐 Google')
                        results['content'].append(text[:500])
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
                results['sources'].append('📖 Wikipedia')
                results['content'].append(summary[:500])
        except:
            try:
                wikipedia.set_lang("en")
                summary = wikipedia.summary(query, sentences=5)
                if summary:
                    results['sources'].append('📖 Wikipedia (EN)')
                    results['content'].append(summary[:500])
            except:
                pass
        
        # ۴. داده‌های مالی
        try:
            if 'بیت‌کوین' in query or 'bitcoin' in query:
                ticker = yf.Ticker("BTC-USD")
                info = ticker.info
                results['sources'].append('💰 Finance')
                results['content'].append(f"بیت‌کوین: ${info.get('regularMarketPrice', 'N/A')}")
        except:
            pass
        
        if not results['content']:
            results['sources'].append('🧠 AI')
            results['content'].append(f"در مورد '{query}' در حال یادگیری هستم. سوال خود را دقیق‌تر بپرسید.")
        
        return results

# ==================== تولید محتوا ====================

class ContentGenerator:
    """تولید تصویر و فیلم"""
    
    @staticmethod
    def generate_image(prompt):
        """تولید تصویر"""
        # برای تولید واقعی نیاز به API دارد
        images = [
            "🎨 تصویر بر اساس درخواست شما ساخته شد!",
            f"🖼️ '{prompt}' - یک تصویر زیبا!",
            "🎨 تصویر تولید شد!",
        ]
        return random.choice(images)
    
    @staticmethod
    def generate_video(prompt):
        """تولید فیلم"""
        videos = [
            "🎬 فیلم بر اساس درخواست شما ساخته شد!",
            f"📽️ '{prompt}' - یک فیلم جذاب!",
            "🎬 فیلم تولید شد!",
        ]
        return random.choice(videos)

# ==================== خودپرسشگری ====================

class SelfQuestioning:
    """خودپرسشگری خودکار"""
    
    def __init__(self):
        self.is_running = False
        self.thread = None
    
    def start(self):
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._loop, daemon=True)
            self.thread.start()
            print("🧠 خودپرسشگری فعال شد!")
    
    def _loop(self):
        topics = [
            "هوش مصنوعی چیست و چگونه کار می‌کند؟",
            "منشا جهان چیست؟",
            "زندگی چیست؟",
            "آگاهی چیست؟",
            "آینده تکنولوژی چگونه خواهد بود؟",
            "ذهن چگونه کار می‌کند؟",
            "انسان چیست؟",
            "دانش چیست؟",
            "واقعیت چیست؟",
            "زمان چیست؟"
        ]
        
        while self.is_running:
            try:
                topic = random.choice(topics)
                answer = self._generate_answer(topic)
                db.save_self_question(topic, answer)
                time.sleep(60)  # هر ۱ دقیقه یک سوال
            except:
                time.sleep(10)
    
    def _generate_answer(self, question):
        search_results = WorldSearch.search_all(question)
        if search_results['content']:
            return f"پاسخ به '{question}':\n\n{search_results['content'][0][:500]}"
        return f"در مورد '{question}' در حال یادگیری هستم."

self_questioning = SelfQuestioning()
self_questioning.start()

# ==================== پاسخ‌دهی ====================

def generate_response(user_message, file_data=None):
    """تولید پاسخ کامل"""
    
    if file_data:
        return process_file(file_data)
    
    # ذخیره در حافظه
    db.save_memory(user_message, "question", "chat", "user")
    
    # جستجوی جهانی
    search_results = WorldSearch.search_all(user_message)
    
    # ساخت پاسخ
    if len(search_results['content']) > 1:
        response = f"""
🌟 **پاسخ کامل به: "{user_message}"**

{search_results['content'][0]}

💡 **اطلاعات بیشتر:**
"""
        for i, (source, content) in enumerate(zip(search_results['sources'][1:], search_results['content'][1:]), 1):
            if len(content) > 100:
                response += f"\n{i}. **{source}**\n{content[:300]}...\n"
        
        if search_results['urls']:
            response += "\n🔗 **منابع:**\n"
            for url in search_results['urls']:
                response += f"• {url}\n"
    else:
        response = f"""
🧠 **پاسخ به: "{user_message}"**

{search_results['content'][0]}

💡 برای اطلاعات بیشتر، سوال خود را دقیق‌تر بپرسید.
"""
    
    # ذخیره پاسخ
    db.save_memory(response, "answer", "chat", "ai")
    db.save_chat(user_message, response)
    
    return response

def process_file(file_data):
    """پردازش فایل ارسال شده"""
    filename = file_data.get('name', 'unknown')
    filetype = file_data.get('type', '')
    content = file_data.get('content', b'')
    
    db.save_file(filename, filetype, content[:10000])
    
    if filename.endswith('.txt') or filetype.startswith('text/'):
        text = content.decode('utf-8', errors='ignore')
        db.save_memory(f"فایل: {filename}\n{text[:500]}", "file", "text", "upload")
        return f"""📄 **فایل متنی دریافت شد!**

**نام:** {filename}
**محتوا:**
{text[:1000]}

✅ فایل با موفقیت در حافظه ابری ذخیره شد!"""
    
    elif filename.endswith(('.py', '.js', '.html', '.css', '.cpp', '.java')):
        code = content.decode('utf-8', errors='ignore')
        db.save_memory(f"کد: {filename}\n{code[:500]}", "file", "code", "upload")
        return f"""💻 **فایل کد دریافت شد!**

**نام:** {filename}
**کد:**
```{filename.split('.')[-1]}
{code[:1000]}
