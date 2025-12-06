from flask import Flask, request, jsonify
import requests
import json
from datetime import datetime

app = Flask(__name__)

# ===== CẤU HÌNH =====
import os
TELEGRAM_BOT_TOKEN = os.environ.get('8237221009:AAGzLVpVnPcZUzrrjtS60XA38JJywsRNMRk')  # Lấy từ @BotFather
TELEGRAM_CHAT_ID = os.environ.get('5690514116')     # Lấy từ @userinfobot

def send_telegram_message(message):
    """Gửi tin nhắn đến Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"Lỗi gửi Telegram: {e}")
        return None

def format_alert_message(data):
    """Format tin nhắn alert"""
    alert_type = data.get('type', 'unknown')
    symbol = data.get('symbol', 'N/A')
    timeframe = data.get('timeframe', 'N/A')
    price = data.get('price', 'N/A')
    
    # Emoji cho từng loại tín hiệu
    emoji_map = {
        'bullish_divergence': '🟢📈',
        'bearish_divergence': '🔴📉',
        'bullish_convergence': '🔵⬆️',
        'bearish_convergence': '🟠⬇️'
    }
    
    # Tên tiếng Việt
    name_map = {
        'bullish_divergence': 'PHÂN KỲ TĂNG',
        'bearish_divergence': 'PHÂN KỲ GIẢM',
        'bullish_convergence': 'HỘI TỤ TĂNG (Fast MA cắt lên)',
        'bearish_convergence': 'HỘI TỤ GIẢM (Fast MA cắt xuống)'
    }
    
    emoji = emoji_map.get(alert_type, '⚠️')
    name = name_map.get(alert_type, alert_type.upper())
    
    message = f"""
{emoji} <b>{name}</b>

📊 Cặp: <b>{symbol}</b>
⏰ Khung: <b>{timeframe}</b>
💰 Giá: <b>{price}</b>
🕐 Thời gian: <b>{datetime.now().strftime('%H:%M:%S %d/%m/%Y')}</b>
"""
    
    # Thêm thông tin MA nếu có
    if 'fastMA' in data and 'slowMA' in data:
        message += f"\n📉 Fast MA: {data['fastMA']:.2f}"
        message += f"\n📈 Slow MA: {data['slowMA']:.2f}"
    
    return message.strip()

@app.route('/webhook', methods=['POST'])
def webhook():
    """Nhận webhook từ TradingView"""
    try:
        # Lấy dữ liệu JSON từ TradingView
        data = request.json
        print(f"Nhận alert: {data}")
        
        # Format và gửi tin nhắn
        message = format_alert_message(data)
        result = send_telegram_message(message)
        
        if result:
            return jsonify({'status': 'success', 'message': 'Đã gửi Telegram'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Lỗi gửi Telegram'}), 500
            
    except Exception as e:
        print(f"Lỗi xử lý webhook: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/test', methods=['GET'])
def test():
    """Test endpoint"""
    test_message = "✅ Bot đang hoạt động!"
    send_telegram_message(test_message)
return jsonify({'status': 'ok', 'message': 'Test message sent'})

@app.route('/', methods=['GET'])
def home():
    """Trang chủ"""
    return """
    <h1>TDI Telegram Webhook Bot</h1>
    <p>Bot đang chạy!</p>
    <ul>
        <li><a href="/test">Test gửi Telegram</a></li>
    </ul>
    """

if __name__ == '__main__':
    print("🚀 Bot đang khởi động...")
    print(f"📱 Telegram Chat ID: {TELEGRAM_CHAT_ID}")
    app.run(host='0.0.0.0', port=5000, debug=True)
