import os
from flask import Flask, render_template_string, request, redirect, session, url_for
import requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = "777leak_gizli_anahtar" # Session güvenliği için

# --- AYARLAR ---
ADMIN_USER = "adminsl"
ADMIN_PASS = "3112"
MEMO_CODE = """--[[ 777LEAK SCRIPT AKTIF ]]
loadstring(game:HttpGet('https://raw.githubusercontent.com/Documantation12/Universal-Vehicle-Script/main/Main.lua'))()"""

# IP'leri hafızada tutmak için liste (Site kapandığında sıfırlanır)
visitor_logs = []

def send_discord_log(ip, ua):
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if webhook_url:
        data = {
            "embeds": [{
                "title": "🌐 777LEAK - Yeni Giriş!",
                "description": f"**IP:** `{ip}`\n**Cihaz:** `{ua}`",
                "color": 12517631,
                "footer": {"text": f"Zaman: {datetime.now().strftime('%H:%M:%S')}"}
            }]
        }
        try: requests.post(webhook_url, json=data)
        except: pass

# --- ARAYÜZLER (HTML) ---
LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Admin Login</title>
    <style>
        body { background: #050505; color: #ff00ff; font-family: monospace; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
        .login-box { padding: 40px; border: 2px solid #8a2be2; box-shadow: 0 0 20px #8a2be2; background: #000; border-radius: 10px; text-align: center; }
        input { background: #111; border: 1px solid #8a2be2; color: #fff; padding: 10px; margin: 10px 0; width: 100%; border-radius: 5px; }
        button { background: #8a2be2; color: #fff; border: none; padding: 10px 20px; cursor: pointer; font-weight: bold; width: 110%; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>777LEAK ADMIN</h2>
        <form method="POST">
            <input type="text" name="user" placeholder="Kullanıcı Adı" required>
            <input type="password" name="pass" placeholder="Şifre" required>
            <button type="submit">GİRİŞ YAP</button>
        </form>
    </div>
</body>
</html>
"""

ADMIN_PANEL_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Admin Panel</title>
    <style>
        body { background: #050505; color: #fff; font-family: monospace; padding: 20px; }
        h1 { color: #ff00ff; text-shadow: 0 0 10px #ff00ff; border-bottom: 2px solid #8a2be2; padding-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #333; padding: 12px; text-align: left; }
        th { background: #1a1a1a; color: #ff00ff; }
        tr:nth-child(even) { background: #0a0a0a; }
        .logout { color: red; text-decoration: none; float: right; }
    </style>
</head>
<body>
    <a href="/logout" class="logout">[ ÇIKIŞ YAP ]</a>
    <h1>777LEAK ZİYARETÇİ LOGLARI</h1>
    <table>
        <tr>
            <th>IP Adresi</th>
            <th>Cihaz / Tarayıcı</th>
            <th>Zaman</th>
        </tr>
        {% for log in logs %}
        <tr>
            <td style="color: #00ff00;">{{ log.ip }}</td>
            <td style="font-size: 12px;">{{ log.ua }}</td>
            <td>{{ log.time }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

# --- YOLLAR (ROUTES) ---

@app.route('/')
def index():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0]
    ua = request.headers.get('User-Agent')
    zaman = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Logu listeye ekle
    visitor_logs.insert(0, {"ip": ip, "ua": ua, "time": zaman})
    
    # Discord'a gönder
    send_discord_log(ip, ua)
    
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>777Leak</title>
        <style>
            body { background: #050505; color: #ff00ff; font-family: monospace; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }
            .box { padding: 30px; border: 2px solid #8a2be2; box-shadow: 0 0 20px #8a2be2; background: #000; border-radius: 10px; width: 85%; max-width: 700px; position: relative; }
            h1 { color: #fff; text-shadow: 0 0 10px #bf00ff; letter-spacing: 5px; font-size: 2.5rem; }
            pre { background: #111; padding: 15px; border: 1px solid #333; color: #00ff00; overflow-x: auto; white-space: pre-wrap; text-align: left; }
            .btn { position: absolute; top: 15px; right: 15px; background: #8a2be2; color: #fff; border: none; padding: 10px 20px; cursor: pointer; border-radius: 5px; font-weight: bold; }
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
                alert('Script Kopyalandı!');
            }
        </script>
    </body>
    </html>
    """, code=MEMO_CODE)

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form['user'] == ADMIN_USER and request.form['pass'] == ADMIN_PASS:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_panel'))
    return render_template_string(LOGIN_HTML)

@app.route('/admin/panel')
def admin_panel():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    return render_template_string(ADMIN_PANEL_HTML, logs=visitor_logs)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
