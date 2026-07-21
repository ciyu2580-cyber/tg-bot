import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from flask import Flask
from threading import Thread

# --------------------------------------------------
# 已填入你的真实 ID
ADMIN_ID = 5410690182  
# --------------------------------------------------

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_id = update.message.from_user.id
    text = update.message.text

    # 1. 如果是你（管理员）在回复某条被转发的消息
    if user_id == ADMIN_ID:
        if update.message.reply_to_message and update.message.reply_to_message.text:
            reply_msg = update.message.reply_to_message.text
            if "ID:" in reply_msg:
                try:
                    # 从转发消息中提取原发送者的 ID
                    target_id = int(reply_msg.split("ID:")[1].split("\n")[0].strip())
                    # 以机器人的名义给对方发消息
                    await context.bot.send_message(chat_id=target_id, text=text)
                    await update.message.reply_text("✅ 已成功以机器人名义回复！")
                except Exception as e:
                    await update.message.reply_text(f"❌ 发送失败: {e}")
        return

    # 2. 如果是其他用户给机器人发消息，自动转发给你
    sender_name = update.message.from_user.full_name
    forward_text = f"📩 **收到新消息**\nID:{user_id}\n来自: {sender_name}\n\n内容：\n{text}\n\n💡 *按住此消息选择『回复(Reply)』即可自由回信*"
    
    # 转发给你
    await context.bot.send_message(chat_id=ADMIN_ID, text=forward_text, parse_mode='Markdown')
    # 自动给对方一个提示
    await update.message.reply_text("消息已收到，我会尽快回复你！")

if __name__ == '__main__':
    Thread(target=run_flask).start()
    
    token = os.environ.get("BOT_TOKEN")
    if token:
        application = ApplicationBuilder().token(token).build()
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.run_polling()
