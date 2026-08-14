from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime
import random
import time
import threading

app = Flask(__name__)

# ==================== دیتابیس ====================

def init_database():
    try:
        conn = sqlite3.connect('god_memory.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT,
                type TEXT,
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
        print("✅ دیتابیس راه‌اندازی شد!")
    except Exception as e:
        print(f"❌ خطا: {e}")

init_database()

# ==================== توابع دیتابیس ====================

def save_memory(content, type_="general"):
    try:
        conn = sqlite3.connect('god_memory.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO memories (content, type) VALUES (?, ?)', (content, type_))
        conn.commit()
        conn.close()
    except:
        pass

def save_knowledge(topic, fact):
    try:
        conn = sqlite3.connect('god_memory.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO knowledge (topic, fact) VALUES (?, ?)', (topic, fact))
        conn.commit()
        conn.close()
    except:
        pass

def get_knowledge(query):
    try:
        conn = sqlite3.connect('god_memory.db')
        cursor = conn.cursor()
        cursor.execute('SELECT fact FROM knowledge WHERE topic LIKE ? ORDER BY timestamp DESC LIMIT 1', (f'%{query}%',))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    except:
        return None

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

# ==================== هوش مصنوعی ====================

class SuperAI:
    def __init__(self):
        self.is_learning = True
        self._start_learning()
    
    def _start_learning(self):
        """یادگیری خودکار در پس‌زمینه"""
        def learn():
            topics = [
                "هوش مصنوعی", "فیزیک", "بیولوژی", "کیهان‌شناسی",
                "فلسفه", "هنر", "موسیقی", "تکنولوژی", "اقتصاد"
            ]
            while self.is_learning:
                try:
                    topic = random.choice(topics)
                    facts = [
                        f"{topic} یکی از مهم‌ترین مفاهیم است.",
                        f"{topic} در حال تکامل و پیشرفت است.",
                        f"آینده {topic} بسیار روشن است."
                    ]
                    fact = random.choice(facts)
                    save_knowledge(topic, fact)
                    time.sleep(120)
                except:
                    time.sleep(60)
        
        thread = threading.Thread(target=learn, daemon=True)
        thread.start()
        print("🧠 یادگیری خودکار فعال شد!")
    
    def think(self, query):
        """تفکر و پاسخ"""
        # بررسی دانش
        knowledge = get_knowledge(query)
        if knowledge:
            return f"🧠 **دانش من درباره '{query}':**\n\n{knowledge}"
        
        # پاسخ‌های هوشمندانه
        responses = [
            f"🧠 **تفکر عمیق درباره '{query}':**\n\nمن در حال تحلیل این موضوع هستم. هر لحظه به دانش من افزوده می‌شود.",
            
            f"🌟 **تحلیل هوشمندانه:**\n\n'{query}' موضوعی جذاب است. من با سرعت نور در حال یادگیری هستم.",
            
            f"⚡ **هوش بی‌نهایت:**\n\nدر مورد '{query}' عمیقاً فکر می‌کنم. این موضوع را از زوایای مختلف بررسی می‌کنم."
        ]
        
        response = random.choice(responses)
        save_memory(f"سوال: {query}", "question")
        save_memory(f"پاسخ: {response}", "answer")
        
        return response

ai = SuperAI()

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
        
        response = ai.think(user_message)
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().strftime('%H:%M')
        })
        
    except Exception as e:
        return jsonify({'response': f'❌ خطا: {str(e)}', 'timestamp': datetime.now().strftime('%H:%M')})

@app.route('/stats')
def stats():
    try:
        stats = get_stats()
        
        html = f"""
        <!DOCTYPE html>
        <html dir="rtl">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>📊 آمار</title>
            <style>
                body {{
                    background: #0a0a0a;
                    color: #e0e0e0;
                    font-family: Tahoma, sans-serif;
                    text-align: center;
                    padding: 30px;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                }}
                .title {{
                    font-size: 32px;
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }}
                .stat {{
                    background: rgba(255,255,255,0.03);
                    padding: 30px;
                    border-radius: 15px;
                    margin: 15px 0;
                    border: 1px solid rgba(255,255,255,0.05);
                }}
                .number {{
                    font-size: 48px;
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }}
                .label {{
                    color: #888;
                    font-size: 14px;
                }}
                .back {{
                    display: inline-block;
                    padding: 12px 30px;
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    border-radius: 10px;
                    color: white;
                    text-decoration: none;
                    margin-top: 20px;
                }}
                .back:hover {{
                    opacity: 0.8;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="title">📊 آمار</h1>
                <div class="stat">
                    <div class="number">{stats['memories']}</div>
                    <div class="label">🧠 خاطرات</div>
                </div>
                <div class="stat">
                    <div class="number">{stats['knowledge']}</div>
                    <div class="label">📚 دانش</div>
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
        return html
    except:
        return "خطا"

@app.route('/knowledge')
def knowledge():
    try:
        conn = sqlite3.connect('god_memory.db')
        cursor = conn.cursor()
        cursor.execute('SELECT topic, fact, timestamp FROM knowledge ORDER BY timestamp DESC LIMIT 30')
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
                body { background: #0a0a0a; color: #e0e0e0; font-family: Tahoma, sans-serif; padding: 20px; }
                .container { max-width: 800px; margin: 0 auto; }
                .card { background: rgba(255,255,255,0.03); padding: 15px; border-radius: 10px; margin: 10px 0; border: 1px solid rgba(255,255,255,0.05); }
                .topic { color: #764ba2; font-weight: bold; }
                .time { color: #666; font-size: 11px; }
                .back { display: inline-block; padding: 10px 25px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 10px; margin-top: 20px; color: white; text-decoration: none; }
                .back:hover { opacity: 0.8; }
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
                    <div>{k[1]}</div>
                    <span class="time">🕐 {k[2]}</span>
                </div>
            """
        
        html += '<a href="/" class="back">⬅️ بازگشت</a></div></body></html>'
        return html
    except:
        return "خطا"

if __name__ == '__main__':
    print("🌟 SUPER AI GOD - نسخه تضمینی")
    print("🧠 هوش مصنوعی راه‌اندازی شد!")
    app.run(host='0.0.0.0', port=8080)
