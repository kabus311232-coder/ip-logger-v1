import os
from flask import Flask, render_template_string, request, redirect, session, url_for, flash
import requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = "777leak_ultra_secret_key_99"

# --- AYARLAR ---
ADMIN_USER = "adminsl"
ADMIN_PASS = "3112"
MEMO_CODE = """--[[ 777LEAK SCRIPT AKTIF ]]
loadstring(game:HttpGet('https://raw.githubusercontent.com/Documantation12/Universal-Vehicle-Script/main/Main.lua'))()"""

# Veritabanı (Site yeniden başlayınca sıfırlanır)
users = {} 
visitor_logs = []

def send_discord_log(title, message):
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if webhook_url:
        data = {"embeds": [{"title": title, "description": message, "color": 12517631}]}
        try: requests.post(webhook_url, json=data, timeout=5)
        except: pass

# --- TASARIM (CSS) ---
UI_STYLE = """
<style>
    body { background: #050505; color: #fff; font-family: 'Segoe UI', sans-serif; display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; flex-direction: column; overflow-x: hidden; }
    .card { background: #000; border: 2px solid #8a2be2; box-shadow: 0 0 25px #8a2be2; padding: 40px; border-radius: 15px; width: 380px; text-align: center; position: relative; animation: glow 2s infinite alternate; }
    @keyframes glow { from { box-shadow: 0 0 15px #8a2be2; } to { box-shadow: 0 0 30px #ff00ff; } }
    h1, h2 { color: #fff; text-shadow: 0 0 15px #ff00ff; letter-spacing: 3px; font-weight: 900; margin-bottom: 25px; }
    input { background: #0a0a0a; border: 1px solid #333; color: #fff; padding: 14px; margin: 12px 0; width: 90%; border-radius: 8px; font-size: 1rem; transition: 0.3s; }
    input:focus { border-color: #ff00ff; outline: none; box-shadow: 0 0 15px #ff00ff; }
    .btn { background: linear-gradient(45deg, #8a2be2, #ff00ff); color: #fff; border: none; padding: 14px; width: 100%; border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 1.1rem; margin-top: 15px; transition: 0.3s; }
    .btn:hover { transform: translateY(-3px); box-shadow: 0 5px 20px #ff00ff; }
    pre { background: #080808; padding: 20px; color: #00ff00; text-align: left; overflow-x: auto; border: 1px solid #1a1a1a; border-radius: 10px; font-family: 'Consolas', monospace; font-size: 0.9rem; line-height: 1.5; }
    .footer-link { color: #666; text-decoration: none; font-size: 0.85rem; margin-top: 20px; display: inline-block; transition: 0.3s; }
    .footer-link:hover { color: #ff00ff; }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 0.8rem; }
    th, td { border: 1px solid #222; padding: 10px; text-align: left; }
    th { color: #ff00ff; text-transform: uppercase; }
    .ip-green { color: #00ff00; font-weight: bold; }
</style>
"""

# --- FONKSİYONLAR ---

@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Giriş yapanın IP'sini logla
    ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0]
    ua = request.headers.get('User-Agent')
    visitor_logs.insert(0, {"ip": ip, "ua": ua, "time": datetime.now().strftime("%H:%M:%S")})

    return render_template_string(f"""
    {UI_STYLE}
    <div class="card" style="width: 85%; max-width: 800px;">
        <h1>777LEAK PANEL</h1>
        <p style="color:#aaa;">Hoş geldin <b style="color:#ff00ff;">{{{{ session['user'] }}}}</b></p>
        <div style="position: relative; margin-top:20px;">
            <button onclick="copyCode()" class="btn" style="width:auto; position:absolute; top:-10px; right:10px; padding:8px 15px; font-size:0.8rem;">KOPYALA</button>
            <pre id="scriptContent">{{{{ code }}}}</pre>
        </div>
        <a href="/logout" class="footer-link" style="color:#ff4444;">[ OTURUMU KAPAT ]</a>
    </div>
    <script>
        function copyCode() {{
            var content = document.getElementById('scriptContent').innerText;
            navigator.clipboard.writeText(content);
            alert('Script kopyalandı!');
        }}
    </script>
    """, code=MEMO_CODE)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = request.form.get('user')
        pw = request.form.get('pass')
        if user in users:
            flash("Kullanıcı adı zaten mevcut!")
        else:
            users[user] = pw
            send_discord_log("📝 Yeni Kayıt", f"**User:** `{user}`")
            return redirect(url_for('login'))
    return render_template_string(f"""
    {UI_STYLE}
    <div class="card">
        <h2>KAYIT OL</h2>
        <form method="POST">
            <input type="text" name="user" placeholder="Kullanıcı Adı" required>
            <input type="password" name="pass" placeholder="Şifre" required>
            <button type="submit" class="btn">HESAP OLUŞTUR</button>
        </form>
        <a href="/login" class="footer-link">Giriş Yap</a>
    </div>
    """)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('user')
        pw = request.form.get('pass')
        
        # Admin Girişi
        if user == ADMIN_USER and pw == ADMIN_PASS:
            session['admin'] = True
            return redirect(url_for('admin_panel'))
            
        # Normal Kullanıcı Girişi
        if user in users and users[user] == pw:
            session['user'] = user
            return redirect(url_for('home'))
        else:
            return "<script>alert('Hatalı Bilgi!'); window.location='/login';</script>"

    return render_template_string(f"""
    {UI_STYLE}
    <div class="card">
        <h2>GİRİŞ YAP</h2>
        <form method="POST">
            <input type="text" name="user" placeholder="Kullanıcı Adı" required>
            <input type="password" name="pass" placeholder="Şifre" required>
            <button type="submit" class="btn">SİSTEME GİR</button>
        </form>
        <a href="/register" class="footer-link">Hesabın yok mu? Kayıt Ol</a>
    </div>
    """)

@app.route('/admin/panel')
def admin_panel():
    if not session.get('admin'):
        return redirect(url_for('login'))
    return render_template_string(f"""
    {UI_STYLE}
    <div style="width: 95%; max-width: 1000px; background:#000; padding:30px; border:2px solid #ff00ff; border-radius:15px;">
        <h1 style="text-align:center;">ADMIN LOG PANELİ</h1>
        <div style="text-align:right;"><a href="/logout" style="color:red;">[ ÇIKIŞ ]</a></div>
        
        <h3 style="color:#ff00ff;">SON GİRİŞ YAPANLAR (IP LOGGER)</h3>
        <table>
            <tr><th>IP ADRESI</th><th>CIHAZ</th><th>ZAMAN</th></tr>
            {{% for log in logs %}}
            <tr><td class="ip-green">{{ log.ip }}</td><td style="color:#888;">{{ log.ua }}</td><td>{{ log.time }}</td></tr>
            {{% endfor %}}
        </table>
        
        <h3 style="color:#ff00ff; margin-top:30px;">KAYITLI ÜYELER</h3>
        <div style="color:#00ff00;">{{% for u in u_list %}} [{{ u }}] {{% endfor %}}</div>
    </div>
    """, logs=visitor_logs, u_list=users.keys())

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    # Render Port Ayarı (Kritik)
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
