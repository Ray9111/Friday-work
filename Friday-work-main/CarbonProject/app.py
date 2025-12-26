import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import time
import random

app = Flask(__name__)

# === 1. 資料庫設定 ===
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///carbon.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# === 2. 定義資料表模型 ===
class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.now)
    electricity = db.Column(db.Float)
    transport = db.Column(db.Float)
    total_co2 = db.Column(db.Float)

# === 3. 知識庫與設定 ===
KNOWLEDGE_BASE = {
    "碳足跡": "碳足跡是指一個活動或產品在其生命週期中，直接或間接產生的溫室氣體排放量。",
    "牛肉": "牛肉的碳排放量非常高（每公斤約 60 kgCO2e）。建議多選擇雞肉或植物性飲食。",
    "冷氣": "建議設定在 26-28 度並搭配電扇，每調高 1 度可省電 6%。",
    "交通": "建議多搭乘捷運、公車，或騎乘 YouBike。",
    "你好": "你好！我是你的減碳小幫手。你可以問我關於『碳足跡』的問題喔！"
}
DEFAULT_REPLIES = ["這個問題我還在學習中，要不要問問關於『節能』的方法？", "建議參考環保署資料，或者我們可以聊聊飲食減碳？"]
COEFFICIENTS = {"electricity": 0.495, "scooter": 0.046}

# === 4. 網頁路徑 (Routes) ===
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculator')
def calculator_page():
    return render_template('calculator.html')

# ⚠️ 這裡就是你原本缺少的「歷史紀錄」路徑
@app.route('/history')
def history_page():
    # 撈出最近 10 筆資料
    records = Record.query.order_by(Record.date.desc()).limit(10).all()
    return render_template('history.html', records=records)

# === 5. API 功能 ===
@app.route('/api/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('message', '')
    reply = ""
    found = False
    for keyword, answer in KNOWLEDGE_BASE.items():
        if keyword in user_msg:
            reply = answer
            found = True
            break
    if not found:
        reply = random.choice(DEFAULT_REPLIES)
    time.sleep(0.5)
    return jsonify({"reply": reply})

@app.route('/api/calculate', methods=['POST'])
def calculate_carbon():
    data = request.json
    try:
        elec = float(data.get('electricity', 0))
        transport_km = float(data.get('transport', 0))
        total_emission = (elec * COEFFICIENTS['electricity']) + \
                         (transport_km * COEFFICIENTS['scooter'])
        
        # 儲存到資料庫
        new_record = Record(
            electricity=elec,
            transport=transport_km,
            total_co2=round(total_emission, 2)
        )
        db.session.add(new_record)
        db.session.commit()

        advice = "您的碳排放控制得很棒！" if total_emission <= 100 else "碳排偏高，建議減少冷氣使用！"
        
        return jsonify({
            "success": True,
            "total": round(total_emission, 2),
            "advice": advice
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # 確保資料庫檔案建立
    app.run(debug=True, port=5000)