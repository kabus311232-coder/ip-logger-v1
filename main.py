import os
from flask import Flask, render_template_string, request, redirect, session, url_for
from datetime import datetime

app = Flask(__name__)
app.secret_key = "777leak_ultimate_combined_v9"

# --- ÜRÜN VE PAKET VERİLERİ ---
# Tüm ürünler Fivem kategorisine toplandı, diğerleri boş bırakıldı.
products = {
    "Fivem": {
        "MACHO": {
        "desc": "Premium Cheat, Undetected Bypass.",
        "img": "https://media.discordapp.net/attachments/1484310420322779186/1484320776692826222/image.png?ex=69bdccf2&is=69bc7b72&hm=11012a663fc174d33d82962e57677cbba66f35baccf7e39d12b9a10c093e1b62&=&format=webp&quality=lossless",
        "color": "#ff1493",
        "plans": [
            {"time": "Günlük", "price": "200TL"}, {"time": "Haftalık", "price": "400TL"},
            {"time": "Aylık", "price": "800TL"}, {"time": "Sınırsız", "price": "2600TL"}
        ]
    },
    "SUSANO": {
        "desc": "Universal Aimbot, ESP, Silent Aim.",
        "img": "https://media.discordapp.net/attachments/1484310420322779186/1484321029923930292/image.png?ex=69bdcd2e&is=69bc7bae&hm=563e0ad01dfcb801f32441f29bd3b5f3e261bdbf30db19a4b3252bc957171fe2&=&format=webp&quality=lossless",
        "color": "#8a2be2",
        "plans": [
            {"time": "Haftalık", "price": "420TL"}, {"time": "Aylık", "price": "900TL"},
            {"time": "Sınırsız", "price": "3600TL"}
        ]
    },
    "FMA LUA": {
        "desc": "Advanced Script Execution Engine.",
        "img": "GÖRSEL_LINKI_BURAYA",
        "color": "#00ffff",
        "plans": [
            {"time": "Haftalık", "price": "300TL"}, {"time": "Aylık", "price": "600TL"},
            {"time": "Sınırsız", "price": "1500TL"}
        ]
    },
    "SPOOFER": {
        "desc": "HWID Ban Removal. Safe & Undetected.",
        "img": "https://media.discordapp.net/attachments/1484310420322779186/1484321617881333981/image.png?ex=69bdcdbb&is=69bc7c3b&hm=73a5f6c74e794141a399d68520885835afa112afc9b0676325942a114d97a187&=&format=webp&quality=lossless",
        "color": "#00ff00",
        "plans": [
            {"time": "Haftalık", "price": "300TL"}, {"time": "Aylık", "price": "600TL"},
            {"time": "Sınırsız", "price": "1000TL"}
        ]
    },
    "REDENGINE": {
        "desc": "The Ultimate GTA V Mod Menu.",
        "img": "https://media.discordapp.net/attachments/1484310420322779186/1484321430110863441/image.png?ex=69bdcd8e&is=69bc7c0e&hm=ca00bcb2702ee61998f867c9bfe910cc6d6e158456f4bede1a4b3c0c85d39eab&=&format=webp&quality=lossless",
        "color": "#ff0000",
        "plans": [
            {"time": "Haftalık", "price": "480TL"}, {"time": "Aylık", "price": "850TL"},
            {"time": "Sınırsız", "price": "2500TL"}

            ]
        }
    },
    "Minecraft": {
        "777 CLIENT": {
            "desc": "Minecraft için en gelişmiş ghost client.",
            "img": "https://media.discordapp.net/attachments/1482399359193710704/1484334464740888770/image.png?ex=69bdd9b1&is=69bc8831&hm=68895f81ce875bd0c5a18e00ea9a290a44cb8674496e7df213a4938d7830dff8&=&format=webp&quality=lossless", 
            "color": "#00ff00",
            "plans": [
                {"time": "Haftalık", "price": "150TL"},
                {"time": "Aylık", "price": "350TL"},
                {"time": "Sınırsız", "price": "900TL"}
            ]
        }
    },
    "Roblox": {}
}

UI_STYLE = """
<style>
    :root { --main: #8a2be2; --bg: #000; --card: #080808; --neon: #ff00ff; --discord: #5865F2; }
    body { background: var(--bg); color: #fff; font-family: 'Segoe UI', sans-serif; margin: 0; padding: 0; overflow-x: hidden; scroll-behavior: smooth; }
    
    .navbar { display: flex; justify-content: space-between; align-items: center; padding: 15px 50px; background: rgba(0,0,0,0.95); backdrop-filter: blur(10px); border-bottom: 2px solid var(--main); position: fixed; width: 100%; top: 0; z-index: 1000; box-sizing: border-box; }
    .brand-logo { font-size: 24px; font-weight: 900; color: var(--neon); text-shadow: 0 0 15px var(--neon); text-transform: uppercase; }
    .nav-links a { color: #aaa; text-decoration: none; margin: 0 15px; font-weight: bold; transition: 0.3s; }
    .nav-links a:hover { color: var(--neon); }
    .btn-discord { background: var(--discord); color: #fff; text-decoration: none; padding: 10px 20px; border-radius: 8px; font-weight: bold; transition: 0.3s; }

    .hero { 
        height: 60vh; 
        background: url('https://media.discordapp.net/attachments/1482399359193710704/1484336658118611034/content.png?ex=69bddbbc&is=69bc8a3c&hm=98c79bbaf487f2535066de8d7f54e6f146892fb50f9d39b71c64e1599c0a5a7a&=&format=webp&quality=lossless&width=1376&height=917') no-repeat center center; 
        background-size: cover; 
        display: flex; align-items: center; justify-content: center;
    }

    .category-section { padding: 60px 20px; max-width: 1300px; margin: auto; }
    .cat-title { font-size: 30px; color: var(--neon); border-left: 5px solid var(--main); padding-left: 15px; margin-bottom: 30px; text-transform: uppercase; }
    
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 25px; }
    .card { background: var(--card); border-radius: 12px; border: 1px solid #111; overflow: hidden; transition: 0.3s; text-align: center; padding-bottom: 20px; }
    .card:hover { border-color: var(--main); box-shadow: 0 0 20px rgba(138,43,226,0.3); }
    
    .img-box { height: 200px; background: #000; overflow: hidden; }
    .img-box img { width: 100%; height: 100%; object-fit: cover; opacity: 0.7; }
    
    .btn-buy { background: linear-gradient(45deg, #8a2be2, #ff00ff); border: none; color: #fff; padding: 12px; border-radius: 6px; cursor: pointer; font-weight: bold; transition: 0.3s; width: 85%; margin-top: 15px; }

    /* MODAL */
    .modal { display: none; position: fixed; z-index: 2000; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.95); backdrop-filter: blur(10px); }
    .modal-content { background: #080808; margin: 10% auto; padding: 30px; border: 2px solid var(--main); border-radius: 20px; width: 80%; max-width: 800px; text-align: center; position: relative; }
    .plan-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-top: 20px; }
    .plan-card { background: #111; padding: 15px; border-radius: 10px; border: 1px solid #222; }
    .plan-price { color: #00ff00; font-weight: bold; font-size: 1.4rem; display: block; margin: 10px 0; }
    .close { position: absolute; top: 15px; right: 20px; font-size: 30px; cursor: pointer; color: #555; }
</style>
"""

@app.route('/')
def index():
    return render_template_string(f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head><meta charset="UTF-8"><title>777LEAK SHOP</title>{UI_STYLE}</head>
    <body>
        <nav class="navbar">
            <div class="brand-logo">777LEAK SHOP</div>
            <div class="nav-links">
                <a href="/">Anasayfa</a>
                <a href="#Fivem">Fivem</a>
                <a href="#Minecraft">Minecraft</a>
                <a href="#Roblox">Roblox</a>
            </div>
            <a href="https://discord.gg/777leak" class="btn-discord">Discord</a>
        </nav>

        <div class="hero">
            <h1 style="font-size: 50px; text-shadow: 0 0 30px var(--neon);">777LEAK EXCLUSIVE</h1>
        </div>

        {{% for cat, items in products.items() %}}
        <div class="category-section" id="{{{{ cat }}}}">
            <h2 class="cat-title">{{{{ cat }}}}</h2>
            <div class="grid">
                {{% if items %}}
                    {{% for name, data in items.items() %}}
                    <div class="card">
                        <div class="img-box"><img src="{{{{ data.img }}}}" alt=""></div>
                        <h3 style="margin-top:15px;">{{{{ name }}}}</h3>
                        <p style="color:#666; font-size:14px; padding:0 10px;">{{{{ data.desc }}}}</p>
                        <button class="btn-buy" onclick='openPlans("{{{{ cat }}}}", "{{{{ name }}}}")'>SEÇENEKLERİ GÖR</button>
                    </div>
                    {{% endfor %}}
                {{% else %}}
                    <div style="color:#444;">Bu kategoride henüz ürün bulunmamaktadır.</div>
                {{% endif %}}
            </div>
        </div>
        {{% endfor %}}

        <div id="planModal" class="modal">
            <div class="modal-content">
                <span class="close" onclick="closeModal()">&times;</span>
                <h2 id="m_title"></h2>
                <div id="m_plans" class="plan-grid"></div>
            </div>
        </div>

        <script>
            const allData = {products};
            function openPlans(cat, name) {{
                const p = allData[cat][name];
                document.getElementById('m_title').innerText = name + " PAKETLERİ";
                let html = "";
                p.plans.forEach(plan => {{
                    html += `<div class="plan-card">
                        <span>${{plan.time}}</span>
                        <span class="plan-price">${{plan.price}}</span>
                        <a href="https://discord.gg/777leak" style="color:#1ed760; text-decoration:none; font-weight:bold;">SATIN AL</a>
                    </div>`;
                }});
                document.getElementById('m_plans').innerHTML = html;
                document.getElementById('planModal').style.display = "block";
            }}
            function closeModal() {{ document.getElementById('planModal').style.display = "none"; }}
        </script>
    </body>
    </html>
    """, products=products)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
