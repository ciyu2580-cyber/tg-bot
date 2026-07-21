import os
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- 1. 防止服务器休眠的 Web 服务 ---
app_web = Flask('')

@app_web.route('/')
def home():
    return "Bot is active and running!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app_web.run(host='0.0.0.0', port=port)

# --- 2. 机器人的交流逻辑 ---
# 处理 /start 命令
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(f"你好，{user_name}！我是你的智能助手，有什么想聊聊的吗？")

# 处理普通聊天消息
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_received = update.message.text
    # 收到什么就自动回复
    reply_text = f"收到你的消息啦！你刚才说的是：“{text_received}”"
    await update.message.reply_text(reply_text)

# --- 3. 启动程序 ---
if __name__ == '__main__':
    # 后台线程启动 Web 服务
    server_thread = Thread(target=run_web)
    server_thread.start()

    # 获取系统环境变量中的 Token
    token = os.environ.get("BOT_TOKEN")
    if not token:
        print("错误：未检测到 BOT_TOKEN 环境变量！")
    else:
        app_bot = ApplicationBuilder().token(token).build()
        
        # 绑定处理器
        app_bot.add_handler(CommandHandler("start", start))
        app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
        
        print("机器人已成功启动！")
        app_bot.run_polling()
