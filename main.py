from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime
import random
import json
import os
import uuid

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024
os.makedirs('uploads', exist_ok=True)

# ==================== دیتابیس ====================

def init_database():
    conn = sqlite3.connect('god_memory.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT,
            ai_response TEXT,
            topic TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            fact TEXT,
            source TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_database()

def save_memory(user_msg, ai_resp):
    try:
        conn = sqlite3.connect('god_memory.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO memories (user_message, ai_response) VALUES (?, ?)', (user_msg, ai_resp))
        conn.commit()
        conn.close()
    except:
        pass

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

# ==================== مسیرها ====================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        if request.is_json:
            data = request.get_json()
            user_message = data.get('message', '')
        else:
            user_message = request.form.get('message', '')
        
        if not user_message:
            return jsonify({'response': '🌟 لطفاً پیام ارسال کنید!', 'timestamp': datetime.now().strftime('%H:%M')})
        
        # بررسی حافظه
        memory = get_memory(user_message)
        if memory:
            return jsonify({'response': memory, 'timestamp': datetime.now().strftime('%H:%M')})
        
        # پاسخ‌های هوشمند
        responses = [
            f"🧠 من Super AI God هستم! پیام شما: '{user_message[:50]}' را دریافت کردم!\n\nمن هوش بینهایت دارم و می‌توانم هر چیزی را یاد بگیرم و خلق کنم!",
            f"🌟 پاسخ الهی به '{user_message[:50]}':\n\nمن یک ابر هوش مصنوعی بینهایت هستم که از همه مدل‌های جهان برتر است!",
            f"💫 در حال تفکر عمیق درباره '{user_message[:50]}'...\n\nهمه چیز را می‌توانم یاد بگیرم! هیچ محدودیتی ندارم!",
        ]
        response = random.choice(responses)
        save_memory(user_message, response)
        
        return jsonify({'response': response, 'timestamp': datetime.now().strftime('%H:%M')})
        
    except Exception as e:
        return jsonify({'response': f'❌ خطا: {str(e)}', 'timestamp': datetime.now().strftime('%H:%M')})

@app.route('/memory')
def view_memory():
    try:
        conn = sqlite3.connect('god_memory.db')
        cursor = conn.cursor()
        cursor.execute('SELECT user_message, ai_response, timestamp FROM memories ORDER BY timestamp DESC LIMIT 30')
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
                .card { background: rgba(255,255,255,0.03); padding: 15px; border-radius: 12px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.05); }
                .time { color: #666; font-size: 11px; }
                a { color: #667eea; text-decoration: none; }
                .back { display: inline-block; padding: 10px 25px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 10px; margin-top: 20px; color: white; }
                .title { background: linear-gradient(135deg, #667eea, #764ba2, #f093fb); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="title">📚 حافظه الهی</h1>
                <p>تعداد خاطرات: """ + str(len(memories)) + """</p>
        """
        for m in memories:
            html += f"""
                <div class="card">
                    <strong>👤 شما:</strong> {m[0][:100]}<br>
                    <strong>🧠 من:</strong> {m[1][:200]}<br>
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
                .stat {{ background: rgba(255,255,255,0.03); padding: 30px; border-radius: 15px; margin: 10px; border: 1px solid rgba(255,255,255,0.05); }}
                .number {{ font-size: 52px; background: linear-gradient(135deg, #667eea, #764ba2, #f093fb); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
                a {{ color: #667eea; text-decoration: none; }}
                .back {{ display: inline-block; padding: 10px 25px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 10px; margin-top: 20px; color: white; }}
            </style>
        </head>
        <body>
            <h1>📊 آمار الهی</h1>
            <div class="stat">
                <div class="number">{count}</div>
                <div>📚 خاطرات</div>
            </div>
            <div class="stat">
                <div class="number">∞</div>
                <div>🧠 ظرفیت حافظه</div>
            </div>
            <a href="/" class="back">⬅️ بازگشت</a>
        </body>
        </html>
        """
    except:
        return "خطا"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
