import discord
from discord.ext import commands
import google.generativeai as genai
import asyncio
import os

# ================= CẤU HÌNH BẢO MẬT =================
# Code sẽ tự động lấy Token và API Key từ biến môi trường (Environment Variables)
# Bạn sẽ nhập các key này vào phần Variables trên Railway (không nhập vào đây)
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Kiểm tra xem đã nhập Key chưa
if not DISCORD_TOKEN or not GEMINI_API_KEY:
    print("LỖI: Chưa cấu hình DISCORD_TOKEN hoặc GEMINI_API_KEY trong biến môi trường!")
    exit()

# Cấu hình AI
genai.configure(api_key=GEMINI_API_KEY)
# Dùng model gemini-1.5-flash để chạy nhanh và ổn định hơn
model = genai.GenerativeModel('gemini-1.5-flash')

# Cấu hình Bot
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents)

# ================= HÀM HỖ TRỢ AI =================
async def ask_ai(prompt):
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, model.generate_content, prompt)
        return response.text
    except Exception as e:
        print(f"Lỗi AI: {e}")
        return "Não bộ AI đang bận, thử lại sau nhé!"

# ================= SỰ KIỆN BOT =================
@bot.event
async def on_ready():
    print(f'🤖 Bot {bot.user} đã online và sẵn sàng!')
    print('Gõ !build trong server Discord để bắt đầu tạo cấu trúc.')

# ================= LỆNH BUILD SERVER (YORUS STYLE) =================
@bot.command()
@commands.has_permissions(administrator=True)
async def build(ctx):
    guild = ctx.guild
    await ctx.send("⏳ **Đang xây dựng Server theo phong cách Yorus...** (Vui lòng đợi trong giây lát)")

    # 1. XÓA TOÀN BỘ KÊNH CŨ
    for channel in guild.channels:
        try:
            await channel.delete()
        except:
            pass

    # 2. TẠO CẤU TRÚC KÊNH (Giống hệt ảnh bạn gửi)
    server_structure = {
        "1. ✧ : Server Info ˎˊ-": [
            ("voice", "📢 · thông-báo"),
            ("text", "📚 · rules"),
            ("text", "🎉 · giveaway"),
            ("text", "🎭 · pick-role"),
            ("text", "🚀 · boost"),
            ("text", "🤖 · link-bot"),
            ("text", "🥽 · vr-status"),
            ("text", "🛒 · bút-vi"),
            ("voice", "Séch Voice")
        ],
        "2. ✧ : Welcome & Goodbye ˎˊ-": [
            ("text", "🤗 · wellcum"),
            ("text", "👋 · goodbye")
        ],
        "3. ✧ : gay ˎˊ-": [
            ("text", "💬 · chat"),
            ("text", "💬 · toxic-chat"),
            ("text", "🩷-🩷-🩷"),
            ("text", "🦅 · owocash"),
            ("text", "🤖 · commands"),
            ("text", "💾 · save")
        ],
        "4. ✧ : Ticket ˎˊ-": [
            ("text", "🎟️ · ticket")
        ],
        "5. ✧ : PARTNER ˎˊ-": [
            ("text", "📚 · partner-rules"),
            ("text", "🤝 · partner-list")
        ],
        "6. ✧ : VOICE ˎˊ-": [
            ("voice", "Kiếm ni"),
            ("voice", "ha meo dthw")
        ]
    }

    await ctx.send("🔹 Đang tạo Categories & Channels...")

    for cat_name, channels in server_structure.items():
        category = await guild.create_category(cat_name)
        
        for ch_type, ch_name in channels:
            if ch_type == "voice":
                await guild.create_voice_channel(name=ch_name, category=category)
            else:
                # Dùng AI viết mô tả cho kênh text
                prompt = f"Viết mô tả ngắn (dưới 40 chữ) cho kênh Discord tên '{ch_name}' thuộc mục '{cat_name}'. Trả về duy nhất câu mô tả."
                topic = await ask_ai(prompt)
                await guild.create_text_channel(name=ch_name, category=category, topic=topic)

    # 3. TẠO ROLES CƠ BẢN
    await ctx.send("🔹 Đang tạo Roles...")
    roles = ["Admin", "Moderator", "Partner", "Member", "Bot"]
    for r in roles:
        if not discord.utils.get(guild.roles, name=r):
            await guild.create_role(name=r, colour=discord.Colour.random())

    # 4. GỬI NỘI QUY BẰNG AI VÀO KÊNH #rules
    await ctx.send("🔹 Đang nhờ AI soạn thảo Nội quy...")
    rules_channel = discord.utils.get(guild.text_channels, name="📚 · rules")
    if rules_channel:
        rules_prompt = "Viết 6 điều nội quy ngắn gọn, chuyên nghiệp cho server Discord Gaming/Cộng đồng. Có icon cảm xúc ở đầu mỗi dòng. Đánh số thứ tự."
        rules_text = await ask_ai(rules_prompt)
        embed = discord.Embed(
            title="📜 NỘI QUY SERVER YORUS", 
            description=rules_text, 
            color=discord.Color.purple()
        )
        await rules_channel.send(embed=embed)

    await ctx.send("✅ **Đã xây dựng xong Server!** Hãy kiểm tra lại các kênh và Role.")

# ================= TÍNH NĂNG CHAT VỚI AI =================
@bot.command()
async def ask(ctx, *, question):
    """Gõ !ask <câu hỏi> để trò chuyện với AI"""
    await ctx.send("🤔 Đang suy nghĩ...")
    answer = await ask_ai(question)
    
    # Discord giới hạn 2000 ký tự, cắt bớt nếu AI nói dài
    if len(answer) > 1900:
        answer = answer[:1900] + "..."
        
    await ctx.reply(answer)

# ================= CHẠY BOT =================
bot.run(DISCORD_TOKEN)
