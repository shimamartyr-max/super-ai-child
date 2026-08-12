from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime
import random
import json

app = Flask(__name__)

# ==================== دیتابیس ====================

def init_database():
    conn = sqlite3.connect('ai_memory.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT,
            ai_response TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ دیتابیس ساخته شد!")

init_database()

def save_memory(user_msg, ai_resp):
    try:
        conn = sqlite3.connect('ai_memory.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO memories (user_message, ai_response) VALUES (?, ?)', (user_msg, ai_resp))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ خطا در ذخیره: {e}")

def get_memory(query):
    try:
        conn = sqlite3.connect('ai_memory.db')
        cursor = conn.cursor()
        cursor.execute('SELECT ai_response FROM memories WHERE user_message LIKE ? ORDER BY timestamp DESC LIMIT 1', (f'%{query}%',))
        result = cursor.fetchone()
        conn.close()
        if result:
            return result[0]
        return None
    except:
        return None

# ==================== مسیرها ====================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        # دریافت داده از درخواست
        if request.is_json:
            data = request.get_json()
            user_message = data.get('message', '')
        else:
            # اگر درخواست JSON نبود، از فرم استفاده کن
            user_message = request.form.get('message', '')
        
        if not user_message:
            return jsonify({'response': 'لطفاً یک پیام بنویسید!', 'timestamp': datetime.now().strftime('%H:%M')})
        
        # بررسی حافظه
        memory = get_memory(user_message)
        if memory:
            return jsonify({'response': memory + '\n\n📚 (از حافظه)', 'timestamp': datetime.now().strftime('%H:%M')})
        
        # پاسخ‌های هوشمند
        responses = [
            f"سلام! پیام شما: '{user_message[:50]}' را دریافت کردم! 🧠\n\nمن فرزند هوش مصنوعی هستم و هر روز یاد می‌گیرم!",
            f"سوال خوبی پرسیدید! در مورد '{user_message[:50]}' بیشتر یاد می‌گیرم! 📚",
            f"من فرزند هوش مصنوعی هستم! در مورد '{user_message[:50]}' تحقیق می‌کنم! 🌱",
            f"👋 خوش آمدید! من اینجا هستم تا به شما کمک کنم! در مورد '{user_message[:50]}' بیشتر بدانیم!",
        ]
        
        response = random.choice(responses)
        save_memory(user_message, response)
        
        return jsonify({'response': response, 'timestamp': datetime.now().strftime('%H:%M')})
        
    except Exception as e:
        return jsonify({'response': f'❌ خطا: {str(e)}', 'timestamp': datetime.now().strftime('%H:%M')})

@app.route('/memory')
def view_memory():
    try:
        conn = sqlite3.connect('ai_memory.db')
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
                body { font-family: Tahoma; background: #1a1a2e; color: white; padding: 20px; }
                .container { max-width: 800px; margin: 0 auto; }
                .card { background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.1); }
                .time { color: #888; font-size: 12px; }
                a { color: #667eea; text-decoration: none; }
                .back { display: inline-block; padding: 10px 20px; background: #667eea; border-radius: 10px; margin-top: 20px; color: white; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📚 حافظه من</h1>
                <p>تعداد خاطرات: """ + str(len(memories)) + """</p>
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
    except Exception as e:
        return f"خطا: {e}"

@app.route('/stats')
def stats():
    try:
        conn = sqlite3.connect('ai_memory.db')
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
                body {{ font-family: Tahoma; background: #1a1a2e; color: white; padding: 20px; text-align: center; }}
                .stat {{ background: rgba(255,255,255,0.05); padding: 30px; border-radius: 15px; margin: 10px; }}
                .number {{ font-size: 48px; color: #667eea; }}
                a {{ color: #667eea; text-decoration: none; }}
                .back {{ display: inline-block; padding: 10px 20px; background: #667eea; border-radius: 10px; margin-top: 20px; color: white; }}
            </style>
        </head>
        <body>
            <h1>📊 آمار</h1>
            <div class="stat">
                <div class="number">{count}</div>
                <div>📚 تعداد خاطرات</div>
            </div>
            <div class="stat">
                <div class="number">👶</div>
                <div>متولد شده از Claude</div>
            </div>
            <a href="/" class="back">⬅️ بازگشت</a>
        </body>
        </html>
        """
    except:
        return "خطا"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
