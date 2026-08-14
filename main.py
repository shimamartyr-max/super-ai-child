from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime
import random
import os

app = Flask(__name__)

# ==================== دیتابیس ====================

def init_database():
    try:
        conn = sqlite3.connect('memory.db')
        cursor = conn.cursor()
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
        print("✅ دیتابیس ساخته شد!")
    except Exception as e:
        print(f"⚠️ خطا: {e}")

init_database()

def save_chat(user_msg, ai_resp):
    try:
        conn = sqlite3.connect('memory.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO chats (user_message, ai_response) VALUES (?, ?)', (user_msg, ai_resp))
        conn.commit()
        conn.close()
    except:
        pass

def get_response(msg):
    responses = [
        f"سلام! پیام شما: '{msg[:50]}...' را دریافت کردم! 🧠",
        f"سوال خوبی پرسیدید! در مورد '{msg[:50]}...' بیشتر یاد می‌گیرم! 📚",
        f"👋 خوش آمدید! من اینجا هستم تا به شما کمک کنم!",
        f"💡 سوال جالبی! بگذارید درباره '{msg[:50]}...' فکر کنم!",
    ]
    response = random.choice(responses)
    save_chat(msg, response)
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
        
        response = get_response(user_message)
        return jsonify({
            'response': response,
            'timestamp': datetime.now().strftime('%H:%M')
        })
        
    except Exception as e:
        return jsonify({'response': f'❌ خطا: {str(e)}', 'timestamp': datetime.now().strftime('%H:%M')})

@app.route('/memory')
def memory():
    try:
        conn = sqlite3.connect('memory.db')
        cursor = conn.cursor()
        cursor.execute('SELECT user_message, ai_response, timestamp FROM chats ORDER BY timestamp DESC LIMIT 20')
        chats = cursor.fetchall()
        conn.close()
        
        html = """
        <!DOCTYPE html>
        <html dir="rtl">
        <head><meta charset="UTF-8"><title>📚 حافظه</title>
        <style>
            body{background:#0a0a0a;color:#e0e0e0;font-family:Tahoma;padding:20px;}
            .card{background:rgba(255,255,255,0.03);padding:15px;border-radius:10px;margin:10px 0;border:1px solid rgba(255,255,255,0.05);}
            .time{color:#666;font-size:11px;}
            a{color:#667eea;text-decoration:none;}
            .back{display:inline-block;padding:10px 20px;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:10px;margin-top:20px;color:white;}
        </style>
        </head>
        <body>
        <h1>📚 حافظه</h1>
        """
        for c in chats:
            html += f"""
            <div class="card">
                <strong>شما:</strong> {c[0][:100]}<br>
                <strong>من:</strong> {c[1][:150]}<br>
                <span class="time">🕐 {c[2]}</span>
            </div>
            """
        html += '<a href="/" class="back">⬅️ بازگشت</a></body></html>'
        return html
    except:
        return "خطا"

@app.route('/stats')
def stats():
    try:
        conn = sqlite3.connect('memory.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM chats')
        count = cursor.fetchone()[0]
        conn.close()
        
        return f"""
        <!DOCTYPE html>
        <html dir="rtl">
        <head><meta charset="UTF-8"><title>📊 آمار</title>
        <style>
            body{{background:#0a0a0a;color:#e0e0e0;font-family:Tahoma;text-align:center;padding:20px;}}
            .stat{{background:rgba(255,255,255,0.03);padding:30px;border-radius:15px;margin:10px;}}
            .number{{font-size:48px;color:#667eea;}}
            a{{color:#667eea;text-decoration:none;}}
            .back{{display:inline-block;padding:10px 20px;background:linear-gradient(135deg,#667eea,#764ba2);border-radius:10px;margin-top:20px;color:white;}}
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print("🚀 Super AI God راه‌اندازی شد!")
    app.run(host='0.0.0.0', port=port)
