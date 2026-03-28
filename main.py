import discord
from discord import app_commands
from discord.ext import commands
import os
import re
import asyncio
from flask import Flask
from threading import Thread

# --- RENDER İÇİN WEB SUNUCUSU ---
app = Flask('')

@app.route('/')
def home():
    return "Bot Aktif ve Koruma Devrede!"

def run():
    # Render genellikle 8080 portunu tercih eder
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- AYARLAR ---
# Render Panelinde 'Environment' kısmına TOKEN, KATEGORI_ID ve OTO_ROL_ID eklemeyi unutma!
TOKEN = 'MTQ4NzQ1NTc3NjkzNDE5OTQwNw.G4al0W.Tesq_-OImof2-2BKfGLkX41myRmdDkNyYcczN0'
KATEGORI_ID =  1487456333299974276 # Kumarhane odaları kategorisi
OTO_ROL_ID = 1487520928182308976   # Yeni gelenlere verilecek rol ID
VARSAYILAN_FOTOGRAF = "https://media.discordapp.net/attachments/1486745717744865323/1487456786620354610/HCEEuUVXwAARc0B.png?ex=69c93595&is=69c7e415&hm=63e5dc21ce0fc9787f63633dfbcc4ab433e0d6ad9c9060a0fe58fe1dd6eec5ce&format=webp&quality=lossless&width=960&height=960&"
KUFUR_LISTESI = ["küfür1", "küfür2", "anan", "bacın"] # Burayı genişletebilirsin

# --- ÖZEL ODA BUTON SİSTEMİ ---
class OdaAcButonu(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Kalıcı buton

    @discord.ui.button(label="🎰 Özel Oda Oluştur", style=discord.ButtonStyle.blurple, custom_id="kumarhane_oda_ac")
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        category = guild.get_channel(KATEGORI_ID)

        if not category:
            return await interaction.response.send_message("❌ Hata: Kategori bulunamadı!", ephemeral=True)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, connect=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        channel = await guild.create_text_channel(
            name=f"🎰-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )

        await interaction.response.send_message(f"✅ Odan hazırlandı: {channel.mention}", ephemeral=True)
        
        embed = discord.Embed(
            title="🎰 Hoş Geldin!", 
            description=f"Selam {interaction.user.mention}, bu oda sadece senin görebileceğin şekilde oluşturuldu.", 
            color=0xFF00FF
        )
        await channel.send(embed=embed)

class KorumaBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self.anti_spam_counter = {}

    async def setup_hook(self):
        # Butonun bot kapanıp açılsa da çalışması için register ediyoruz
        self.add_view(OdaAcButonu())
        await self.tree.sync()

    async def on_ready(self):
        print(f'{self.user} olarak giriş yapıldı! Sistemler aktif.')

bot = KorumaBot()

# --- 1. OTO ROL ---
@bot.event
async def on_member_join(member):
    role = member.guild.get_role(OTO_ROL_ID)
    if role:
        try:
            await member.add_roles(role)
        except:
            pass

# --- 2. KORUMA SİSTEMLERİ ---
@bot.event
async def on_message(message):
    if message.author.bot or message.author.guild_permissions.administrator:
        return

    content = message.content.lower()

    # Küfür ve Reklam (URL) Kontrolü
    url_pattern = r"(https?://\S+|discord\.gg/\S+)"
    if any(k in content for k in KUFUR_LISTESI) or re.search(url_pattern, content):
        await message.delete()
        return

    # Spam Kontrolü (5 saniyede 5 mesaj)
    u_id = message.author.id
    if u_id not in bot.anti_spam_counter: bot.anti_spam_counter[u_id] = []
    now = asyncio.get_event_loop().time()
    bot.anti_spam_counter[u_id] = [t for t in bot.anti_spam_counter[u_id] if now - t < 5]
    bot.anti_spam_counter[u_id].append(now)

    if len(bot.anti_spam_counter[u_id]) > 5:
        await message.delete()
        return

    await bot.process_commands(message)

# --- 3. PANEL KOMUTU ---
@bot.tree.command(name="panel", description="Özel oda açma panelini kurar.")
@app_commands.describe(gorsel_url="Panelde görünecek fotoğrafın linki")
async def panel(interaction: discord.Interaction, gorsel_url: str = None):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("Bu yetkin yok!", ephemeral=True)

    embed = discord.Embed(
        title="🎰 Özel Oda Sistemi",
        description="Aşağıdaki butona tıklayarak sadece size özel bir oda açabilirsiniz.\n\n**Kurallar:**\n🚫 Küfür, reklam ve spam yasaktır.",
        color=0xFF00FF
    )
    
    foto = gorsel_url if gorsel_url else VARSAYILAN_FOTOGRAF
    embed.set_image(url=foto)
    
    await interaction.response.send_message("Panel kuruluyor...", ephemeral=True)
    await interaction.channel.send(embed=embed, view=OdaAcButonu())

# --- BAŞLATMA ---
if __name__ == "__main__":
    keep_alive()
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("HATA: TOKEN bulunamadı!")
