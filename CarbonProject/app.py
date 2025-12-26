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

# === 3. 終極版知識庫 (新增冷知識、挑戰、更多生活議題) ===
KNOWLEDGE_BASE = {
    # --- 核心觀念 ---
    "碳足跡": [
        "👣 <b>碳足跡</b>就是我們在地球上留下的「汙染腳印」。腳印越小，對地球越好！",
        "你知道嗎？連發送 Email、看 Netflix 都有碳足跡喔！不過了解它是減碳的第一步。",
        "碳足跡計算了產品從原料、製造、運送到廢棄的所有溫室氣體排放。"
    ],
    "SDG": [
        "🌍 <b>SDG 13 氣候行動</b>：這是聯合國為了因應氣候變遷所訂下的目標。",
        "SDGs 第 13 項告訴我們要完備減緩調適行動，這也是我們這個網站的設計初衷喔！"
    ],

    # --- 飲食與浪費 ---
    "牛肉": [
        "🥩 <b>少吃牛救地球！</b>生產一公斤牛肉的碳排量，是雞肉的近 10 倍！",
        "牛是反芻動物，打嗝排放的甲烷是強效溫室氣體。建議每週選一天當「無肉日」。"
    ],
    "剩食": [
        "🍱 <b>吃光光最環保！</b>全球有 1/3 的食物被浪費，這些食物腐爛後會產生大量甲烷。",
        "吃多少點多少，減少廚餘就是最簡單的減碳行動！"
    ],
    "水": [
        "💧 <b>有水當思無水之苦。</b>處理自來水需要消耗大量電力，所以節水就是節能！",
        "洗澡改用淋浴代替泡澡，每次可以省下約 50 公升的水喔！"
    ],

    # --- 能源與數位 ---
    "冷氣": [
        "❄️ <b>冷氣省電秘訣：</b>設定 26-28 度 + 電扇，省電又涼快！",
        "濾網太髒會讓冷氣多耗電 10%，記得兩週洗一次濾網喔！"
    ],
    "手機": [
        "📱 <b>數位碳足跡：</b>滑手機也會排碳！因為數據中心的伺服器 24 小時都在吃電。",
        "建議調低螢幕亮度、關閉不用的後台程式，延長手機壽命也是減碳的一種。"
    ],
    "電腦": [
        "💻 電腦不用時記得關機，待機模式其實還是在偷偷耗電喔！",
        "把螢幕亮度調低一點，不僅護眼還能省電減碳。"
    ],

    # --- 生活與時尚 ---
    "衣服": [
        "👕 <b>快時尚的代價：</b>時尚產業的碳排量佔全球 10%！建議多買耐穿的衣服，或選擇二手衣。",
        "一件棉T恤的製作需要 2700 公升的水（夠一個人喝 2.5 年），請珍惜每一件衣服。"
    ],
    "回收": [
        "♻️ <b>鋁罐回收超讚！</b>回收再製鋁罐所需的能量，只有開採新礦的 5%！",
        "紙容器（如便當盒）要先沖洗乾淨再回收，不然會汙染其他紙類喔。"
    ],
    "交通": [
        "🚌 <b>多搭大眾運輸！</b>捷運和公車的平均碳排遠低於自己開車。",
        "如果是短程移動，騎 <b>YouBike</b> 或走路是零碳排的最佳選擇！"
    ],

    # --- ✨ 新增：趣味互動功能 ---
    "冷知識": [
        "🤓 <b>【環保冷知識】</b> 你知道嗎？Google 搜尋一次產生的碳排，大約等於人體體溫產生 0.2 克的 CO2。",
        "🤓 <b>【環保冷知識】</b> 鯊魚其實是海洋的守護者，牠們維持海洋生態平衡，間接幫助海洋吸收碳排！",
        "🤓 <b>【環保冷知識】</b> 竹子的吸碳能力是普通樹木的 4 倍！種竹子超環保。",
        "🤓 <b>【環保冷知識】</b> 發送一封帶附件的 Email，碳排放量約等於開燈 1 小時！"
    ],
    "挑戰": [
        "🔥 <b>【今日減碳挑戰】</b> 試試看今天洗澡時間縮短 2 分鐘！",
        "🔥 <b>【今日減碳挑戰】</b> 今天午餐試著不拿免洗筷，使用自備餐具。",
        "🔥 <b>【今日減碳挑戰】</b> 挑戰今天都不喝瓶裝水，只用保溫杯！",
        "🔥 <b>【今日減碳挑戰】</b> 檢查家裡有沒有沒關的插頭，把它拔掉！"
    ],
    "測驗": [
        "📝 <b>【減碳小測驗】</b> 隨手關燈有幫助嗎？<br>答案：<b>有！</b>積少成多！",
        "📝 <b>【減碳小測驗】</b> 哪種肉類碳排最高？<br>答案：<b>牛肉</b>。因為牛會排放甲烷。",
        "📝 <b>【減碳小測驗】</b> 舊衣服直接丟掉好嗎？<br>答案：<b>不好</b>。紡織垃圾很難分解，建議捐贈或改造。"
    ],

    # --- 基本招呼 ---
    "你好": [
        "你好！我是你的<b>減碳小幫手</b> 🌱。<br>試試看輸入<b>「冷知識」</b>、<b>「挑戰」</b>或<b>「衣服」</b>！",
        "Hi！很高興見到你。今天想來點<b>「冷知識」</b>還是做個<b>「測驗」</b>呢？",
        "你好呀！讓我們一起為地球降溫吧！💪"
    ]
}

DEFAULT_REPLIES = [
    "🤔 這個問題考倒我了... 試試看輸入<b>「冷知識」</b>來聽聽有趣的事？",
    "我還在學習中。不過你可以輸入<b>「挑戰」</b>來領取今天的環保任務！",
    "關於這點我不太確定，但你可以問我關於<b>「衣服」</b>或<b>「手機」</b>的環保知識喔！",
    "您可以試著問我：「什麼是SDG？」或是「吃剩食會怎樣？」"
]

COEFFICIENTS = {"electricity": 0.495, "scooter": 0.046}

# === 4. 網頁路徑 (Routes) ===
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculator')
def calculator_page():
    return render_template('calculator.html')

@app.route('/history')
def history_page():
    records = Record.query.order_by(Record.date.desc()).limit(10).all()
    return render_template('history.html', records=records)

# === 5. API 功能 ===
@app.route('/api/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('message', '')
    reply = ""
    found = False
    
    # 搜尋關鍵字
    for keyword, answers in KNOWLEDGE_BASE.items():
        if keyword in user_msg:
            reply = random.choice(answers) # 隨機挑選一句回答
            found = True
            break
            
    if not found:
        reply = random.choice(DEFAULT_REPLIES)

    time.sleep(0.5) # 模擬思考
    return jsonify({"reply": reply})

@app.route('/api/calculate', methods=['POST'])
def calculate_carbon():
    data = request.json
    try:
        elec = float(data.get('electricity', 0))
        transport_km = float(data.get('transport', 0))
        total_emission = (elec * COEFFICIENTS['electricity']) + \
                         (transport_km * COEFFICIENTS['scooter'])
        
        # 存入資料庫
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
        db.create_all()
    app.run(debug=True, port=5000)