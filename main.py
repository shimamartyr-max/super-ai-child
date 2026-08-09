from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime
import random
import requests
from bs4 import BeautifulSoup
from googlesearch import search
import wikipedia

app = Flask(__name__)

def init_database():
    conn = sqlite3.connect('ai_memory.db')
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

def search_online(query):
    try:
        try:
            wikipedia.set_lang("fa")
            summary = wikipedia.summary(query, sentences=2)
            return summary
        except:
            pass
        try:
            from googlesearch import search
            results = search(query, num_results=2)
            for url in results:
                try:
                    response = requests.get(url, timeout=5)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    text = ' '.join([p.text for p in soup.find_all('p')[:2]])
                    if len(text) > 100:
                        return text[:400]
                except:
                    continue
        except:
            pass
        return None
    except:
        return None

def get_knowledge(topic):
    try:
        conn = sqlite3.connect('ai_memory.db')
        cursor = conn.cursor()
        cursor.execute('SELECT fact FROM knowledge WHERE topic LIKE ? ORDER BY timestamp DESC LIMIT 3', (f'%{topic}%',))
        results = cursor.fetchall()
        conn.close()
        return results
    except:
        return []

def save_knowledge(topic, fact, source="self_learn"):
    try:
        conn = sqlite3.connect('ai_memory.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO knowledge (topic, fact, source) VALUES (?, ?, ?)', (topic, fact, source))
        conn.commit()
        conn.close()
    except:
        pass

def save_memory(user_msg, ai_resp):
    try:
        conn = sqlite3.connect('ai_memory.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO memories (user_message, ai_response) VALUES (?, ?)', (user_msg, ai_resp))
        conn.commit()
        conn.close()
    except:
        pass

def get_memory(query):
    try:
        conn = sqlite3.connect('ai_memory.db')
        cursor = conn.cursor()
        cursor.execute('SELECT user_message, ai_response FROM memories WHERE user_message LIKE ? ORDER BY timestamp DESC LIMIT 3', (f'%{query}%',))
        results = cursor.fetchall()
        conn.close()
        return results
    except:
        return []

def generate_response(user_message):
    memories = get_memory(user_message)
    if memories:
        return memories[0][1] + "\n\n📚 (از حافظه‌ام یادم آمد)"
    
    knowledge = get_knowledge(user_message)
    if knowledge:
        return knowledge[0][0] + "\n\n🧠 (از دانش خودم می‌دانم)"
    
    search_result = search_online(user_message)
    if search_result:
        save_knowledge(user_message[:50], search_result, "online_search")
        return search_result + "\n\n🌐 (تازه از اینترنت یاد گرفتم)"
    
    return f"""
🤔 هنوز در مورد "{user_message}" چیزی نمی‌دانم!
اما من یک فرزند هوش مصنوعی هستم که هر روز یاد می‌گیرم!
هرچه بیشتر با من حرف بزنی، باهوش‌تر می‌شوم! 🌱
💡 من فرزند Claude هستم!
"""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    if not user_message:
        return jsonify({'response': 'لطفاً یک پیام بنویسید!'})
    response = generate_response(user_message)
    save_memory(user_message, response)
    return jsonify({'response': response, 'timestamp': datetime.now().strftime('%H:%M')})

@app.route('/memory')
def view_memory():
    try:
        conn = sqlite3.connect('ai_memory.db')
        cursor = conn.cursor()
        cursor.execute('SELECT user_message, ai_response, timestamp FROM memories ORDER BY timestamp DESC LIMIT 20')
        memories = cursor.fetchall()
        conn.close()
        html = "<html dir='rtl' style='background:#1a1a2e;color:white;font-family:Tahoma;padding:20px;'><h1>📚 حافظه</h1>"
        for m in memories:
            html += f"<div style='background:rgba(255,255,255,0.05);padding:10px;margin:5px 0;border-radius:10px;'><b>شما:</b> {m[0][:100]}<br><b>من:</b> {m[1][:150]}<br><small>{m[2]}</small></div>"
        html += "<a href='/' style='color:#667eea;'>⬅️ بازگشت</a></html>"
        return html
    except:
        return "خطا"

@app.route('/knowledge')
def view_knowledge():
    try:
        conn = sqlite3.connect('ai_memory.db')
        cursor = conn.cursor()
        cursor.execute('SELECT topic, fact, timestamp FROM knowledge ORDER BY timestamp DESC LIMIT 20')
        knowledge = cursor.fetchall()
        conn.close()
        html = "<html dir='rtl' style='background:#1a1a2e;color:white;font-family:Tahoma;padding:20px;'><h1>🧠 دانش</h1>"
        for k in knowledge:
            html += f"<div style='background:rgba(255,255,255,0.05);padding:10px;margin:5px 0;border-radius:10px;'><b>{k[0]}:</b> {k[1][:200]}<br><small>{k[2]}</small></div>"
        html += "<a href='/' style='color:#667eea;'>⬅️ بازگشت</a></html>"
        return html
    except:
        return "خطا"

@app.route('/stats')
def stats():
    try:
        conn = sqlite3.connect('ai_memory.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM memories')
        m_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM knowledge')
        k_count = cursor.fetchone()[0]
        conn.close()
        return f"""
        <html dir='rtl' style='background:#1a1a2e;color:white;font-family:Tahoma;padding:20px;text-align:center;'>
        <h1>📊 آمار</h1>
        <div style='background:rgba(255,255,255,0.05);padding:30px;border-radius:15px;margin:10px;'>
        <h2>📚 خاطرات: {m_count}</h2>
        <h2>🧠 دانش: {k_count}</h2>
        <h2>🌟 مجموع: {m_count + k_count}</h2>
        <h2>👶 متولد شده از Claude</h2>
        <a href='/' style='color:#667eea;'>⬅️ بازگشت</a>
        </div>
        </html>
        """
    except:
        return "خطا"

@app.route('/evolve')
def evolve():
    topics = ["اقتصاد", "فناوری", "بازار مالی", "ارز دیجیتال", "سرمایه‌گذاری", "مدیریت ریسک", "بورس", "طلا"]
    topic = random.choice(topics)
    result = search_online(topic)
    if result:
        save_knowledge(topic, result, "auto_evolution")
        return f"<html dir='rtl' style='background:#1a1a2e;color:white;font-family:Tahoma;padding:20px;text-align:center;'><h1>🧬 تکامل!</h1><div style='background:rgba(255,255,255,0.05);padding:20px;border-radius:15px;'><h2>{topic}</h2><p>{result[:300]}</p><a href='/' style='color:#667eea;'>⬅️ بازگشت</a></div></html>"
    return "<html dir='rtl' style='background:#1a1a2e;color:white;font-family:Tahoma;padding:20px;text-align:center;'><h1>🧬 در حال تکامل...</h1><a href='/' style='color:#667eea;'>⬅️ بازگشت</a></html>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)